#!/opt/venv/bin/python

import argparse
import json
import math
import statistics
import time
from dataclasses import dataclass

import deep_gemm
import torch
import vllm._custom_ops as vllm_ops
from vllm.model_executor.layers.quantization.utils.marlin_utils import (
    marlin_make_workspace_new,
    marlin_pad_dim,
    marlin_repacked_nk,
    marlin_unpad_output,
    should_use_atomic_add_reduce,
)
from vllm.model_executor.layers.quantization.utils.marlin_utils_fp4 import (
    prepare_fp4_layer_for_marlin,
)
from vllm.scalar_type import scalar_types


@dataclass
class TimingResult:
    mode: str
    m: int
    n: int
    k: int
    operator: str
    input_dtype: str
    mean_ms: float
    median_ms: float
    std_ms: float
    min_ms: float
    max_ms: float
    p95_ms: float
    mean_rel_error: float | None = None
    max_abs_error: float | None = None


class MarlinLayerStub:
    pass


def parse_shape(value: str) -> tuple[int, int, int]:
    parts = [int(part) for part in value.split(",")]
    if len(parts) != 3 or any(part <= 0 for part in parts):
        raise argparse.ArgumentTypeError("shape must be three positive integers: M,N,K")
    return (parts[0], parts[1], parts[2])


def positive_int(value: str) -> int:
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return result


def quantize_weights(weight: torch.Tensor):
    packed, raw_scale = deep_gemm.per_token_cast_to_fp4(
        weight, use_ue8m0=True, gran_k=32
    )
    e8m0_scale = raw_scale.to(torch.float8_e8m0fnu).contiguous()
    deep_scale = deep_gemm.transform_sf_into_required_layout(
        raw_scale.float(),
        weight.size(0),
        weight.size(1),
        recipe=(1, 32),
    )
    return packed.contiguous(), e8m0_scale, deep_scale, raw_scale


def prepare_marlin(
    packed_weight: torch.Tensor,
    e8m0_scale: torch.Tensor,
    size_n: int,
    size_k: int,
    device: torch.device,
    dtype: torch.dtype,
) -> MarlinLayerStub:
    layer = MarlinLayerStub()
    layer.output_size_per_partition = size_n
    layer.input_size_per_partition = size_k
    layer.params_dtype = dtype
    layer.weight = packed_weight
    layer.weight_scale = e8m0_scale
    layer.bias = None
    layer.workspace = marlin_make_workspace_new(device)
    prepare_fp4_layer_for_marlin(layer, None)
    return layer


def prepare_deep_values(
    weight: torch.Tensor,
    packed_weight: torch.Tensor,
):
    deep_scale = deep_gemm.transform_sf_into_required_layout(
        raw_scale.float(), size_n, size_k, recipe=(1, 32)
    )
    return deep_gemm, deep_scale


def prepare_deep_input(x: torch.Tensor):
    quantized, raw_scale = deep_gemm.per_token_cast_to_fp8(
        x, use_ue8m0=True, gran_k=32, use_packed_ue8m0=False
    )
    scale = deep_gemm.transform_sf_into_required_layout(
        raw_scale, x.size(0), x.size(1), recipe=(1, 32)
    )
    return quantized, scale


def dequantize_weight(packed_weight: torch.Tensor, raw_scale: torch.Tensor):
    return deep_gemm.cast_back_from_fp4(packed_weight, raw_scale, gran_k=32)


def relative_error(output: torch.Tensor, reference: torch.Tensor):
    output32 = output.float()
    reference32 = reference.float()
    denominator = torch.maximum(reference32.abs(), torch.full_like(reference32, 1e-2))
    return float(((output32 - reference32).abs() / denominator).mean().item()), \
        float((output32 - reference32).abs().max().item())


def elapsed_ms(function, warmup: int, iterations: int) -> list[float]:
    for _ in range(warmup):
        function()
    torch.cuda.synchronize()
    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)
    start_event.record()
    for _ in range(iterations):
        function()
    end_event.record()
    torch.cuda.synchronize()
    elapsed = start_event.elapsed_time(end_event) / iterations
    return [elapsed]


def summarize(values: list[float]):
    std = statistics.stdev(values) if len(values) > 1 else 0.0
    return statistics.mean(values), statistics.median(values), std, min(values), max(values)


def percentile(values: list[float], target: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * target
    lower = math.floor(index)
    upper = math.ceil(index)
    fraction = index - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def benchmark_mode(
    mode: str,
    m: int,
    n: int,
    k: int,
    dtype: torch.dtype,
    packed_weight: torch.Tensor,
    deep_scale: torch.Tensor,
    marlin_layer: MarlinLayerStub,
    warmup: int,
    iterations: int,
    repetitions: int,
    calculate_accuracy: bool,
    raw_scale: torch.Tensor,
):
    device = packed_weight.device
    x = torch.randn((m, k), device=device, dtype=dtype) * 0.35
    deep_quantized, deep_input_scale = prepare_deep_input(x)
    deep_output = torch.empty((m, n), device=device, dtype=dtype)
    marlin_output = torch.empty((m, n), device=device, dtype=dtype)
    padded_n, padded_k = marlin_repacked_nk(marlin_layer.weight, num_bits=4)
    marlin_input = marlin_pad_dim(x, k, padded_k)
    use_atomic_add = should_use_atomic_add_reduce(
        m=m, n=padded_n, k=padded_k, device=device, dtype=dtype
    )

    def run_deep():
        deep_gemm.fp8_fp4_gemm_nt(
            (deep_quantized, deep_input_scale),
            (packed_weight, deep_scale),
            deep_output,
            recipe=(1, 1, 32),
        )
        return deep_output

    def run_marlin():
        result = vllm_ops.marlin_gemm(
            a=marlin_input,
            c=marlin_output,
            b_q_weight=marlin_layer.weight,
            b_bias=None,
            b_scales=marlin_layer.weight_scale,
            a_scales=None,
            global_scale=None,
            b_zeros=None,
            workspace=marlin_layer.workspace,
            b_q_type=scalar_types.float4_e2m1f,
            size_m=m,
            size_n=padded_n,
            size_k=padded_k,
            use_atomic_add=use_atomic_add,
            use_fp32_reduce=True,
        )
        return marlin_unpad_output(result, n, padded_n) if padded_n != n else result

    deep_times: list[float] = []
    marlin_times: list[float] = []
    for _ in range(repetitions):
        deep_times.extend(elapsed_ms(run_deep, warmup, iterations))
        marlin_times.extend(elapsed_ms(run_marlin, warmup, iterations))

    accuracy = [None, None]
    if calculate_accuracy:
        reference = torch.matmul(x, dequantize_weight(packed_weight, raw_scale).to(dtype).t())
        accuracy = [
            relative_error(run_deep(), reference),
            relative_error(run_marlin(), reference),
        ]

    specs = [
        ("deepgemm_mxfp4", "fp8", deep_times, accuracy[0]),
        ("marlin_mxfp4", "bf16", marlin_times, accuracy[1]),
    ]
    results = []
    summary = {}
    for operator, input_dtype, times, errors in specs:
        mean_rel_error = None if errors is None else errors[0]
        max_abs_error = None if errors is None else errors[1]
        mean_ms, median_ms, std_ms, min_ms, max_ms = summarize(times)
        results.append(TimingResult(
            mode=mode,
            m=m,
            n=n,
            k=k,
            operator=operator,
            input_dtype=input_dtype,
            mean_ms=mean_ms,
            median_ms=median_ms,
            std_ms=std_ms,
            min_ms=min_ms,
            max_ms=max_ms,
            p95_ms=percentile(times, 0.95),
            mean_rel_error=mean_rel_error,
            max_abs_error=max_abs_error,
        ))
        summary[operator] = {"mean_ms": mean_ms, "p95_ms": percentile(times, 0.95)}
    return results, summary


def print_table(results: list[TimingResult], comparison: dict | None) -> None:
    print("\nBENCHMARK RESULTS")
    header = (
        f"{'mode':<7} {'m':>5} {'n':>6} {'k':>6} {'operator':<18} "
        f"{'mean_ms':>10} {'median_ms':>10} {'std_ms':>9} {'p95_ms':>10} "
        f"{'min_ms':>10} {'max_ms':>10} {'rel_err_%':>10}"
    )
    print(header)
    print("-" * len(header))
    for result in results:
        print(
            f"{result.mode:<7} {result.m:>5} {result.n:>6} {result.k:>6} "
            f"{result.operator:<18} {result.mean_ms:>10.4f} {result.median_ms:>10.4f} "
            f"{result.std_ms:>9.4f} {result.p95_ms:>10.4f} {result.min_ms:>10.4f} "
            f"{result.max_ms:>10.4f} "
            f"{('-' if result.mean_rel_error is None else f'{result.mean_rel_error * 100:.3f}'):>10}"
        )

    if comparison:
        print("\nDEEPGEMM_SPEEDUP (mean_ms_deepgemm / mean_ms_marlin; >1 when DeepGEMM runs faster)")
        for key, speedup in comparison.items():
            print(f"{key:<28} {speedup:>10.2f}")


def write_json(path: str, results: list[TimingResult], comparison: dict | None, gpu_name: str) -> None:
    rows = []
    for result in results:
        row = vars(result).copy()
        key = f"{result.mode},m{result.m},n{result.n},k{result.k}"
        if comparison and key in comparison:
            row["deepgemm_speedup_mean"] = comparison[key]
        rows.append(row)
    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "gpu": gpu_name,
        "results": rows,
    }
    with open(path, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark vLLM Marlin W4A16 MXFP4 against DeepGEMM FP8-activation MXFP4."
    )
    parser.add_argument("--shapes", nargs="+", default=[(4096, 4096, 4096)], type=parse_shape)
    parser.add_argument("--ms", nargs="+", type=positive_int, default=[1, 8, 32, 128, 512])
    parser.add_argument("--warmup", type=positive_int, default=5)
    parser.add_argument("--iterations", type=positive_int, default=10)
    parser.add_argument("--repetitions", type=positive_int, default=3)
    parser.add_argument("--mode", choices=("kernel", "linear", "both"), default="kernel")
    parser.add_argument("--accuracy", action="store_true")
    parser.add_argument("--dtype", choices=("bf16", "fp16"), default="bf16")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--json", default=None)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")

    device = torch.device(args.device)
    torch.cuda.set_device(device)
    dtype = torch.bfloat16 if args.dtype == "bf16" else torch.float16
    modes = ("kernel", "linear") if args.mode == "both" else (args.mode,)

    gpu_name = torch.cuda.get_device_name(device)
    print(f"gpu={gpu_name}")
    print(f"cuda={torch.version.cuda}, torch={torch.__version__}")
    print(f"deep_gemm={deep_gemm.__name__}, dtype={args.dtype}")
    print(f"warmup={args.warmup}, iterations={args.iterations}, repeats={args.repetitions}")
    print("comparison-position: Marlin is W4A16 (BF16/FP16 activation); DeepGEMM is W4A8 (FP8 activation).")

    torch.manual_seed(42)
    all_results: list[TimingResult] = []
    summary: dict[str, dict] = {}
    for size_n, size_k, quality in args.shapes:
        weight = torch.randn((size_n, size_k), device=device, dtype=dtype) * 0.15
        packed_weight, e8m0_scale, deep_scale, raw_scale = quantize_weights(weight)
        marlin_layer = prepare_marlin(
            packed_weight, e8m0_scale, size_n, size_k, device, dtype
        )

        print(
            f"\npreparing N={size_n}, K={size_k}: "
            f"DeepGEMM packed={tuple(packed_weight.shape)}, "
            f"Marlin packed={tuple(marlin_layer.weight.shape)}"
        )
        for mode in modes:
            for m in args.ms:
                results, timing = benchmark_mode(
                    mode,
                    m,
                    size_n,
                    size_k,
                    dtype,
                    packed_weight,
                    deep_scale,
                    marlin_layer,
                    args.warmup,
                    args.iterations,
                    args.repetitions,
                    args.accuracy,
                    raw_scale,
                )
                all_results.extend(results)
                summary[f"{mode},m{m},n{size_n},k{size_k}"] = timing
                deepgemm_mean = timing["deepgemm_mxfp4"]["mean_ms"]
                marlin_mean = timing["marlin_mxfp4"]["mean_ms"]
                print(
                    f"mode={mode} m={m:<4} deepgemm={deepgemm_mean:.4f} ms, "
                    f"marlin={marlin_mean:.4f} ms, speedup={deepgemm_mean / marlin_mean:.2f}x"
                )
            if args.accuracy:
                print(
                    f'[accuracy {mode} m={args.ms[0]}] '
                    'relative errors are printed in the exported JSON/table.'
                )

        del weight, raw_scale, deep_scale, marlin_layer
        torch.cuda.empty_cache()

    comparison = {
        key: value["deepgemm_mxfp4"]["mean_ms"] / value["marlin_mxfp4"]["mean_ms"]
        for key, value in summary.items()
    }
    print_table(all_results, comparison)
    if args.json:
        write_json(args.json, all_results, comparison, gpu_name)
        print(f"\nresults written to {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
