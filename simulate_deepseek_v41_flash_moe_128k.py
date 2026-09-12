#!/opt/venv/bin/python

import argparse
import json

HIDDEN_SIZE = 5120
INTERMEDIATE_SIZE = 2304
N_ROUTED_EXPERTS = 384
NUM_EXPERTS_PER_TOK = 6
SWIGLU_LIMIT = 10.0


def format_est(value: float) -> str:
    return f"{value:.4f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokens", default=131072, type=int)
    parser.add_argument("--tp-size", default=1, type=int)
    parser.add_argument("--ep-size", default=1, type=int)
    parser.add_argument("--json", default=None)
    args = parser.parse_args()

    if args.tp_size <= 0 or args.ep_size <= 0:
        raise ValueError("tp_size and ep_size must be greater than 0")

    total_routes = args.tokens * NUM_EXPERTS_PER_TOK
    routed_tokens_per_expert = total_routes / N_ROUTED_EXPERTS
    gate_up_macs_per_token = 2 * INTERMEDIATE_SIZE * HIDDEN_SIZE
    down_macs_per_token = INTERMEDIATE_SIZE * HIDDEN_SIZE
    total_macs_per_token = gate_up_macs_per_token + down_macs_per_token
    total_flops_per_token = total_macs_per_token * 2
    expert_total_macs = routed_tokens_per_expert * total_macs_per_token
    expert_total_flops = expert_total_macs * 2
    total_macs = total_routes * total_macs_per_token
    total_flops = total_macs * 2
    rank_total_flops = total_flops / (args.tp_size * args.ep_size)

    report = {
        "model": "DeepSeek V4.1 Flash MoE",
        "tokens": args.tokens,
        "n_routed_experts": N_ROUTED_EXPERTS,
        "num_experts_per_tok": NUM_EXPERTS_PER_TOK,
        "hidden_size": HIDDEN_SIZE,
        "moe_intermediate_size": INTERMEDIATE_SIZE,
        "tp_size": args.tp_size,
        "ep_size": args.ep_size,
        "total_routes": total_routes,
        "routed_tokens_per_expert": routed_tokens_per_expert,
        "training_macs_per_token_per_expert": total_macs_per_token,
        "training_flops_per_token_per_expert": total_flops_per_token,
        "expert_total_macs": expert_total_macs,
        "expert_total_flops": expert_total_flops,
        "expert_total_tflops": expert_total_flops / 1e12,
        "layer_total_macs": total_macs,
        "layer_total_flops": total_flops,
        "layer_total_tflops": total_flops / 1e12,
        "rank_total_flops": rank_total_flops,
        "rank_total_tflops": rank_total_flops / 1e12,
    }

    print("DeepSeek V4.1 Flash MoE computation for 128K-token input")
    print(f"tokens: {args.tokens}")
    print(f"n_routed_experts: {N_ROUTED_EXPERTS}")
    print(f"num_experts_per_tok: {NUM_EXPERTS_PER_TOK}")
    print(f"hidden_size: {HIDDEN_SIZE}")
    print(f"moe_intermediate_size: {INTERMEDIATE_SIZE}")
    print()
    print("routing")
    print(f"total_routes: {total_routes:,}")
    print(f"routed_tokens_per_expert: {routed_tokens_per_expert:,.0f}")
    print()
    print("per-expert compute")
    print(f"gate_up MACs/token: {gate_up_macs_per_token:,}")
    print(f"down MACs/token: {down_macs_per_token:,}")
    print(f"total MACs/token: {total_macs_per_token:,}")
    print(f"total FLOPs/token: {total_flops_per_token:,} = {total_flops_per_token / 1e9:.4f} GFLOPs")
    print(f"expert total MACs: {expert_total_macs:,.0f}")
    print(f"expert total FLOPs: {expert_total_flops:,.0f} = {expert_total_flops / 1e9:.4f} GFLOPs")
    print()
    print("whole-MoE layer compute")
    print(f"total MACs: {total_macs:,.0f}")
    print(f"total FLOPs: {total_flops:,.0f} = {total_flops / 1e12:.4f} TFLOPs")

    if args.tp_size > 1 or args.ep_size > 1:
        print()
        print("TP/EP scaling")
        print(f"tp_size: {args.tp_size}")
        print(f"ep_size: {args.ep_size}")
        print(f"rank_total_flops: {rank_total_flops:,.0f} = {rank_total_flops / 1e12:.4f} TFLOPs")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
