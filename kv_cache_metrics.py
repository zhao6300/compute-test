#!/usr/bin/env python3
"""Read KV cache and prefix cache metrics from a vLLM /metrics endpoint."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request


METRIC_ALIASES = {
    "kv_cache_usage": {"vllm:kv_cache_usage_perc", "vllm:kv_cache_usage_ratio"},
    "prefix_queries": {
        "vllm:prefix_cache_queries",
        "vllm:prefix_cache_queries_total",
    },
    "prefix_hits": {"vllm:prefix_cache_hits", "vllm:prefix_cache_hits_total"},
    "external_queries": {
        "vllm:external_prefix_cache_queries",
        "vllm:external_prefix_cache_queries_total",
    },
    "external_hits": {
        "vllm:external_prefix_cache_hits",
        "vllm:external_prefix_cache_hits_total",
    },
}

SAMPLE_RE = re.compile(r"^(?P<name>[A-Za-z_:][A-Za-z0-9_:]*)(?P<labels>\{.*\})?\s+(?P<value>\S+)")


def parse_metrics(text: str) -> dict[str, dict[str, float]]:
    """Parse the small subset of metrics used by this script."""

    values: dict[str, dict[str, float]] = {key: {} for key in METRIC_ALIASES}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = SAMPLE_RE.match(line)
        if not match:
            continue
        metric_name = match.group("name")
        family = next(
            (key for key, aliases in METRIC_ALIASES.items() if metric_name in aliases),
            None,
        )
        if family is None:
            continue
        try:
            value = float(match.group("value"))
        except ValueError:
            continue
        labels = match.group("labels") or ""
        key = json.dumps(_normalized_labels(labels), sort_keys=True, separators=(",", ":"))
        # Keep the last sample when duplicate label keys are accidentally present.
        values[family][key] = value
    return values


def _normalized_labels(labels_text: str) -> dict[str, str]:
    """Return Prometheus-style labels as a plain dictionary."""

    result: dict[str, str] = {}
    if labels_text.startswith("{") and labels_text.endswith("}"):
        labels_text = labels_text[1:-1]
    for match in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"((?:\\.|[^"])*)"', labels_text):
        name, value = match.groups()
        result[name] = value.replace('\\"', '"').replace("\\\\", "\\")
    return result


def take_snapshot(url: str, timeout: float) -> tuple[float, dict[str, dict[str, float]]]:
    request = urllib.request.Request(url, headers={"Accept": "text/plain; version=0.0.4"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        body = response.read().decode("utf-8")
    return time.monotonic(), parse_metrics(body)


def sum_values(samples: dict[str, float]) -> float:
    return sum(samples.values())


def ratio_percent(numerator: float, denominator: float) -> float | None:
    return numerator / denominator * 100.0 if denominator else None


def format_percent(value: float | None) -> str:
    return f"{value:.2f}%" if value is not None else "N/A(0 queries)"


def build_comparison(
    previous: tuple[float, dict[str, dict[str, float]]],
    current: tuple[float, dict[str, dict[str, float]]],
) -> dict[str, object]:
    previous_time, previous_values = previous
    current_time, current_values = current
    elapsed = max(current_time - previous_time, 0.0)
    rows = []
    for family in ("prefix", "external"):
        queries_key = f"{family}_queries"
        hits_key = f"{family}_hits"
        all_label_keys = set(previous_values[queries_key]) | set(current_values[queries_key])
        all_label_keys.update(previous_values[hits_key])
        all_label_keys.update(current_values[hits_key])

        delta_queries = 0.0
        delta_hits = 0.0
        for label_key in sorted(all_label_keys):
            delta_queries += max(
                current_values[queries_key].get(label_key, 0.0)
                - previous_values[queries_key].get(label_key, 0.0),
                0.0,
            )
            delta_hits += max(
                current_values[hits_key].get(label_key, 0.0)
                - previous_values[hits_key].get(label_key, 0.0),
                0.0,
            )
        previous_rate = ratio_percent(
            sum_values(previous_values[hits_key]),
            sum_values(previous_values[queries_key]),
        )
        current_rate = ratio_percent(delta_hits, delta_queries)
        if current_rate is None:
            current_rate = previous_rate
        rows.append(
            {
                "name": "prefix_cache" if family == "prefix" else "external_prefix_cache",
                "delta_queries": delta_queries,
                "delta_hits": delta_hits,
                "hit_rate_percent": current_rate,
                "rate_fallback": delta_queries == 0 and previous_rate is not None,
            }
        )

    usage_values = current_values["kv_cache_usage"]
    usage_percent: float | None = None
    if usage_values:
        # In normal vLLM exposition there is one value per engine. Averaging is
        # only a safety fallback for custom label duplication.
        usage_percent = sum_values(usage_values) / len(usage_values) * 100.0
    return {"elapsed_seconds": elapsed, "usage_percent": usage_percent, "rows": rows}


def print_snapshot(
    snapshot: tuple[float, dict[str, dict[str, float]]],
    label: str,
) -> None:
    _, values = snapshot
    usage = (
        ratio_percent(sum_values(values["kv_cache_usage"]), len(values["kv_cache_usage"]))
        if values["kv_cache_usage"]
        else None
    )
    print(f"[{label}] KV cache usage: {format_percent(usage)}")
    for family in ("prefix_queries", "external_queries"):
        hits_family = family.replace("queries", "hits")
        hit_rate = ratio_percent(sum_values(values[hits_family]), sum_values(values[family]))
        name = family.replace("queries", "cache")
        print(
            f"[{label}] {name} hit rate: {format_percent(hit_rate)}"
            f" (hits={sum_values(values[hits_family]):.0f},"
            f" queries={sum_values(values[family]):.0f})"
        )
    for present, family in (
        (values["prefix_queries"] or values["prefix_hits"], "prefix"),
        (values["external_queries"] or values["external_hits"], "external prefix"),
    ):
        if not present:
            print(f"[{label}] {family} cache counters: not exposed")


def print_rate(comparison: dict[str, object], interval_label: str | None = None) -> None:
    elapsed = comparison["elapsed_seconds"]
    prefix = f"r{interval_label}" if interval_label else f"last {elapsed:.2f}s"
    usage = comparison["usage_percent"]
    print(f"[{prefix}] KV cache usage: {format_percent(usage)}")
    for row in comparison["rows"]:
        print(
            f"[{prefix}] {row['name']} hit rate: "
            f"{format_percent(row['hit_rate_percent'])}"
            f" (delta_hits={row['delta_hits']:.0f}, delta_queries={row['delta_queries']:.0f},"
            f" fallback={'previous cumulative rate' if row['rate_fallback'] else 'none'},"
            f" window={elapsed:.2f}s)"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        default="host.docker.internal",
        help="vLLM API host (default: host.docker.internal)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="vLLM API port (default: 8000)",
    )
    parser.add_argument(
        "--url",
        help="Full Prometheus metrics URL; overrides --host and --port",
    )
    parser.add_argument(
        "--interval",
        default=10.0,
        type=float,
        help="Seconds between samples (default: 10)",
    )
    parser.add_argument(
        "--count",
        default=1,
        type=int,
        help="Number of rate samples after the initial snapshot; 0 means forever (default: 1)",
    )
    parser.add_argument(
        "--timeout",
        default=5.0,
        type=float,
        help="HTTP timeout in seconds (default: 5)",
    )
    args = parser.parse_args(argv)
    if args.interval < 0:
        parser.error("--interval must be >= 0")
    if args.count < 0:
        parser.error("--count must be >= 0")

    url = args.url or f"http://{args.host}:{args.port}/metrics"
    try:
        first = take_snapshot(url, args.timeout)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"Cannot access {url}: {exc}", file=sys.stderr)
        return 2

    print_snapshot(first, "cumulative")
    remaining = args.count
    while True:
        time.sleep(args.interval)
        try:
            current = take_snapshot(url, args.timeout)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"Cannot access {url}: {exc}", file=sys.stderr)
            return 2
        print_rate(build_comparison(first, current))
        first = current
        if remaining != 0:
            remaining -= 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
