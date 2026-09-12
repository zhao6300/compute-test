#!/opt/venv/bin/python

import argparse
import json
import os
import signal
import socket
import torch.distributed as dist
import torch


HIDDEN_SIZE = 5120
INTERMEDIATE_SIZE = 2304


def parse_size(value: str) -> int:
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return result


def parse_seconds(value: str) -> float:
    result = float(value)
    if result <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return result


def parse_dtype(value: str) -> torch.dtype:
    return {
        "bf16": torch.bfloat16,
        "fp16": torch.float16,
        "fp32": torch.float32,
    }[value]


def set_local_nccl_defaults() -> None:
    os.environ.setdefault("NCCL_SOCKET_IFNAME", "lo")
    os.environ.setdefault("NCCL_P2P_DISABLE", "1")
    os.environ.setdefault("NCCL_IB_DISABLE", "1")
    os.environ.setdefault("NCCL_DEBUG", "WARN")
    os.environ.setdefault("NCCL_ALGO", "Ring")
    os.environ.setdefault("NCCL_PROTO", "Simple")
    os.environ.setdefault("TORCH_NCCL_ASYNC_ERROR_HANDLING", "1")
    os.environ.setdefault("TORCH_NCCL_BLOCKING_WAIT", "1")


def maybe_assert_invariance(
    args: argparse.Namespace,
    tensor: torch.Tensor,
    group: dist.ProcessGroup,
) -> None:
    if not args.assert_allreduce:
        return
    group_ranks = dist.get_process_group_ranks(group)
    gathered = [torch.empty_like(tensor) for _ in group_ranks]
    dist.all_gather(gathered, tensor.contiguous(), group=group)
    if dist.get_rank() == 0:
        for item in gathered[1:]:
            if not torch.equal(gathered[0].float(), item.float()):
                raise RuntimeError("allreduce invariance test failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("all2all", "allreduce", "both", "tp_ep"),
        default="both",
    )
    parser.add_argument("--ep-size", default=1, type=parse_size)
    parser.add_argument("--tp-size", default=1, type=parse_size)
    parser.add_argument("--tokens", default=32768, type=parse_size)
    parser.add_argument("--product", default=8192, type=parse_size)
    parser.add_argument("--dtype", choices=("bf16", "fp16", "fp32"), default="bf16")
    parser.add_argument("--hidden-size", default=HIDDEN_SIZE, type=parse_size)
    parser.add_argument("--intermediate-size", default=INTERMEDIATE_SIZE, type=parse_size)
    parser.add_argument("--topk", default=6, type=parse_size)
    parser.add_argument("--warmup", default=5, type=parse_size)
    parser.add_argument("--iterations", default=20, type=parse_size)
    parser.add_argument("--in-flight", default=1, type=parse_size)
    parser.add_argument("--timeout", default=90.0, type=parse_seconds)
    parser.add_argument("--assert-allreduce", action="store_true")
    parser.add_argument("--json", default=None)
    args = parser.parse_args()

    set_local_nccl_defaults()
    socket.setdefaulttimeout(args.timeout)

    def report_timeout(signum: int, frame: object) -> None:
        raise TimeoutError(f"NCCL operation exceeded {args.timeout:g}s")

    signal.signal(signal.SIGALRM, report_timeout)

    local_rank = int(os.environ.get("LOCAL_RANK", "0"))
    device = torch.device(f"cuda:{local_rank}")
    torch.cuda.set_device(device)
    dist.init_process_group(backend="nccl", init_method="env://")
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    dist.barrier(device_ids=[local_rank])
    dtype = parse_dtype(args.dtype)

    if args.mode == "tp_ep":
        ep_size = args.ep_size
        tp_size = args.tp_size
        if world_size != ep_size * tp_size:
            raise ValueError(
                f"world_size={world_size} must equal ep_size={ep_size} * tp_size={tp_size}"
            )
        ep_rank = rank % ep_size
        tp_rank = rank // ep_size
        tp_group_ranks = [tp_rank * ep_size + ep_index for ep_index in range(ep_size)]
        tp_group = dist.new_group(ranks=tp_group_ranks, backend="nccl")
    else:
        ep_size = world_size
        tp_size = world_size
        tp_group = None

    tokens_per_rank = args.tokens // ep_size
    product = args.product // tp_size
    chunk_shape = (tokens_per_rank, product)
    send_buffers = [
        torch.randn(chunk_shape, device=device, dtype=torch.float32).to(dtype)
        for _ in range(args.in_flight)
    ]
    recv_buffers = [
        torch.empty_like(send_buffers[0]) for _ in range(args.in_flight)
    ]

    if args.mode in ("all2all", "both", "tp_ep"):
        input_list = list(send_buffers)
        output_list = list(recv_buffers)
        local_input = input_list[0].contiguous()
        gathered_outputs = [torch.empty_like(local_input) for _ in range(world_size)]
        for _ in range(args.warmup):
            dist.all_gather(gathered_outputs, local_input)
            torch.cuda.synchronize(device)
        dist.barrier(device_ids=[local_rank])
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        for _ in range(args.iterations):
            dist.all_gather(gathered_outputs, local_input)
            torch.cuda.synchronize(device)
        end.record()
        torch.cuda.synchronize(device)
        elapsed_ms = start.elapsed_time(end) / args.iterations
        print(f"rank={rank} all2all_ms={elapsed_ms:.3f}")

    if args.mode in ("allreduce", "both", "tp_ep"):
        allreduce_tensor = torch.randn(chunk_shape, device=device, dtype=torch.float32).to(dtype)
        for _ in range(args.warmup):
            dist.all_reduce(allreduce_tensor)
            torch.cuda.synchronize(device)
        dist.barrier(device_ids=[local_rank])
        torch.cuda.synchronize(device)
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        for _ in range(args.iterations):
            dist.all_reduce(allreduce_tensor)
            torch.cuda.synchronize(device)
            maybe_assert_invariance(
                args,
                allreduce_tensor,
                tp_group if tp_group is not None else dist.group.WORLD,
            )
        end.record()
        torch.cuda.synchronize(device)
        elapsed_ms = start.elapsed_time(end) / args.iterations
        print(f"rank={rank} allreduce_ms={elapsed_ms:.3f}")

    report = {
        "device": device.type,
        "world_size": world_size,
        "rank": rank,
        "mode": args.mode,
        "tokens_per_rank": tokens_per_rank,
        "bytes_per_rank": tokens_per_rank * product * torch.ones(
            1,
            dtype=dtype,
            device=device,
        ).element_size(),
        "dtype": args.dtype,
        "config": {
            "hidden_size": args.hidden_size,
            "intermediate_size": args.intermediate_size,
            "topk": args.topk,
            "product": product,
            "mode": args.mode,
            "warmup": args.warmup,
            "iterations": args.iterations,
            "in_flight": args.in_flight,
            "assert_allreduce": bool(args.assert_allreduce),
            "ep_size": ep_size,
            "tp_size": tp_size,
            "ep_rank": rank % ep_size,
            "tp_rank": rank // ep_size,
        },
    }

    if args.json and rank == 0:
        with open(args.json, "w", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")

    dist.destroy_process_group()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
