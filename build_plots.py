"""Build the four interactive score-shaping figures for the NEWCAS 2026 talk.

Run:  .venv/bin/python build_plots.py
Outputs self-contained HTML (no internet needed) into plots/ and, if kaleido
is present, PNG thumbnails into plots/thumbs/ for quick visual QA.
"""
from __future__ import annotations

import os
from typing import Any, Callable

import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import score_shaping as ss
from score_shaping import FloatArray, Mode

OUT: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
THUMBS: str = os.path.join(OUT, "thumbs")
os.makedirs(THUMBS, exist_ok=True)

FONT: dict[str, Any] = dict(family="Inter, Helvetica, Arial, sans-serif",
                            size=15, color="#111827")
ALPHAS: list[float] = [0.5, 1.0, 2.0, 3.0, 5.0]   # selectable saturation rates
ALPHA_DEFAULT_IDX: int = 1                          # -> alpha = 1.0


def _wrap(text: str, width: int = 92) -> str:
    """Soft-wrap a subtitle into <br>-joined lines (plotly titles don't wrap)."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "<br>".join(lines)


def _style(fig: go.Figure, title: str, subtitle: str = "") -> go.Figure:
    head = f"<b>{title}</b>"
    if subtitle:
        head += (f"<br><span style='font-size:13px;color:#6b7280'>"
                 f"{_wrap(subtitle)}</span>")
    fig.update_layout(
        title=dict(text=head, x=0.5, xanchor="center", y=0.97, font=dict(size=20)),
        font=FONT, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=70, r=40, t=128, b=70), hovermode="closest",
    )
    fig.update_xaxes(showgrid=True, gridcolor=ss.COLORS["grid"], zeroline=False,
                     linecolor="#9ca3af", ticks="outside")
    fig.update_yaxes(showgrid=True, gridcolor=ss.COLORS["grid"], zeroline=False,
                     linecolor="#9ca3af", ticks="outside")
    return fig


# ============================================================ FIG 1: squashing
def fig_squash() -> go.Figure:
    ph = np.linspace(0, 6, 400)
    fig = go.Figure()
    # linear baseline (unbounded) + saturation reference
    fig.add_trace(go.Scatter(x=ph, y=ph, name="Linear  P̂ = p/S",
                             line=dict(color=ss.COLORS["linear"], width=3)))
    fig.add_hline(y=1.0, line=dict(color="#9ca3af", width=1, dash="dot"),
                  annotation_text="sigmoid ceiling = 1", annotation_position="top left")
    # one sigmoid trace per alpha; toggle via slider
    for a in ALPHAS:
        fig.add_trace(go.Scatter(x=ph, y=ss.sigmoid_squash(ph, a),
                                 name=f"Sigmoid (α={a:g})", visible=False,
                                 line=dict(color=ss.COLORS["sigmoid"], width=3)))
    fig.data[1 + ALPHA_DEFAULT_IDX].visible = True

    # add_hline adds a shape (not a trace), so trace order is [linear, sig0..sigN]
    steps: list[dict[str, Any]] = []
    for i, a in enumerate(ALPHAS):
        vis = [True] + [j == i for j in range(len(ALPHAS))]
        steps.append(dict(method="update", label=f"{a:g}",
                          args=[{"visible": vis},
                                {"annotations[0].text": f"saturation rate α = {a:g}"}]))
    fig.update_layout(sliders=[dict(active=ALPHA_DEFAULT_IDX, currentvalue=dict(
        prefix="α = ", font=dict(size=16, color=ss.COLORS["sigmoid"])),
        pad=dict(t=60), steps=steps)])
    fig.update_xaxes(title="relative error  P̂  (penalty ÷ target scale)", range=[0, 6])
    fig.update_yaxes(title="shaped penalty  P", range=[0, 4])
    _style(fig, "Score shaping squashes outliers into a bounded range",
           "Linear penalty grows without limit; the sigmoid saturates at 1 so a single far-off "
           "metric can’t dominate the cost. Drag α to set how sharply it saturates.")
    fig.update_layout(legend=dict(x=0.98, y=0.05, xanchor="right", yanchor="bottom",
                                  bgcolor="rgba(255,255,255,0.7)"))
    return fig


# ============================================================ FIG 2: masking
def fig_masking() -> go.Figure:
    """Share of total penalty kept by a *near-feasible* metric as another metric
    drifts far from target. Linear lets the outlier mask it; sigmoid bounds the
    outlier so the violated metric stays visible to the optimizer."""
    outlier = np.linspace(0, 10, 400)        # relative error of the dominating metric
    near = 0.30                              # the near-feasible metric's fixed rel. error

    def share(mode: Mode, a: float = 1.0) -> FloatArray:
        if mode == "linear":
            po, pn = outlier, near
        else:
            po, pn = ss.sigmoid_squash(outlier, a), ss.sigmoid_squash(near, a)
        return 100.0 * pn / (po + pn)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=outlier, y=share("linear"), name="Linear",
                             line=dict(color=ss.COLORS["linear"], width=3)))
    for a in ALPHAS:
        fig.add_trace(go.Scatter(x=outlier, y=share("sigmoid", a), visible=False,
                                 name=f"Sigmoid (α={a:g})",
                                 line=dict(color=ss.COLORS["sigmoid"], width=3)))
    fig.data[1 + ALPHA_DEFAULT_IDX].visible = True

    steps: list[dict[str, Any]] = []
    for i, a in enumerate(ALPHAS):
        vis = [True] + [j == i for j in range(len(ALPHAS))]
        steps.append(dict(method="update", label=f"{a:g}", args=[{"visible": vis}]))
    fig.update_layout(sliders=[dict(active=ALPHA_DEFAULT_IDX, currentvalue=dict(
        prefix="α = ", font=dict(size=16, color=ss.COLORS["sigmoid"])),
        pad=dict(t=60), steps=steps)])

    fig.add_annotation(x=8.5, y=share("linear")[-40], ax=40, ay=-30,
                       text="violation<br><b>masked</b>", font=dict(color=ss.COLORS["linear"]),
                       showarrow=True, arrowcolor=ss.COLORS["linear"])
    fig.update_xaxes(title="how far the OTHER metric drifts from target  (relative error)")
    fig.update_yaxes(title="penalty share kept by the near-feasible metric  (%)",
                     range=[0, 55])
    _style(fig, "Linear scoring lets a single outlier ‘mask’ other violations",
           "A metric sitting just outside spec (rel. error 0.30) should keep the optimizer’s "
           "attention. Under linear scoring its share of the cost collapses as another metric "
           "drifts; the bounded sigmoid keeps it visible.")
    fig.update_layout(legend=dict(x=0.98, y=0.98, xanchor="right", yanchor="top",
                                  bgcolor="rgba(255,255,255,0.7)"))
    return fig


# ============================================================ FIG 3: outcome
def _goodness(metric: str, value_disp: float) -> float:
    """Map a presentation-unit value to a radial 'goodness' (1.0 = exactly on target)."""
    s = ss.METRICS[metric]
    t = s["target"] * s["scale"]
    if s["kind"] == "EXCEED":      # higher is better
        return value_disp / t
    if s["kind"] == "MINIMIZE":    # lower is better
        return t / value_disp
    if s["kind"] == "EXACT":       # within ±tol -> >=1 (meets spec), edge -> 1
        tol = s.get("tol", 1.0)
        return max(0.0, 2.0 - abs(value_disp - t) / tol)
    return 1.0


def fig_outcome() -> go.Figure:
    sig = ss.best_design("de_sigmoid")
    lin = ss.best_design("de_linear")
    order: list[str] = ["ugf", "dcgain", "pm", "v(inoise_total)", "i(idd_total)", "tsettle"]
    labels = [ss.METRICS[m]["label"] for m in order]

    fig = make_subplots(rows=1, cols=2, column_widths=[0.48, 0.52], horizontal_spacing=0.12,
                        subplot_titles=("Spec margin per metric  (≥1 = meets spec)",
                                        "Top-100 designs: current vs. bandwidth"))

    # ---- left: grouped spec-margin bars (clip tall bars for readability)
    CAP = 2.4
    def margins(d: dict[str, float]) -> list[float]:
        return [min(CAP, _goodness(m, d[m])) for m in order]
    for d, color, lbl in [(lin, ss.COLORS["linear"], "Linear"),
                          (sig, ss.COLORS["sigmoid"], "Sigmoid")]:
        mg = margins(d)
        fig.add_trace(go.Bar(x=labels, y=mg, name=lbl, marker_color=color, opacity=0.9,
                             text=[f"{v:.2f}" for v in mg], textposition="outside",
                             textfont=dict(size=11),
                             hovertemplate=f"{lbl}: %{{y:.2f}}× target<extra></extra>"), 1, 1)
    # target line + fail zone (plotly stubs type row/col as str; they accept int)
    fig.add_hline(y=1.0, line=dict(color=ss.COLORS["target"], width=2, dash="dash"),
                  row=1, col=1)  # pyright: ignore[reportArgumentType]
    fig.add_shape(type="rect", x0=-0.5, x1=len(order) - 0.5, y0=0, y1=1.0,
                  xref="x", yref="y", fillcolor="rgba(220,38,38,0.07)", line_width=0,
                  layer="below")
    fig.add_annotation(x=4.5, y=0.5, text="fails spec", showarrow=False,
                       font=dict(color=ss.COLORS["linear"], size=12), xref="x", yref="y")

    # ---- right: top-100 clouds + best stars in (UGF, current)
    for name, color, lbl in [("de_sigmoid", ss.COLORS["sigmoid"], "Sigmoid"),
                             ("de_linear", ss.COLORS["linear"], "Linear")]:
        df = ss.load_run(name + "_top100")
        fig.add_trace(go.Scatter(x=df["ugf"], y=df["i(idd_total)"], mode="markers",
                                 name=f"{lbl} top-100", showlegend=False,
                                 marker=dict(color=color, size=6, opacity=0.40),
                                 hovertemplate="UGF %{x:.0f} MHz<br>I %{y:.1f} µA<extra></extra>"),
                      1, 2)
    for d, color, lbl in [(sig, ss.COLORS["sigmoid"], "Sigmoid"),
                          (lin, ss.COLORS["linear"], "Linear")]:
        fig.add_trace(go.Scatter(x=[d["ugf"]], y=[d["i(idd_total)"]], mode="markers",
                                 name=f"{lbl} best", showlegend=False,
                                 marker=dict(color=color, size=20, symbol="star",
                                             line=dict(color="white", width=1.5)),
                                 hovertemplate=f"<b>{lbl} best</b><br>UGF %{{x:.0f}} MHz<br>"
                                               "I %{y:.1f} µA<extra></extra>"), 1, 2)
    # target lines + feasible quadrant
    fig.add_shape(type="rect", x0=200, x1=2000, y0=1, y1=25, xref="x2", yref="y2",
                  fillcolor="rgba(22,163,74,0.08)", line_width=0, layer="below")
    fig.add_vline(x=200, line=dict(color=ss.COLORS["target"], dash="dash"),
                  row=1, col=2)  # pyright: ignore[reportArgumentType]
    fig.add_hline(y=25, line=dict(color=ss.COLORS["target"], dash="dash"),
                  row=1, col=2)  # pyright: ignore[reportArgumentType]
    fig.add_annotation(x=560, y=13, text="✓ feasible<br>≥200 MHz · ≤25 µA", showarrow=False,
                       font=dict(color=ss.COLORS["lhs"], size=12), xref="x2", yref="y2")

    fig.update_yaxes(title="margin = achieved ÷ target", range=[0, CAP + 0.25], row=1, col=1)
    fig.update_xaxes(tickangle=-25, row=1, col=1)
    fig.update_xaxes(title="Unity-gain frequency (MHz)", type="log",
                     range=[np.log10(110), np.log10(950)], row=1, col=2)
    fig.update_yaxes(title="Supply current (µA)", type="log",
                     range=[np.log10(9), np.log10(75)], row=1, col=2)
    _style(fig, "Sigmoid balances every spec; linear blows the current budget",
           "Linear’s best meets bandwidth & gain but lands at 43.7 µA — 1.7× over the 25 µA "
           "budget (current bar below the line, star above it). Sigmoid meets all specs at 20.6 µA.")
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.12,
                      legend=dict(orientation="h", x=0.5, y=-0.16, xanchor="center"))
    return fig


# ============================================================ FIG 4: equi-score
# Strictly-positive metrics get a log axis; the rest (which can be <=0) stay linear.
LOG_METRICS: set[str] = {"ugf", "v(inoise_total)", "i(idd_total)"}


def _axis_grid(metric: str, runs: list, n: int = 140) -> tuple[FloatArray, bool]:
    """Sampling grid (SI units) for `metric`, spanning the explored range with the
    target comfortably inside. Returns (grid, is_log)."""
    spec = ss.METRICS[metric]
    vals = np.concatenate([r[f"{metric}_raw"].to_numpy() for r in runs])
    vals = vals[np.isfinite(vals)]
    lo, hi = float(np.percentile(vals, 1)), float(np.percentile(vals, 99))
    lo, hi = min(lo, spec["target"]), max(hi, spec["target"])  # keep target in view
    is_log = metric in LOG_METRICS
    if is_log:
        lo = max(lo, float(vals[vals > 0].min()))
        loL, hiL = np.log10(lo), np.log10(hi)
        pad = 0.06 * (hiL - loL)
        grid = np.logspace(loL - pad, hiL + pad, n)
    else:
        pad = 0.04 * (hi - lo)
        grid = np.linspace(lo - pad, hi + pad, n)
    return grid, is_log


def fig_contours(x_metric: str = "ugf", y_metric: str = "i(idd_total)") -> go.Figure:
    """Equi-score landscape over any two metrics from ``ss.METRICS``.

    The 2-metric cost field is  F2 = P_x(m_x) + P_y(m_y).  Toggle Linear/Sigmoid;
    the α slider reshapes the sigmoid basin. Real visited points are overlaid.
    """
    sx, sy = ss.METRICS[x_metric], ss.METRICS[y_metric]
    runs = [ss.load_run("de_sigmoid"), ss.load_run("de_linear")]
    xs, xlog = _axis_grid(x_metric, runs)
    ys, ylog = _axis_grid(y_metric, runs)
    XX, YY = np.meshgrid(xs, ys)

    def Z(mode: Mode, a: float = 1.0) -> FloatArray:
        px = ss.normalized_penalty(XX, sx["target"], sx["kind"], mode, a)
        py = ss.normalized_penalty(YY, sy["target"], sy["kind"], mode, a)
        return px + py

    xk, yk = xs * sx["scale"], ys * sy["scale"]   # presentation units for the axes
    xlab = f"{sx['label']} ({sx['unit']})"
    ylab = f"{sy['label']} ({sy['unit']})"

    def heat(z: FloatArray, mode: Mode) -> go.Contour:
        zmax = 2.0 if mode == "sigmoid" else float(np.percentile(z, 92))
        return go.Contour(x=xk, y=yk, z=z, colorscale="Viridis_r",
                          zmin=0, zmax=zmax, ncontours=18,
                          contours=dict(showlabels=True,
                                        labelfont=dict(size=10, color="white")),
                          colorbar=dict(title="total<br>penalty", x=1.02),
                          hovertemplate=f"{sx['label']} %{{x:.3s}}<br>"
                                        f"{sy['label']} %{{y:.3s}}<br>"
                                        "penalty %{z:.2f}<extra></extra>")

    fig = go.Figure()
    # trace 0: linear contour, then one sigmoid contour per alpha. Start on the
    # default-alpha sigmoid so the basin reads first; the rest start hidden.
    lin_contour = heat(Z("linear"), "linear")
    lin_contour.visible = False
    fig.add_trace(lin_contour)
    for i, a in enumerate(ALPHAS):
        t = heat(Z("sigmoid", a), "sigmoid")
        t.visible = (i == ALPHA_DEFAULT_IDX)
        fig.add_trace(t)

    # overlays: sampled visited points + best designs for the chosen pair
    sig, lin = ss.best_design("de_sigmoid"), ss.best_design("de_linear")
    dfa, dfb = runs
    samp = slice(None, None, 8)
    overlays = [
        go.Scatter(x=dfb[x_metric][samp], y=dfb[y_metric][samp], mode="markers",
                   name="Linear visited", marker=dict(color=ss.COLORS["linear"], size=4,
                   opacity=0.30), hoverinfo="skip"),
        go.Scatter(x=dfa[x_metric][samp], y=dfa[y_metric][samp], mode="markers",
                   name="Sigmoid visited", marker=dict(color=ss.COLORS["sigmoid"], size=4,
                   opacity=0.30), hoverinfo="skip"),
        go.Scatter(x=[lin[x_metric]], y=[lin[y_metric]], mode="markers", name="Linear best",
                   marker=dict(color=ss.COLORS["linear"], size=16, symbol="star",
                   line=dict(color="white", width=1.5))),
        go.Scatter(x=[sig[x_metric]], y=[sig[y_metric]], mode="markers", name="Sigmoid best",
                   marker=dict(color=ss.COLORS["sigmoid"], size=16, symbol="star",
                   line=dict(color="white", width=1.5))),
    ]
    for o in overlays:
        fig.add_trace(o)
    n_overlay = len(overlays)
    n_contour = 1 + len(ALPHAS)

    # target guides (layout shapes -> unaffected by trace visibility); EXACT adds a band
    def guide(spec: ss.MetricSpec, axis: str) -> None:
        t = spec["target"] * spec["scale"]
        guides: list[tuple[float, str, float]] = [(t, "dash", 1.5)]
        if spec["kind"] == "EXACT":
            tol = spec.get("tol", 0.0) * spec["scale"]
            guides += [(t + tol, "dot", 1.0), (t - tol, "dot", 1.0)]
        for pos, dash, w in guides:
            line = dict(color="white", width=w, dash=dash)
            if axis == "x":
                fig.add_vline(x=pos, line=line)
            else:
                fig.add_hline(y=pos, line=line)
    guide(sx, "x")
    guide(sy, "y")

    def vis(contour_idx: int) -> list[bool]:
        v = [False] * n_contour + [True] * n_overlay
        v[contour_idx] = True
        return v

    # buttons: Linear vs Sigmoid(current alpha). Slider: alpha (only affects sigmoid).
    fig.update_layout(updatemenus=[dict(
        type="buttons", direction="right", x=0.0, y=1.12, xanchor="left",
        buttons=[
            dict(label="Linear (unbounded)", method="update",
                 args=[{"visible": vis(0)}]),
            dict(label="Sigmoid (bounded)", method="update",
                 args=[{"visible": vis(1 + ALPHA_DEFAULT_IDX)}]),
        ])])
    steps: list[dict[str, Any]] = []
    for i, a in enumerate(ALPHAS):
        steps.append(dict(method="update", label=f"{a:g}",
                          args=[{"visible": vis(1 + i)}]))
    fig.update_layout(sliders=[dict(active=ALPHA_DEFAULT_IDX, currentvalue=dict(
        prefix="sigmoid α = ", font=dict(size=15, color=ss.COLORS["sigmoid"])),
        pad=dict(t=50), steps=steps)])

    # explicit ranges: autorange mis-fires on a log-axis contour
    fig.update_xaxes(title=xlab, type="log" if xlog else "linear",
                     range=[np.log10(xk[0]), np.log10(xk[-1])] if xlog else [xk[0], xk[-1]])
    fig.update_yaxes(title=ylab, type="log" if ylog else "linear",
                     range=[np.log10(yk[0]), np.log10(yk[-1])] if ylog else [yk[0], yk[-1]])
    _style(fig, f"Equi-score landscape: {sx['label']} × {sy['label']}",
           "Cost field  F₂ = Pₓ(mₓ) + P_y(m_y).  Linear → straight, parallel iso-lines "
           "dominated by one axis (the other is masked). Sigmoid → a bounded, concentric "
           "basin pulling toward the feasible corner. Toggle the mode and drag α.")
    fig.update_layout(legend=dict(x=0.01, y=0.01, xanchor="left", yanchor="bottom",
                                  bgcolor="rgba(255,255,255,0.75)", font=dict(size=11)))
    return fig


# ============================================================ build
FIGS: dict[str, Callable[[], go.Figure]] = {
    "1_squashing_curves": fig_squash,
    "2_masking_demo": fig_masking,
    "3_tradeoff_outcome": fig_outcome,
    "4_equiscore_contours": fig_contours,
}


CARDS: list[tuple[str, str, str]] = [
    ("1_squashing_curves", "1 · The squashing function",
     "Linear vs. sigmoid penalty mapping. Drag α to set the saturation rate."),
    ("2_masking_demo", "2 · The masking effect",
     "How a single far-off metric hides another’s violation under linear scoring."),
    ("3_tradeoff_outcome", "3 · The trade-off outcome",
     "Best designs & top-100 clouds — sigmoid meets every spec, linear blows the current budget."),
    ("4_equiscore_contours", "4 · Equi-score landscape",
     "Iso-score contours over two metric axes. Toggle Linear/Sigmoid; drag α."),
]


def write_index() -> None:
    cards = "\n".join(
        f"""<a class="card" href="{n}.html">
              <div class="num">{t.split(' · ')[0]}</div>
              <h3>{t.split(' · ')[1]}</h3><p>{d}</p>
              <span class="open">Open ▸</span></a>"""
        for n, t, d in CARDS)
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Score Shaping — interactive figures (NEWCAS 2026)</title>
<style>
 body{{font-family:Inter,Helvetica,Arial,sans-serif;background:#f8fafc;color:#111827;
   margin:0;padding:48px 24px;}}
 .wrap{{max-width:980px;margin:0 auto;}}
 h1{{font-size:30px;margin:0 0 6px;}} .sub{{color:#6b7280;margin:0 0 32px;font-size:16px;}}
 .grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;}}
 .card{{display:block;background:white;border:1px solid #e5e7eb;border-radius:14px;
   padding:22px 24px;text-decoration:none;color:inherit;transition:.15s;position:relative;}}
 .card:hover{{transform:translateY(-3px);box-shadow:0 10px 24px rgba(0,0,0,.08);
   border-color:#2563eb;}}
 .num{{font-size:13px;font-weight:700;color:#2563eb;letter-spacing:.05em;}}
 .card h3{{margin:6px 0 8px;font-size:19px;}} .card p{{margin:0;color:#6b7280;font-size:14px;
   line-height:1.5;}}
 .open{{display:inline-block;margin-top:14px;color:#2563eb;font-weight:600;font-size:14px;}}
 footer{{color:#9ca3af;font-size:13px;margin-top:32px;text-align:center;}}
</style></head><body><div class="wrap">
 <h1>Score Shaping &amp; Pareto Optimality</h1>
 <p class="sub">Interactive figures · NEWCAS 2026 · telescopic OTA, IHP-130nm · real
   Differential-Evolution runs from SpiceXplorer</p>
 <div class="grid">{cards}</div>
 <footer>Self-contained — works offline. Click any card; use the in-figure sliders/buttons.</footer>
</div></body></html>"""
    path = os.path.join(OUT, "index.html")
    with open(path, "w") as f:
        f.write(html)
    print("wrote", path)


def main() -> None:
    config: dict[str, Any] = {"displaylogo": False,
              "toImageButtonOptions": {"format": "svg", "scale": 2}}
    for name, fn in FIGS.items():
        fig = fn()
        path = os.path.join(OUT, f"{name}.html")
        fig.write_html(path, include_plotlyjs=True, full_html=True, config=config)
        print("wrote", path)
        try:
            fig.write_image(os.path.join(THUMBS, f"{name}.png"),
                            width=1100, height=720, scale=1)
        except Exception as e:
            print("  (thumb skipped:", e, ")")
    write_index()
    print("done")


if __name__ == "__main__":
    main()
