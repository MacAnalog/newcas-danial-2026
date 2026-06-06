"""Score-shaping math + data loading for the NEWCAS 2026 talk plots.

Everything the interactive figures need is here so the notebook stays thin.
Penalty / normalization definitions follow Section III of the paper:

    raw penalty p_i      EXCEED   : max(0, T_i - m_i)        (maximize specs)
                         MINIMIZE : max(0, m_i - T_i)        (minimize specs)
                         EXACT    : |m_i - T_i|              (target a value)

    linear  (baseline)   P_hat = p / S          (S = |T|, unbounded)
    sigmoid (proposed)   P     = 2/(1+e^{-a*P_hat}) - 1   (bounded [0,1))
"""
from __future__ import annotations

import os
from typing import Literal, NotRequired, TypedDict

import numpy as np
import numpy.typing as npt
import pandas as pd

# ---------------------------------------------------------------- type aliases
Kind = Literal["EXCEED", "MINIMIZE", "EXACT"]
Mode = Literal["linear", "sigmoid"]
FloatArray = npt.NDArray[np.float64]
BoolArray = npt.NDArray[np.bool_]


class MetricSpec(TypedDict):
    """Per-metric optimization target (Table I)."""

    label: str
    kind: Kind
    target: float
    unit: str
    scale: float          # SI -> presentation units multiplier
    tol: NotRequired[float]  # half-window for EXACT constraints


DATA_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------- metric specs
# Targets from Table I. `scale` converts SI -> presentation units.
METRICS: dict[str, MetricSpec] = {
    "ugf":             {"label": "Unity-Gain Freq.", "kind": "EXCEED",   "target": 200e6,  "unit": "MHz", "scale": 1e-6},
    "dcgain":          {"label": "DC Gain",          "kind": "EXCEED",   "target": 40.0,   "unit": "dB",  "scale": 1.0},
    "v(inoise_total)": {"label": "Input Noise",      "kind": "MINIMIZE", "target": 1.2e-3, "unit": "mV",  "scale": 1e3},
    "i(idd_total)":    {"label": "Supply Current",   "kind": "MINIMIZE", "target": 25e-6,  "unit": "µA", "scale": 1e6},
    "pm":              {"label": "Phase Margin",     "kind": "EXACT",    "target": 60.0,   "unit": "°", "scale": 1.0, "tol": 10.0},
    "tsettle":         {"label": "Settling Time",    "kind": "MINIMIZE", "target": 15e-6,  "unit": "µs", "scale": 1e6},
}

# A consistent colour language for the whole deck.
COLORS: dict[str, str] = dict(sigmoid="#2563eb", linear="#dc2626", lhs="#16a34a",
                              target="#111827", grid="#e5e7eb")


# ---------------------------------------------------------------- core math
def raw_penalty(m: npt.ArrayLike, target: float, kind: Kind) -> FloatArray:
    """Raw (un-normalized) penalty p_i for measured value(s) m."""
    m = np.asarray(m, dtype=float)
    if kind == "EXCEED":
        return np.maximum(0.0, target - m)
    if kind == "MINIMIZE":
        return np.maximum(0.0, m - target)
    if kind == "EXACT":
        return np.abs(m - target)
    raise ValueError(kind)


def rel_error(m: npt.ArrayLike, target: float, kind: Kind) -> FloatArray:
    """Linear normalized penalty  P_hat = p / |T|  (Eq. 1)."""
    return raw_penalty(m, target, kind) / abs(target)


def sigmoid_squash(p_hat: npt.ArrayLike, alpha: float = 1.0) -> FloatArray:
    """Sigmoid shaping  P = 2/(1+e^{-a*P_hat}) - 1  (Eq. 2). Bounded [0,1)."""
    p_hat = np.asarray(p_hat, dtype=float)
    return 2.0 / (1.0 + np.exp(-alpha * p_hat)) - 1.0


def normalized_penalty(m: npt.ArrayLike, target: float, kind: Kind,
                       mode: Mode = "sigmoid", alpha: float = 1.0) -> FloatArray:
    """Per-metric normalized penalty under the chosen shaping mode."""
    p_hat = rel_error(m, target, kind)
    return sigmoid_squash(p_hat, alpha) if mode == "sigmoid" else p_hat


# ---------------------------------------------------------------- data loading
_COL: str = "fit_summary.{m}.curr_val"
_SCORE: str = "fit_summary.{m}.score"


def load_run(name: str) -> pd.DataFrame:
    """Load a run CSV (e.g. 'de_sigmoid') into a tidy frame of metric values.

    Returns columns: <metric> (presentation units), <metric>_raw (SI),
    <metric>_score (per-metric contribution logged by SpiceXplorer), plus
    'score' (aggregate point.score) and 'iter'.
    """
    df = pd.read_csv(os.path.join(DATA_DIR, f"{name}.csv"))
    out = pd.DataFrame()
    out["iter"] = np.arange(len(df))
    out["score"] = df["point.score"].to_numpy()
    for m, spec in METRICS.items():
        raw = df[_COL.format(m=m)].to_numpy()
        out[f"{m}_raw"] = raw
        out[m] = raw * spec["scale"]
        sc = _SCORE.format(m=m)
        if sc in df.columns:
            out[f"{m}_score"] = df[sc].to_numpy()
    return out


def feasible_mask(df: pd.DataFrame) -> BoolArray:
    """Boolean mask: rows meeting *all* Table-I constraints (SI columns)."""
    ok: BoolArray = np.ones(len(df), dtype=bool)
    for m, s in METRICS.items():
        v = df[f"{m}_raw"].to_numpy()
        if s["kind"] == "EXCEED":
            ok &= v >= s["target"]
        elif s["kind"] == "MINIMIZE":
            ok &= v <= s["target"]
        elif s["kind"] == "EXACT":
            ok &= np.abs(v - s["target"]) <= s.get("tol", 0.0)
    return ok


def best_design(name: str) -> dict[str, float]:
    """Top-ranked design from a *_top100 file as a dict of presentation-unit values."""
    df = pd.read_csv(os.path.join(DATA_DIR, f"{name}_top100.csv")).iloc[0]
    d: dict[str, float] = {"score": float(df["point.score"])}
    for m, spec in METRICS.items():
        d[m] = float(df[_COL.format(m=m)]) * spec["scale"]
        d[f"{m}_raw"] = float(df[_COL.format(m=m)])
    return d
