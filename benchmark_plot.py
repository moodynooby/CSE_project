"""Benchmark factorial implementations and plot two charts.

1. Line plot: best-of runtime vs n over log-spaced sample sizes.
2. Distribution plot: box plot of raw timing samples at a fixed n.

One file per chart.
"""
import contextlib
import io
import os
import platform
import subprocess
import sys
import time
from collections import OrderedDict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    import main
except ModuleNotFoundError:
    # Allow running from any working directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import main

FUNCS = OrderedDict([
    ("iterfact",     main.iterfact),
    ("fact1",        main.fact1),
    ("recfact_v1",   main.recfact_v1),
    ("recfact_or0",  main.recfact_or0),
    ("recfact_or1",  main.recfact_or1),
    ("recfact_one",  main.recfact_one),
    ("recfact_lt",   main.recfact_lt),
    ("recfact_set",  main.recfact_set),
])

MAX_N = 2500
REPEATS = 250
POINTS_PER_DECADE = 10
TIME_BUDGET_S = 0.5

# Distribution-plot settings: raw timing samples at a single fixed n
BOX_N = 500
BOX_SAMPLES = 2000

MARKERS = ["o", "s", "^", "D", "v", "<", ">", "p"]


def sample_sizes(n_max=MAX_N, per_decade=POINTS_PER_DECADE):
    """Log-spaced sample of n values: dense at small n, sparse at large n.

    Timing every integer 0..n_max is overkill (25001 points per function)
    and swamps the plot. Runtime curves change fast at small n and are
    smooth at large n, so log spacing captures the interesting region
    with ~40 points total.
    """
    sizes = {0}
    k = 0
    while True:
        v = round(10 ** (k / per_decade))
        if v > n_max:
            break
        sizes.add(v)
        k += 1
    return sorted(sizes)


def cpu_model():
    """Return a human-readable CPU model on any platform."""
    try:
        if sys.platform.startswith("linux"):
            with open("/proc/cpuinfo") as f:
                models = [
                    l.split(":", 1)[1].strip()
                    for l in f if l.startswith("model name")
                ]
            if models:
                return models[0]
        elif sys.platform == "darwin":
            return subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
            ).strip()
        elif sys.platform.startswith("win"):
            name = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command",
                 "(Get-CimInstance Win32_Processor).Name"],
                text=True,
            ).strip()
            if name:
                return name
            return os.environ.get(
                "PROCESSOR_IDENTIFIER", platform.processor() or "unknown"
            )
    except (OSError, subprocess.SubprocessError):
        pass
    return platform.processor() or platform.machine() or "unknown"


def machine_config():
    cfg = ["Machine configuration", "-" * 20]
    cfg.append(f"OS  : {platform.platform()}")
    cfg.append(f"CPU : {cpu_model()}")
    return "\n".join(cfg)


def suppress_stdout(func, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return func(*args)


def time_func(func, n):
    """Best-of timing with a wall-clock budget.

    Fast calls still get up to REPEATS samples; slow calls (big-n
    factorials take milliseconds each) are capped at TIME_BUDGET_S so the
    whole benchmark finishes in reasonable time.
    """
    best = float("inf")
    count = 0
    deadline = time.perf_counter() + TIME_BUDGET_S
    while count < REPEATS:
        t0 = time.perf_counter_ns()
        func(n)
        t1 = time.perf_counter_ns()
        best = min(best, t1 - t0)
        count += 1
        if time.perf_counter() >= deadline:
            break
    return best / 1000.0


def time_samples(func, n, count=BOX_SAMPLES):
    """Collect `count` raw timing samples in microseconds."""
    out = []
    for _ in range(count):
        t0 = time.perf_counter_ns()
        func(n)
        t1 = time.perf_counter_ns()
        out.append((t1 - t0) / 1000.0)
    return out


def save_line_plot(ns, results, config_text):
    """Line plot: best-of runtime vs n, saved as line_plot.png."""
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for (name, ts), marker in zip(results.items(), MARKERS):
        ax.plot(ns, ts, marker=marker, markersize=4, label=name)
    ax.set_yscale("log")
    ax.set_xlabel("Input n (log-spaced samples)")
    ax.set_ylabel("Runtime (µs, log scale)")
    ax.set_title(f"Best-of runtime vs n (up to {REPEATS:,} runs per point)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(ncol=2, fontsize=8, loc="upper left",
              bbox_to_anchor=(1.01, 1.0))
    ax.text(0.0, -0.18, config_text, transform=ax.transAxes, fontsize=8,
            family="monospace", va="top",
            bbox=dict(boxstyle="round", alpha=0.1))
    out = "line_plot.png"
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved plot to {out}")


def save_distribution_plot(dists, config_text):
    """Distribution plot: box plot of raw samples, saved as distribution_plot.png."""
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.boxplot([dists[name] for name in FUNCS],
               tick_labels=list(FUNCS), showfliers=False)
    ax.set_yscale("log")
    ax.set_ylabel("Runtime (µs, log scale)")
    ax.set_title(f"Timing distribution per implementation at n = {BOX_N} "
                 f"({BOX_SAMPLES:,} samples each)")
    ax.tick_params(axis="x", labelrotation=45)
    ax.grid(True, which="both", axis="y", alpha=0.3)
    ax.text(0.0, -0.18, config_text, transform=ax.transAxes, fontsize=8,
            family="monospace", va="top",
            bbox=dict(boxstyle="round", alpha=0.1))
    out = "distribution_plot.png"
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved plot to {out}")


def main():
    print(machine_config())
    config_text = machine_config()

    # --- Line plot data: best-of runtime over log-spaced sample sizes ---
    ns = sample_sizes()
    print("-" * 30)
    print(f"Benchmarking {len(FUNCS)} implementations at {len(ns)} sample sizes "
          f"(n up to {MAX_N:,}, best of up to {REPEATS:,} runs per point)...")
    results = {name: [] for name in FUNCS}
    for i, n in enumerate(ns):
        print(f"\r  {i + 1}/{len(ns)}: n={n:<6}", end="", flush=True)
        for name, func in FUNCS.items():
            try:
                if name == "iterfact":
                    t = time_func(
                        lambda _: suppress_stdout(main.iterfact, n), n)
                else:
                    t = time_func(func, n)
                results[name].append(t)
            except Exception:
                results[name].append(float("nan"))
    print()

    # --- Distribution plot data: raw samples at a fixed n ---
    print(f"Collecting {BOX_SAMPLES:,} timing samples per implementation "
          f"at n = {BOX_N}...")
    dists = {}
    for name, func in FUNCS.items():
        try:
            if name == "iterfact":
                dists[name] = time_samples(
                    lambda _: suppress_stdout(main.iterfact, BOX_N), BOX_N)
            else:
                dists[name] = time_samples(func, BOX_N)
        except Exception:
            dists[name] = []

    save_line_plot(ns, results, config_text)
    save_distribution_plot(dists, config_text)

    with open("machine_config.txt", "w") as f:
        f.write(config_text + "\n")


if __name__ == "__main__":
    main()
