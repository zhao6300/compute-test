#!/opt/venv/bin/python

import argparse


def positive_int(value: str) -> int:
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return result


def format_bytes(count: int) -> str:
    value = float(count)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024.0 or unit == "TiB":
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{value:.2f} TiB"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Explain and simulate the compute volume of one MoE expert as two GEMMs."
        )
    )
    parser.add_argument("--hidden-size", type=positive_int, default=4096)
    parser.add_argument("--intermediate-size", type=positive_int, default=11008)
    parser.add_argument("--tokens", type=positive_int, default=1024)
    parser.add_argument("--simulate", action="store_true")
    args = parser.parse_args()

    hidden_size = args.hidden_size
    intermediate_size = args.intermediate_size
    tokens = args.tokens

    print("MoE expert operator decomposition")
    print("- gate_up: [tokens, hidden] @ [hidden, 2*intermediate]")
    print("- down:    [tokens, intermediate] @ [intermediate, hidden]")
    print()
    print(
        f"tokens={tokens} hidden_size={hidden_size} "
        f"intermediate_size={intermediate_size}"
    )
    print()
    print("shape sequence:")
    print(f"  x           {tokens} x {hidden_size}")
    print(f"  gate_up_w   {hidden_size} x {2 * intermediate_size}")
    print(f"  gate_up_out {tokens} x {2 * intermediate_size}")
    print(f"  silu-and-mul {tokens} x {intermediate_size}")
    print(f"  down_w      {intermediate_size} x {hidden_size}")
    print(f"  output      {tokens} x {hidden_size}")
    print()
    gate_up_macs = tokens * 2 * intermediate_size * hidden_size
    down_macs = tokens * intermediate_size * hidden_size
    total_macs = gate_up_macs + down_macs
    total_flops = total_macs * 2
    total_bytes = {
        "gate_up_bf16": 2 * hidden_size * 2 * intermediate_size,
        "down_bf16": 2 * intermediate_size * hidden_size,
    }
    quantized_weight_bytes = (hidden_size * 2 * intermediate_size + intermediate_size * hidden_size) // 2
    quantized_scale_bytes = hidden_size * 2 * intermediate_size / 32 + intermediate_size * hidden_size / 32

    print("counting convention: 1 multiply-add = 2 FLOPs")
    print(f"gate_up MACs : {gate_up_macs:,}")
    print(f"down MACs    : {down_macs:,}")
    print(f"total MACs   : {total_macs:,}")
    print(f"total FLOPs  : {total_flops:,} = {total_flops / 1e9:.2f} GFLOPs")
    print(f"total GMACs  : {total_macs / 1e9:.2f}")
    print()
    print("unquantized bf16 expert weight bytes:")
    for name, value in total_bytes.items():
        print(f"  {name:<14} {value:,} bytes = {format_bytes(value)}")
    print(
        f"  packed MXFP4  {int(quantized_weight_bytes):,} weight bytes "
        f"+ ~{int(quantized_scale_bytes):,} E8M0 scale bytes "
        f"= {format_bytes(quantized_weight_bytes + quantized_scale_bytes)}"
    )

    if args.simulate:
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is unavailable")

        device = torch.device("cuda:0")
        x = torch.randn((tokens, hidden_size), device=device, dtype=torch.bfloat16)
        gate_up_weight = torch.randn(
            (2 * intermediate_size, hidden_size), device=device, dtype=torch.bfloat16
        ) * 0.05
        down_weight = torch.randn(
            (hidden_size, intermediate_size), device=device, dtype=torch.bfloat16
        ) * 0.05

        gate_up_output = torch.nn.functional.linear(x, gate_up_weight)
        gate = torch.nn.functional.silu(gate_up_output[:, :intermediate_size])
        up = gate_up_output[:, intermediate_size:]
        intermediate = gate * up
        output = torch.nn.functional.linear(intermediate, down_weight)

        simulate_macs = gate_up_macs + down_macs
        if simulate_macs != total_macs:
            raise RuntimeError("simulate and analytic estimates disagree")
        if tuple(intermediate.shape) != (tokens, intermediate_size):
            raise RuntimeError("unexpected output shape")

        print()
        print("simulation:")
        print(f"  x={tuple(x.shape)}")
        print(f"  gate_up={tuple(gate_up_output.shape)}")
        print(f"  intermediate={tuple(intermediate.shape)}")
        print(f"  output={tuple(output.shape)}")
        print(f"  macs={total_macs:,}")
        print(f"  flops={total_flops:,}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
