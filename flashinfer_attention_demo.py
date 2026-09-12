import argparse
import statistics
import time

import torch
import torch.nn.functional as F
from flashinfer import single_prefill_with_kv_cache


def torch_attention(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    sm_scale: float,
    causal: bool,
) -> torch.Tensor:
    # [seq, heads, dim] -> [batch, heads, seq, dim]
    q = q.transpose(0, 1).unsqueeze(0)
    repeat = q.shape[1] // k.shape[1]
    k = k.repeat_interleave(repeat, dim=1)
    v = v.repeat_interleave(repeat, dim=1)
    k = k.transpose(0, 1).unsqueeze(0)
    v = v.transpose(0, 1).unsqueeze(0)
    return F.scaled_dot_product_attention(
        q,
        k,
        v,
        attn_mask=None,
        is_causal=causal,
        scale=sm_scale,
    ).squeeze(0).transpose(0, 1)


def run_case(
    q_seq: int,
    qo_heads: int,
    kv_heads: int,
    head_dim: int,
    iters: int,
) -> None:
    device = torch.device("cuda")
    dtype = torch.float16
    sm_scale = head_dim**-0.5

    torch.manual_seed(42)
    q = torch.randn(q_seq, qo_heads, head_dim, device=device, dtype=dtype)
    k = torch.randn(q_seq, kv_heads, head_dim, device=device, dtype=dtype)
    v = torch.randn(q_seq, kv_heads, head_dim, device=device, dtype=dtype)

    out = single_prefill_with_kv_cache(
        q,
        k,
        v,
        causal=True,
        kv_layout="NHD",
        pos_encoding_mode="NONE",
        sm_scale=sm_scale,
    )
    expected = torch_attention(q, k, v, sm_scale, causal=True)
    max_abs_err = (out.float() - expected.float()).abs().max().item()

    times = []
    for _ in range(iters):
        torch.cuda.synchronize(device)
        start = time.perf_counter()
        single_prefill_with_kv_cache(
            q,
            k,
            v,
            causal=True,
            kv_layout="NHD",
            pos_encoding_mode="NONE",
            sm_scale=sm_scale,
        )
        torch.cuda.synchronize(device)
        times.append((time.perf_counter() - start) * 1000.0)

    print(f"shape: q={tuple(q.shape)}, k/v={tuple(k.shape)}")
    print(f"flashinfer median: {statistics.median(times):.3f} ms")
    print(f"torch sdpa max_abs_err: {max_abs_err:.6f}")
    print(f"output: {tuple(out.shape)}, dtype={out.dtype}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--q-seq", type=int, default=128)
    parser.add_argument("--qo-heads", type=int, default=8)
    parser.add_argument("--kv-heads", type=int, default=2)
    parser.add_argument("--head-dim", type=int, default=128)
    parser.add_argument("--iters", type=int, default=8)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA device is required")
    if args.qo_heads % args.kv_heads != 0:
        raise ValueError("qo_heads must be divisible by kv_heads")

    run_case(
        args.q_seq,
        args.qo_heads,
        args.kv_heads,
        args.head_dim,
        args.iters,
    )


if __name__ == "__main__":
    main()
