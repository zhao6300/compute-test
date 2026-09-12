#!/opt/venv/bin/python

import argparse

import torch
from transformers.models.deepseek_v4.configuration_deepseek_v4 import DeepseekV4Config
from transformers.models.deepseek_v4.modeling_deepseek_v4 import DeepseekV4Experts


def format_bytes(value: int) -> str:
    return f"{value / (1024 ** 2):.2f} MiB"


def parse_positive_int(value: str) -> int:
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return result


def format_relative(value: float) -> str:
    return f"{value:.2f}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Simulate the forward pass and compute volume of a DeepSeek V4 Flash expert."
        )
    )
    parser.add_argument("--tokens", default=8, type=parse_positive_int)
    parser.add_argument("--dtype", choices=("bf16", "fp16"), default="bf16")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--json", default=None)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")

    torch.manual_seed(42)
    device = torch.device(args.device)
    torch.cuda.set_device(device)
    dtype = torch.bfloat16 if args.dtype == "bf16" else torch.float16

    config = DeepseekV4Config()
    intermediate_size = config.intermediate_size
    hidden_size = config.hidden_size

    expert_config = DeepseekV4Config()
    expert_config.num_local_experts = 1
    expert = DeepseekV4Experts(expert_config).to(device=device, dtype=dtype)
    for parameter in expert.parameters():
        torch.nn.init.normal_(parameter, mean=0.0, std=0.02)

    hidden_states = torch.randn((args.tokens, hidden_size), device=device, dtype=dtype)
    top_k_index = torch.full((args.tokens, 1), 0, device=device, dtype=torch.long)
    top_k_weights = torch.ones((args.tokens, 1), device=device, dtype=dtype)

    gate_up, down = next(iter(expert.named_parameters()))
    del gate_up, down
    gate_up_shape = tuple(expert.gate_up_proj.shape)
    down_shape = tuple(expert.down_proj.shape)
    output = expert(hidden_states, top_k_index, top_k_weights)

    gate_up_macs = args.tokens * 2 * intermediate_size * hidden_size
    down_macs = args.tokens * intermediate_size * hidden_size
    total_macs = gate_up_macs + down_macs
    total_flops = total_macs * 2
    gate_up_bf16_bytes = hidden_size * 2 * intermediate_size * 2
    down_bf16_bytes = intermediate_size * hidden_size * 2
    packed_weight_bytes = (hidden_size * 2 * intermediate_size + intermediate_size * hidden_size) // 2
    packed_scale_bytes = int(hidden_size * 2 * intermediate_size / 32 + intermediate_size * hidden_size / 32)

    report = {
        "model": "DeepSeek V4 Flash expert",
        "hidden_size": hidden_size,
        "intermediate_size": intermediate_size,
        "tokens_to_this_expert": args.tokens,
        "dtype": args.dtype,
        "device": device.type,
        "gate_up_shape": gate_up_shape,
        "down_shape": down_shape,
        "gate_up_macs": gate_up_macs,
        "down_macs": down_macs,
        "total_macs": total_macs,
        "total_flops": total_flops,
        "total_gfmacs": total_macs / 1e9,
        "total_gflops": total_flops / 1e9,
        "gate_up_bf16_bytes": gate_up_bf16_bytes,
        "down_bf16_bytes": down_bf16_bytes,
        "packed_mxfp4_weight_bytes": packed_weight_bytes,
        "packed_mxfp4_scale_bytes": packed_scale_bytes,
        "packed_mxfp4_total_bytes": packed_weight_bytes + packed_scale_bytes,
        "expert_forward_shape": tuple(output.shape),
        "swiglu_limit": config.swiglu_limit,
        "relative_output_mean": float(output.float().abs().mean().item()),
    }

    print("DeepSeek V4 Flash single-expert simulation")
    print(f"  hidden_size={hidden_size}, intermediate_size={intermediate_size}")
    print(f"  gate_up={gate_up_shape}, down={down_shape}")
    print(f"  tokens={args.tokens}, dtype={args.dtype}, device={device}")
    print(f"  forward_output={tuple(output.shape)}")
    print()
    print("compute volume")
    print(f"  gate_up MACs: {gate_up_macs:,}")
    print(f"  down MACs: {down_macs:,}")
    print(f"  total MACs: {total_macs:,}")
    print(f"  total FLOPs: {total_flops:,} = {total_flops / 1e9:.2f} GFLOPs")
    print()
    print("memory estimate")
    print(f"  gate_up bf16: {format_bytes(gate_up_bf16_bytes)}")
    print(f"  down bf16: {format_bytes(down_bf16_bytes)}")
    print(f"  packed MXFP4: {format_bytes(packed_weight_bytes + packed_scale_bytes)}")
    print(f"  relative_output_mean: {format_relative(report['relative_output_mean'])}")

    if args.json:
        import json

        with open(args.json, "w", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print(f"\nreport written to {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
