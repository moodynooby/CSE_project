import contextlib
import io
import os
import platform
import sys
import time
from collections import OrderedDict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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

MAX_N = 25000
REPEATS = 2000
CALIB = 200_000


def machine_config():
    cfg = ["Machine configuration:", "-" * 30]
    cfg.append(f"OS        : {platform.platform()}")
    cfg.append(f"Hostname  : {platform.node()}")
    cfg.append(f"Python    : {sys.version.split()[0]} ({sys.executable})")
    with open("/proc/cpuinfo") as f:
        lines = f.read().splitlines()
    models = [l.split(":", 1)[1].strip() for l in lines if l.startswith("model name")]
    cfg.append(f"CPU       : {models[0] if models else 'unknown'}")
    cfg.append(f"CPU cores : {os.cpu_count()} logical")
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemTotal"):
                mem = int(line.split()[1]) // 1024
                cfg.append(f"RAM       : {mem:,} MB")
                break
    return "\n".join(cfg)


def suppress_stdout(func, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return func(*args)


def time_func(func, n):
    best = float("inf")
    for _ in range(REPEATS):
        t0 = time.perf_counter_ns()
        func(n)
        t1 = time.perf_counter_ns()
        best = min(best, t1 - t0)
    return best / 1000.0


def main():
    print(machine_config())
    print("-" * 30)
    print("Benchmarking...")

    results = {name: [] for name in FUNCS}
    for n in range(0, MAX_N + 1):
        for name, func in FUNCS.items():
            try:
                if name == "iterfact":
                    t = time_func(lambda: suppress_stdout(main.iterfact, n), None)
                else:
                    t = time_func(func, n)
                results[name].append(t)
            except Exception:
                results[name].append(float("nan"))

    fig, ax = plt.subplots(figsize=(10, 6))
    x = list(range(0, MAX_N + 1))
    for name, ts in results.items():
        ax.plot(x, ts, marker="o", markersize=4, label=name)

    ax.set_yscale("log")
    ax.set_xlabel("Input n")
    ax.set_ylabel("Runtime (microseconds, log scale)")
    ax.set_title(f"Factorial implementations runtime vs input (best of {REPEATS:,} runs)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()

    config_text = machine_config()
    ax.text(0.0, -0.22, config_text, transform=ax.transAxes, fontsize=8,
            family="monospace", va="top", bbox=dict(boxstyle="round", alpha=0.1))

    out = "runtime_plot.png"
    fig.tight_layout(rect=[0, 0.12, 1, 1])
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\nSaved plot to {out}")

    with open("machine_config.txt", "w") as f:
        f.write(config_text + "\n")


if __name__ == "__main__":
    main()
