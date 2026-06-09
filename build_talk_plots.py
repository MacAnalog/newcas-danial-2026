"""Presentation-ready static figures for the NEWCAS 2026 talk.

Generates three high-resolution PNGs from the real SpiceXplorer DE/LHS runs:
  1. convergence_trace.png   - score vs iteration, sigmoid vs linear (+ best-so-far),
                               zero-crossing = constraint satisfaction.
  2. tradeoff_clouds.png     - top-100 clouds (current vs gain, current vs UGF) +
                               spec-margin bars; linear blows the 25 uA budget.
  3. metric_distributions.png- histograms of UGF and supply current across
                               sigmoid / linear / LHS (exploration behaviour).

Run:  python3 build_talk_plots.py
Out:  plots/talk/*.png  (transparent-friendly white bg, 200 dpi)
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# score_shaping.py uses typing.NotRequired (3.11+); shim for older interpreters.
import typing as _t
if not hasattr(_t, "NotRequired"):
    _t.NotRequired = _t.Optional  # subscriptable stand-in, runtime-only

import score_shaping as ss

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plots", "talk")
os.makedirs(OUT, exist_ok=True)

C = ss.COLORS            # sigmoid=blue, linear=red, lhs=green, target=ink
plt.rcParams.update({
    "font.size": 15,
    "axes.titlesize": 17,
    "axes.titleweight": "bold",
    "axes.labelsize": 15,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "figure.constrained_layout.use": False,
    "axes.grid": True,
    "grid.color": C["grid"],
    "grid.linewidth": 0.8,
})


def _best_so_far(score: np.ndarray) -> np.ndarray:
    return np.maximum.accumulate(score)


# ----------------------------------------------------------------- Figure 1
def fig_convergence() -> None:
    sig = ss.load_run("de_sigmoid")
    lin = ss.load_run("de_linear")
    fig, ax = plt.subplots(figsize=(11, 6))

    YLO, YHI = -260, 75
    for df, key in [(lin, "linear"), (sig, "sigmoid")]:
        raw = df["score"].to_numpy()
        ax.plot(df["iter"], np.clip(raw, YLO, YHI), color=C[key], alpha=0.18, lw=0.7)
        ax.plot(df["iter"], _best_so_far(raw),
                color=C[key], lw=3, label=f"{key.capitalize()} (best-so-far)")

    ax.axhline(0, color=C["target"], lw=1.6, ls="--")
    ax.text(1980, 3, "feasibility  (score = 0)", color=C["target"],
            fontsize=12, va="bottom", ha="right")

    # mark where sigmoid first crosses zero
    sig_best = _best_so_far(sig["score"].to_numpy())
    cross = int(np.argmax(sig_best >= 0)) if (sig_best >= 0).any() else None
    if cross:
        ax.axvline(cross, color=C["sigmoid"], lw=1.2, ls=":")
        ax.annotate(f"sigmoid feasible @ iter {cross}",
                    xy=(cross, 0), xytext=(cross + 120, -90),
                    color=C["sigmoid"], fontsize=12, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=C["sigmoid"]))

    ax.annotate("linear never reaches feasibility",
                xy=(1850, max(_best_so_far(lin["score"].to_numpy())[-1], YLO)),
                xytext=(650, -180), color=C["linear"], fontsize=12, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C["linear"]))

    ax.set_xlabel("Optimization iteration")
    ax.set_ylabel("Aggregate score  F(x)")
    ax.set_title("Convergence: sigmoid shaping reaches the feasible region; linear does not")
    ax.set_xlim(0, 2000)
    ax.set_ylim(YLO, YHI)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "convergence_trace.png"))
    plt.close(fig)


# ----------------------------------------------------------------- Figure 2
def _cloud(ax, xcol, xlabel, logx=False):
    lhs = ss.load_run("lhs_baseline")
    sig = pd.read_csv(os.path.join(ss.DATA_DIR, "de_sigmoid_top100.csv"))
    lin = pd.read_csv(os.path.join(ss.DATA_DIR, "de_linear_top100.csv"))

    def col(df, m):
        return df[f"fit_summary.{m}.curr_val"].to_numpy() * ss.METRICS[m]["scale"]

    ax.scatter(lhs[xcol[0]] if isinstance(xcol, tuple) else col_run(lhs, xcol),
               lhs["i(idd_total)"], s=6, c=C["lhs"], alpha=0.12, label="LHS baseline")
    for df, key in [(lin, "linear"), (sig, "sigmoid")]:
        ax.scatter(col(df, xcol), col(df, "i(idd_total)"),
                   s=34, c=C[key], alpha=0.85, edgecolors="white", linewidths=0.4,
                   label=f"{key.capitalize()} top-100")
    ax.axhline(25, color=C["target"], lw=1.6, ls="--")
    ax.text(ax.get_xlim()[0], 26, "25 µA current budget", color=C["target"], fontsize=11)
    ax.set_yscale("log")
    if logx:
        ax.set_xscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Supply current  I$_{DD}$ (µA)")


def col_run(df, m):
    return df[m].to_numpy()


def fig_tradeoff() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(19, 6.2))
    # panel a: current vs gain
    _cloud(axes[0], "dcgain", "DC gain (dB)")
    axes[0].set_title("(a) Current vs DC gain")
    axes[0].legend(loc="upper left", frameon=False, fontsize=11)
    # panel b: current vs UGF
    _cloud(axes[1], "ugf", "Unity-gain frequency (MHz)", logx=True)
    axes[1].set_title("(b) Current vs UGF")

    # panel c: spec-margin bars from best designs (Table III)
    sig = ss.best_design("de_sigmoid")
    lin = ss.best_design("de_linear")
    metrics = ["ugf", "dcgain", "pm", "v(inoise_total)", "i(idd_total)", "tsettle"]
    labels = [ss.METRICS[m]["label"] for m in metrics]

    def margin(b, m):
        s = ss.METRICS[m]
        v, t = b[m], s["target"] * s["scale"]
        if s["kind"] == "EXCEED":      # want v >= t  -> positive good
            return (v - t) / t * 100
        if s["kind"] == "MINIMIZE":    # want v <= t  -> positive good if under
            return (t - v) / t * 100
        return -abs(v - t) / (s.get("tol", 1)) * 100  # EXACT: 0 is best

    sig_m = [margin(sig, m) for m in metrics]
    lin_m = [margin(lin, m) for m in metrics]
    y = np.arange(len(metrics))
    h = 0.38
    ax = axes[2]
    ax.grid(axis="y", visible=False)
    ax.barh(y + h/2, sig_m, height=h, color=C["sigmoid"], label="Sigmoid (best)")
    ax.barh(y - h/2, lin_m, height=h, color=C["linear"], label="Linear (best)")
    ax.axvline(0, color=C["target"], lw=1.6)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Spec margin (%)   →  meets spec")
    ax.set_title("(c) Spec margin per metric")
    ax.legend(loc="lower right", frameon=False, fontsize=11)
    ax.set_xlim(-160, 160)
    # annotate the linear current violation
    idx = metrics.index("i(idd_total)")
    ax.annotate("linear: 43.7 µA\n(violates 25 µA)", xy=(lin_m[idx], idx - h/2),
                xytext=(-150, idx - 1.2), color=C["linear"], fontsize=10.5, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C["linear"]))

    fig.suptitle("Trade-off outcome: sigmoid meets every spec; linear maximizes UGF/gain but blows the current budget",
                 fontsize=15, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(OUT, "tradeoff_clouds.png"))
    plt.close(fig)


# ----------------------------------------------------------------- Figure 3
def fig_distributions() -> None:
    runs = {"sigmoid": ss.load_run("de_sigmoid"),
            "linear": ss.load_run("de_linear"),
            "lhs": ss.load_run("lhs_baseline")}
    names = {"sigmoid": "Sigmoid", "linear": "Linear", "lhs": "LHS baseline"}

    fig, axes = plt.subplots(2, 3, figsize=(18, 9), sharey="row")

    ugf_bins = np.logspace(2, 9.3, 40)
    idd_bins = np.logspace(0, 3, 40)

    for j, key in enumerate(["sigmoid", "linear", "lhs"]):
        df = runs[key]
        # row 0: UGF
        ax = axes[0, j]
        w = np.ones(len(df)) / len(df) * 100
        ax.hist(df["ugf"] * 1e6, bins=ugf_bins, color=C[key], alpha=0.85, weights=w)
        ax.axvline(200, color=C["target"], ls="--", lw=1.5)
        ax.set_xscale("log")
        ax.set_title(f"{names[key]}")
        if j == 0:
            ax.set_ylabel("UGF\n% of simulations")
        ax.set_xlabel("Unity-gain freq. (Hz)")
        # row 1: IDD
        ax = axes[1, j]
        ax.hist(df["i(idd_total)"], bins=idd_bins, color=C[key], alpha=0.85, weights=w)
        ax.axvline(25, color=C["target"], ls="--", lw=1.5)
        ax.set_xscale("log")
        if j == 0:
            ax.set_ylabel("Supply current\n% of simulations")
        ax.set_xlabel("Supply current (µA)")

    # one shared legend note for the dashed target line
    axes[0, 2].text(0.98, 0.92, "dashed = spec target", transform=axes[0, 2].transAxes,
                    ha="right", color=C["target"], fontsize=11)
    fig.suptitle("Where each method spends its simulations  (top: UGF, bottom: supply current)",
                 fontsize=16, fontweight="bold", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(os.path.join(OUT, "metric_distributions.png"))
    plt.close(fig)


if __name__ == "__main__":
    fig_convergence()
    fig_tradeoff()
    fig_distributions()
    print("wrote:", os.listdir(OUT))
