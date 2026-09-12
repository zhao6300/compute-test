#!/opt/venv/bin/python

import argparse
import json

import torch
import torch.nn as nn


HIDDEN_SIZE = 5120
INTERMEDIATE_SIZE = 2304
N_ROUTED_EXPERTS = 384
NUM_EXPERTS_PER_TOK = 6
SWIGLU_LIMIT = 10.0
WEIGHT_BLOCK_SIZE = (32, 32)


def format_bytes(value: int) -> str:
    return f"{value / (1024 ** 2):.2f} MiB"


def parse_positive_int(value: str) -> int:
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return result


def parse_dtype(value: str) -> torch.dtype:
    return torch.bfloat16 if value == "bf16" else torch.float16


class DeepseekV41FlashExpert(nn.Module):
    def __init__(self, hidden_size: int, intermediate_size: int, limit: float, dtype: torch.dtype, device: torch.device):
        super().__init__()
        self.gate_up_proj = nn.Linear(hidden_size, 2 * intermediate_size, bias=False)
        self.down_proj = nn.Linear(intermediate_size, hidden_size, bias=False)
        self.act_fn = nn.SiLU()
        self.limit = limit
        self.to(device=device, dtype=dtype)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gate_up = self.gate_up_proj(x)
        gate, up = gate_up.chunk(2, dim=-1)
        gate = gate.clamp(max=self.limit)
        up = up.clamp(min=-self.limit, max=self.limit)
        return self.down_proj(self.act_fn(gate) * up)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Simulate one routed expert from the DeepSeek V4.1 Flash config "
            "(hidden 5120, MoE intermediate 2304, 384 experts, top-6, FP4 experts)."
        )
    )
    parser.add_argument("--tokens", default=8, type=parse_positive_int)
    parser.add_argument("--dtype", choices=("bf16", "fp16"), default="bf16", type=parse_dtype)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--json", default=None)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")

    torch.manual_seed(42)
    device = torch.device(args.device)
    torch.cuda.set_device(device)
    dtype = args.dtype

    expert = DeepseekV41FlashExpert(
        hidden_size=HIDDEN_SIZE,
        intermediate_size=INTERMEDIATE_SIZE,
        limit=SWIGLU_LIMIT,
        dtype=dtype,
        device=device,
    )
    with torch.no_grad():
        for parameter in expert.parameters():
            parameter.normal_(mean=0.0, std=0.02)

    x = torch.randn((args.tokens, HIDDEN_SIZE), device=device, dtype=dtype)
    output = expert(x)

    gate_up_macs_per_token = 2 * INTERMEDIATE_SIZE * HIDDEN_SIZE
    down_macs_per_token = INTERMEDIATE_SIZE * HIDDEN_SIZE
    total_macs_per_token = gate_up_macs_per_token + down_macs_per_token
    total_flops_per_token = total_macs_per_token * 2
    gate_up_bf16_bytes = 2 * INTERMEDIATE_SIZE * HIDDEN_SIZE * 2
    down_bf16_bytes = INTERMEDIATE_SIZE * HIDDEN_SIZE * 2
    packed_fp4_weight_bytes = (2 * INTERMEDIATE_SIZE * HIDDEN_SIZE + INTERMEDIATE_SIZE * HIDDEN_SIZE) // 2
    packed_fp4_scale_bytes = (
        2 * INTERMEDIATE_SIZE * HIDDEN_SIZE // 32 + INTERMEDIATE_SIZE * HIDDEN_SIZE // 32
    )

    report = {
        "model": "DeepSeek V4.1 Flash routed expert",
        "hidden_size": HIDDEN_SIZE,
        "moe_intermediate_size": INTERMEDIATE_SIZE,
        "n_routed_experts": N_ROUTED_EXPERTS,
        "num_experts_per_tok": NUM_EXPERTS_PER_TOK,
        "swiglu_limit": SWIGLU_LIMIT,
        "quantization": {
            "expert_dtype": "fp4",
            "weight_block_size": WEIGHT_BLOCK_SIZE,
        },
        "gate_up_shape": tuple(expert.gate_up_proj.weight.shape),
        "down_shape": tuple(expert.down_proj.weight.shape),
        "tokens_to_this_expert": args.tokens,
        "compute_per_token": {
            "gate_up_macs": gate_up_macs_per_token,
            "down_macs": down_macs_per_token,
            "total_macs": total_macs_per_token,
            "total_flops": total_flops_per_token,
            "total_gflops": total_flops_per_token / 1e9,
        },
        "tokens_compute": {
            "gate_up_macs": gate_up_macs_per_token * args.tokens,
            "down_macs": down_macs_per_token * args.tokens,
            "total_macs": total_macs_per_token * args.tokens,
            "total_flops": total_flops_per_token * args.tokens,
            "total_gflops": total_flops_per_token * args.tokens / 1e9,
        },
        "memory": {
            "gate_up_bf16_bytes": gate_up_bf16_bytes,
            "down_bf16_bytes": down_bf16_bytes,
            "packed_fp4_weight_bytes": packed_fp4_weight_bytes,
            "packed_fp4_scale_bytes": packed_fp4_scale_bytes,
            "packed_fp4_total_bytes": packed_fp4_weight_bytes + packed_fp4_scale_bytes,
        },
        "forward_shape": tuple(output.shape),
        "relative_output_mean": float(output.float().abs().mean().item()),
    }

    print("DeepSeek V4.1 Flash expert configuration")
    print(f"  hidden_size: {HIDDEN_SIZE}")
    print(f"  moe_intermediate_size: {INTERMEDIATE_SIZE}")
    print(f"  n_routed_experts: {N_ROUTED_EXPERTS}")
    print(f"  num_experts_per_tok: {NUM_EXPERTS_PER_TOK}")
    print(f"  swiglu_limit: {SWIGLU_LIMIT}")
    print(f"  expert_dtype: fp4")
    print(f"  weight_block_size: {WEIGHT_BLOCK_SIZE}")
    print()
    print("shapes")
    print(f"  gate_up: {tuple(expert.gate_up_proj.weight.shape)}")
    print(f"  down: {tuple(expert.down_proj.weight.shape)}")
    print()
    print("compute volume")
    print(f"  gate_up MACs/token: {gate_up_macs_per_token:,}")
    print(f"  down MACs/token: {down_macs_per_token:,}")
    print(f"  total MACs/token: {total_macs_per_token:,}")
    print(f"  total FLOPs/token: {total_flops_per_token:,} = {total_flops_per_token / 1e9:.4f} GFLOPs")
    print()
    print("memory estimate")
    print(f"  gate_up BF16: {format_bytes(gate_up_bf16_bytes)}")
    print(f"  down BF16: {format_bytes(down_bf16_bytes)}")
    print(f"  packed FP4 weights: {format_bytes(packed_fp4_weight_bytes)}")
    print(f"  packed FP4 scales: {format_bytes(packed_fp4_scale_bytes)}")
    print(f"  packed FP4 total: {format_bytes(packed_fp4_weight_bytes + packed_fp4_scale_bytes)}")
    print()
    print("forward simulation")
    print(f"  tokens: {args.tokens}")
    print(f"  dtype: {args.dtype}")
    print(f"  device: {device}")
    print(f"  output: {tuple(output.shape)}")
    print(f"  relative_output_mean: {output.float().abs().mean().item():.4f}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print(f"\nreport written to {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
