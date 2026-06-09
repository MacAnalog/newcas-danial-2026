"""Build a single self-contained INTERACTIVE HTML slide deck for NEWCAS 2026.

Embeds the six live Plotly figures from build_plots.py (alpha sliders, linear/
sigmoid toggles, hover) into a keyboard-navigable, projection-ready deck. One
shared Plotly bundle; figures are lazy-initialised per slide. Works offline.

Run:  python3 build_interactive_deck.py
Out:  presentation/NEWCAS_ScoreShaping_INTERACTIVE.html
"""
from __future__ import annotations

import base64
import json
import os
import typing as _t

# score_shaping.py uses typing.NotRequired (3.11+); shim for 3.10 interpreters.
if not hasattr(_t, "NotRequired"):
    _t.NotRequired = _t.Optional  # type: ignore[attr-defined]

import plotly.io as pio
from plotly.offline import get_plotlyjs

import build_plots as bp

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "presentation", "NEWCAS_ScoreShaping_INTERACTIVE.html")
DECK_FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"


# ---------------------------------------------------------------- figure prep
def prep(fig, top=56, b=74, l=70, r=44):
    """Strip the in-figure title (the slide carries the heading), make the
    figure autosize/responsive, and bump type for projection."""
    fig.update_layout(
        title_text="", autosize=True,
        margin=dict(l=l, r=r, t=top, b=b),
        font=dict(family=DECK_FONT, size=16, color="#111827"),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    return json.loads(pio.to_json(fig))


def build_figures() -> dict:
    """Return {fig_id: plotly_json_dict} for the six interactive figures."""
    return {
        "squash":        prep(bp.fig_squash(),        top=54, b=80),
        "masking":       prep(bp.fig_masking(),       top=54, b=80),
        "convergence":   prep(bp.fig_convergence(),   top=54, b=72),
        "outcome":       prep(bp.fig_outcome(),       top=66, b=96),
        "contours":      prep(bp.fig_contours(),      top=98, b=82, r=92),
        "distributions": prep(bp.fig_distributions(), top=60, b=72, r=82),
    }


def b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


# ---------------------------------------------------------------- block diagram (SVG)
BLOCK_SVG = """
<svg viewBox="0 0 1180 430" class="blocksvg" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="ar" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto">
      <path d="M0,0 L7,3 L0,6 Z" fill="#7A003C"/>
    </marker>
    <marker id="arb" markerWidth="11" markerHeight="11" refX="3" refY="3.2" orient="auto">
      <path d="M0,0 L7,3.2 L0,6.4 Z" fill="#2563eb"/>
    </marker>
  </defs>
  <!-- YAML config -->
  <rect x="20" y="168" width="150" height="92" rx="12" class="bx bx-cfg"/>
  <text x="95" y="200" class="bt bt-h">config.yaml</text>
  <text x="95" y="224" class="bt bt-s">specs · ranges</text>
  <text x="95" y="242" class="bt bt-s">engines · score</text>
  <!-- core engine container -->
  <rect x="250" y="44" width="560" height="342" rx="16" class="bx bx-core"/>
  <text x="530" y="74" class="bt bt-core">SpiceXplorer engine</text>
  <!-- optimizer -->
  <rect x="280" y="100" width="220" height="118" rx="12" class="bx bx-opt"/>
  <text x="390" y="130" class="bt bt-h">Black-box optimizer</text>
  <text x="390" y="156" class="bt bt-s">Nevergrad · Ax</text>
  <text x="390" y="178" class="bt bt-s">DE · BFGS · LHS</text>
  <text x="390" y="200" class="bt bt-s">14-D design vector x</text>
  <!-- spice -->
  <rect x="560" y="100" width="220" height="118" rx="12" class="bx bx-spice"/>
  <text x="670" y="130" class="bt bt-h">SPICE engine</text>
  <text x="670" y="156" class="bt bt-s">ngspice netlist</text>
  <text x="670" y="178" class="bt bt-s">AC · noise · tran</text>
  <text x="670" y="200" class="bt bt-s">metric extraction</text>
  <!-- score shaping -->
  <rect x="280" y="258" width="500" height="96" rx="12" class="bx bx-score"/>
  <text x="530" y="288" class="bt bt-h">Score shaping &#8212; the lever of this work</text>
  <text x="530" y="314" class="bt bt-lin">linear  P&#770; = p / |T|</text>
  <text x="530" y="336" class="bt bt-sig">sigmoid  P = 2/(1+e&#8315;&#7488;&#7472;&#770;) &#8722; 1</text>
  <!-- viz -->
  <rect x="1010" y="168" width="150" height="92" rx="12" class="bx bx-viz"/>
  <text x="1085" y="200" class="bt bt-h">Pareto &amp;</text>
  <text x="1085" y="222" class="bt bt-h">exploration</text>
  <text x="1085" y="244" class="bt bt-s">viz</text>
  <!-- arrows -->
  <line x1="170" y1="214" x2="276" y2="160" class="arrow"/>
  <line x1="500" y1="150" x2="556" y2="150" class="arrow-b"/>
  <line x1="556" y1="172" x2="500" y2="172" class="arrow-b"/>
  <line x1="810" y1="214" x2="1006" y2="210" class="arrow"/>
  <text x="528" y="142" class="bt bt-mini">propose x</text>
  <text x="528" y="190" class="bt bt-mini">metrics</text>
</svg>
"""


# ---------------------------------------------------------------- slides
def slide_title():
    return """
<section class="slide title-slide">
  <div class="title-bar"></div>
  <div class="title-body">
    <div class="kicker maroon">IEEE NEWCAS 2026 &nbsp;·&nbsp; Lecture &nbsp;·&nbsp; June 22, 2026</div>
    <h1>Score Shaping &amp; Pareto Optimality<br>in Analog IC Design Automation</h1>
    <p class="subtitle">Why the <em>shape</em> of your score function decides whether
       automated transistor sizing succeeds.</p>
    <div class="title-meta">
      <div><strong>Danial Noori Zadeh</strong></div>
      <div class="muted">MacAnalog &nbsp;·&nbsp; McMaster University, Electrical &amp; Computer Engineering</div>
    </div>
  </div>
  <div class="brandmark">
    <span class="bm-main">McMaster <span class="bm-u">University</span></span>
    <span class="bm-div"></span>
    <span class="bm-eng">Engineering</span>
  </div>
</section>"""


def slide_speaker():
    return """
<section class="slide">
  <div class="head">
    <div class="kicker">02 &nbsp;·&nbsp; SPEAKER &amp; GROUP</div>
    <h2>MacAnalog &#8212; analog design automation at McMaster</h2>
  </div>
  <div class="two-col">
    <div class="panel">
      <h3>Danial Noori Zadeh</h3>
      <p class="muted">Electrical &amp; Computer Engineering, McMaster University.
        Building open tooling that puts <em>optimization formulation</em> &#8212; not just
        the solver &#8212; at the centre of analog sizing.</p>
      <ul class="ticks">
        <li>SpiceXplorer: YAML-driven black-box optimization over SPICE.</li>
        <li>This talk: a controlled study of how the <em>score function shape</em>
            changes what the optimizer finds.</li>
      </ul>
    </div>
    <div class="panel accent">
      <div class="bignum maroon">1</div>
      <p class="big-claim">One message for the next 12 minutes:</p>
      <p class="thesis">Problem <u>formulation</u> matters as much as the solver.
         A bounded (sigmoid) score meets every spec where the unbounded (linear)
         baseline silently blows the current budget &#8212; and finds
         <strong>~2&times; lower-power</strong> designs.</p>
    </div>
  </div>
</section>"""


def slide_problem():
    return """
<section class="slide">
  <div class="head">
    <div class="kicker">03 &nbsp;·&nbsp; THE PROBLEM</div>
    <h2>Sizing is a constrained, multi-objective trade-off</h2>
    <p class="insight">Analog specs live on wildly different scales &#8212; and how you
       normalize them decides what the optimizer chases.</p>
  </div>
  <div class="two-col">
    <div class="panel">
      <h3>The setup</h3>
      <ul class="ticks">
        <li>Find a parameter vector <strong>x</strong> (widths, lengths, biases)
            that meets hard targets <strong>T</strong>, then maximizes a figure of merit.</li>
        <li>Objectives are application-dependent: bandwidth, gain, noise, power,
            phase margin, settling &#8212; all at once.</li>
      </ul>
    </div>
    <div class="panel">
      <h3>The gap</h3>
      <ul class="ticks">
        <li>Research over-fixates on the <em>solver</em>; the <em>score function</em>
            is under-studied.</li>
        <li>An ill-shaped objective stalls even a strong optimizer.</li>
      </ul>
      <div class="callout lin-callout">
        A 500&nbsp;MHz bandwidth error and a 100% power error live on totally
        different scales. Normalize them wrong and one drowns the other.
      </div>
    </div>
  </div>
</section>"""


def slide_framing():
    return """
<section class="slide">
  <div class="head">
    <div class="kicker">04 &nbsp;·&nbsp; FRAMING</div>
    <h2>Constraint satisfaction, then a single fitness</h2>
    <p class="insight">Feasibility first (drive every penalty to zero), then bank
       reward beyond spec &#8212; one scalar <em>F(x)</em>.</p>
  </div>
  <div class="two-col">
    <div class="panel">
      <h3>Raw penalty per metric</h3>
      <div class="eqlist">
        <div class="eqrow"><span class="tag exceed">EXCEED</span>
          <span class="eq">p<sub>i</sub> = max(0,&nbsp; T<sub>i</sub> &#8722; m<sub>i</sub>)</span></div>
        <div class="eqrow"><span class="tag minim">MINIMIZE</span>
          <span class="eq">p<sub>i</sub> = max(0,&nbsp; m<sub>i</sub> &#8722; T<sub>i</sub>)</span></div>
        <div class="eqrow"><span class="tag exact">EXACT</span>
          <span class="eq">p<sub>i</sub> = | m<sub>i</sub> &#8722; T<sub>i</sub> |</span></div>
      </div>
      <p class="muted small">m = measured metric, T = target. Zero penalty = spec met.</p>
    </div>
    <div class="panel">
      <h3>Dual-mode fitness <span class="mono">F(x)</span></h3>
      <div class="modebox infeasible">
        <div class="modelab">while infeasible</div>
        <div class="modeeq">F(x) = &#8722; &#931;<sub>i</sub> P<sub>i</sub>
          &nbsp;<span class="muted small">(push penalties &#8594; 0)</span></div>
      </div>
      <div class="modebox feasible">
        <div class="modelab">once feasible</div>
        <div class="modeeq">F(x) = + reward(x)
          &nbsp;<span class="muted small">(maximize FOM beyond spec)</span></div>
      </div>
      <p class="muted small">Crossing <span class="mono">F = 0</span> means every constraint is met.</p>
    </div>
  </div>
</section>"""


def slide_squash():
    return """
<section class="slide fig-slide" data-fig="squash">
  <div class="head">
    <div class="kicker">05 &nbsp;·&nbsp; METHOD &nbsp;·&nbsp; <span class="live">LIVE</span></div>
    <h2>Score shaping: bound the penalty</h2>
    <p class="insight">Linear (red) <span class="eq-in">P&#770; = p/|T|</span> grows without
       limit &#8212; one outlier dominates. Sigmoid (blue)
       <span class="eq-in">P = 2/(1+e<sup>&#8722;&#945;P&#770;</sup>)&#8722;1</span> saturates at 1.</p>
  </div>
  <div class="figwrap"><div class="plot" id="plot-squash"></div></div>
  <div class="hint">Drag the <b>&#945;</b> slider &#8595; to set how sharply the penalty saturates</div>
</section>"""


def slide_masking():
    return """
<section class="slide fig-slide" data-fig="masking">
  <div class="head">
    <div class="kicker">06 &nbsp;·&nbsp; WHY IT MATTERS &nbsp;·&nbsp; <span class="live">LIVE</span></div>
    <h2>The masking effect</h2>
    <p class="insight">Under linear scoring, a metric just outside spec loses its share of
       the cost as another metric drifts &#8212; its violation is <em>masked</em>. The
       bounded sigmoid keeps it visible to the optimizer.</p>
  </div>
  <div class="figwrap"><div class="plot" id="plot-masking"></div></div>
  <div class="hint">Drag <b>&#945;</b> &#8212; watch the near-feasible metric&#8217;s share hold up under sigmoid, collapse under linear</div>
</section>"""


def slide_casestudy(schematic_b64):
    return f"""
<section class="slide">
  <div class="head">
    <div class="kicker">07 &nbsp;·&nbsp; CASE STUDY</div>
    <h2>Telescopic cascode OTA &#8212; IHP 130&nbsp;nm</h2>
    <p class="insight">14-D design space (W/L + biases). Three engines, same targets,
       a resource-constrained budget.</p>
  </div>
  <div class="case-grid">
    <div class="schematic">
      <img src="data:image/png;base64,{schematic_b64}" alt="Telescopic cascode OTA schematic"/>
      <div class="cap">Improved telescopic cascode OTA, ideal bias (paper Fig.&nbsp;2)</div>
    </div>
    <div class="case-side">
      <table class="spec">
        <thead><tr><th>Metric</th><th>Target</th><th>Type</th></tr></thead>
        <tbody>
          <tr><td>Unity-gain freq.</td><td>&gt; 200 MHz</td><td>max</td></tr>
          <tr><td>DC gain</td><td>&gt; 40 dB</td><td>max</td></tr>
          <tr><td>Input noise</td><td>&lt; 1.2 mV</td><td>min</td></tr>
          <tr class="hl"><td>Supply current</td><td>&lt; 25 &#181;A</td><td>min</td></tr>
          <tr><td>Phase margin</td><td>60 &#177; 10&#176;</td><td>exact</td></tr>
          <tr><td>Settling time</td><td>&lt; 15 &#181;s</td><td>min</td></tr>
        </tbody>
      </table>
      <div class="engines">
        <div class="eng"><span class="dot lhs"></span>LHS baseline <b>12k</b> sims</div>
        <div class="eng"><span class="dot sig"></span>DE <b>2k</b> sims &#8212; the workhorse</div>
        <div class="eng"><span class="dot lin"></span>BFGS <b>2k</b> sims</div>
      </div>
      <p class="muted small">V<sub>DD</sub> 1.5&nbsp;V &nbsp;·&nbsp; C<sub>L</sub> 50&nbsp;fF
        &nbsp;·&nbsp; I<sub>bias</sub> 5&nbsp;&#181;A. Targets competitive with manual designs.</p>
    </div>
  </div>
</section>"""


def slide_convergence():
    return """
<section class="slide fig-slide" data-fig="convergence">
  <div class="head">
    <div class="kicker">08 &nbsp;·&nbsp; RESULT 1 &nbsp;·&nbsp; <span class="live">LIVE</span></div>
    <h2>Same solver, same budget &#8212; only the score shape changed</h2>
    <p class="insight">Sigmoid crosses into feasibility at iter&nbsp;1050 and banks reward.
       Linear <strong>never</strong> reaches a feasible design in 2,000 sims.</p>
  </div>
  <div class="figwrap"><div class="plot" id="plot-convergence"></div></div>
  <div class="hint">Hover the bold best-so-far curves &#8212; crossing <b>F = 0</b> means all constraints met</div>
</section>"""


def slide_outcome():
    return """
<section class="slide fig-slide" data-fig="outcome">
  <div class="head">
    <div class="kicker">09 &nbsp;·&nbsp; RESULT 2 &nbsp;·&nbsp; <span class="live">LIVE</span></div>
    <h2>Sigmoid balances every spec; linear blows the current budget</h2>
    <p class="insight">Linear&#8217;s best maximizes bandwidth &amp; gain but lands at
       <span class="lin-txt">43.7&nbsp;&#181;A &#8212; 1.75&times; over the 25&nbsp;&#181;A budget</span>.
       Sigmoid meets all six specs at <span class="sig-txt">20.6&nbsp;&#181;A</span>. That is the masking effect, made real.</p>
  </div>
  <div class="figwrap"><div class="plot" id="plot-outcome"></div></div>
  <div class="hint">Hover any design in the top-100 clouds &#8212; stars mark each method&#8217;s best</div>
</section>"""


def slide_contours():
    return """
<section class="slide fig-slide" data-fig="contours">
  <div class="head">
    <div class="kicker">10 &nbsp;·&nbsp; RESULT 3 &nbsp;·&nbsp; <span class="live">LIVE</span></div>
    <h2>Why: the equi-score landscape</h2>
    <p class="insight">Linear &#8594; straight, parallel iso-lines dominated by one axis (the
       other is masked). Sigmoid &#8594; a bounded, concentric basin pulling toward the
       feasible corner.</p>
  </div>
  <div class="figwrap"><div class="plot" id="plot-contours"></div></div>
  <div class="hint">Toggle <b>Linear / Sigmoid</b> and drag <b>&#945;</b> &#8212; real visited points overlaid</div>
</section>"""


def slide_distributions():
    return """
<section class="slide fig-slide" data-fig="distributions">
  <div class="head">
    <div class="kicker">11 &nbsp;·&nbsp; RESULT 4 &nbsp;·&nbsp; <span class="live">LIVE</span></div>
    <h2>Where each method spends its simulations</h2>
    <p class="insight">Sigmoid keeps unity-gain-frequency diversity while pulling current
       <em>below</em> 25&nbsp;&#181;A. Linear over-concentrates at high UGF and higher power;
       LHS stalls at the &#8776;5&nbsp;&#181;A sub-threshold bias.</p>
  </div>
  <div class="figwrap"><div class="plot" id="plot-distributions"></div></div>
  <div class="hint">Dashed line = spec target &#8212; hover bars to compare exploration behaviour</div>
</section>"""


def slide_tool():
    return f"""
<section class="slide">
  <div class="head">
    <div class="kicker">12 &nbsp;·&nbsp; THE TOOL</div>
    <h2>SpiceXplorer &#8212; the open framework behind this</h2>
    <p class="insight">Everything you just saw is one YAML config away.</p>
  </div>
  <div class="blockwrap">{BLOCK_SVG}</div>
  <div class="tool-foot">
    <span>A YAML config orchestrates black-box optimizers (Nevergrad / Ax) against SPICE:
      metric extraction &#8594; score shaping &#8594; Pareto / exploration viz.</span>
    <span class="repo">github.com/MacAnalog/SpiceXplorer &nbsp;·&nbsp; open-source</span>
  </div>
</section>"""


def slide_future():
    return """
<section class="slide">
  <div class="head">
    <div class="kicker">13 &nbsp;·&nbsp; WHERE IT&#8217;S GOING</div>
    <h2>Agentic, topology-aware sizing</h2>
  </div>
  <div class="three-col">
    <div class="panel"><div class="bignum sig">01</div><h3>Warm starts</h3>
      <p class="muted">Initialize from circuit theory (g<sub>m</sub>/I<sub>D</sub>) instead of cold random search.</p></div>
    <div class="panel"><div class="bignum maroon">02</div><h3>Constraint synthesis</h3>
      <p class="muted">Auto-derive symmetry and biasing constraints to shrink the feasible search.</p></div>
    <div class="panel"><div class="bignum lhs">03</div><h3>Manager agents</h3>
      <p class="muted">Multi-fidelity orchestration: cheap screens first, full SPICE where it counts.</p></div>
  </div>
</section>"""


def slide_conclusion():
    return """
<section class="slide conclusion">
  <div class="head">
    <div class="kicker">14 &nbsp;·&nbsp; CONCLUSION</div>
    <h2>Formulation is a first-class lever</h2>
  </div>
  <div class="concl-grid">
    <div class="concl-card sig-card">
      <div class="ck">Constraint satisfaction</div>
      <div class="cv">Sigmoid met <b>all 6 specs</b>; linear met <b>0/2000</b></div>
    </div>
    <div class="concl-card maroon-card">
      <div class="ck">Power</div>
      <div class="cv"><b>20.6 &#181;A</b> vs 43.7 &#181;A &#8212; ~2&times; lower</div>
    </div>
    <div class="concl-card lhs-card">
      <div class="ck">Same solver &amp; budget</div>
      <div class="cv">Only the <b>score shape</b> changed</div>
    </div>
  </div>
  <div class="thanks">
    <h3>Thank you &#8212; questions?</h3>
    <p class="muted">Danial Noori Zadeh &nbsp;·&nbsp; MacAnalog, McMaster University
       &nbsp;·&nbsp; github.com/MacAnalog/SpiceXplorer</p>
  </div>
</section>"""


# ---------------------------------------------------------------- presenter notes
NOTES = [
    "Title. 'Today: why the shape of your score function decides whether automated sizing succeeds.'",
    "Speaker + the one message. Say the thesis out loud; everything else serves it.",
    "Problem: multi-objective, application-dependent. The gap is the score function, not the solver.",
    "Framing: feasibility first (drive penalties to 0), then reward. One scalar F(x). Crossing 0 = feasible.",
    "LIVE squashing. Drag alpha. Point: linear is unbounded, sigmoid saturates at 1 -> balance beats peaks.",
    "LIVE masking. The near-feasible metric's cost share collapses under linear as another metric drifts.",
    "Case study: telescopic OTA, IHP 130nm, 14-D. Note the 25 uA current budget specifically.",
    "RESULT 1 convergence. Same solver, same budget. Sigmoid feasible @1050; linear never feasible.",
    "RESULT 2 outcome. Linear 43.7 uA (1.75x over); sigmoid 20.6 uA meets all. This IS the masking effect.",
    "RESULT 3 landscape. Linear = parallel iso-lines (one axis masks the other); sigmoid = concentric basin.",
    "RESULT 4 exploration. Sigmoid keeps UGF diversity at low power; linear over-concentrates; LHS stalls.",
    "Tool. One YAML config away. Open-source. Invite people to try it.",
    "Future: warm starts, constraint synthesis, manager agents. 3 bullets, keep moving.",
    "Conclusion. Formulation is a lever: constraint satisfaction where linear failed, ~2x lower power, open tool.",
]


# ---------------------------------------------------------------- assemble
def build_html(figs: dict, schematic_b64: str, plotlyjs: str) -> str:
    slides = [
        slide_title(),
        slide_speaker(),
        slide_problem(),
        slide_framing(),
        slide_squash(),
        slide_masking(),
        slide_casestudy(schematic_b64),
        slide_convergence(),
        slide_outcome(),
        slide_contours(),
        slide_distributions(),
        slide_tool(),
        slide_future(),
        slide_conclusion(),
    ]
    slides_html = "\n".join(slides)
    figs_json = json.dumps(figs)
    notes_json = json.dumps(NOTES)

    return (
        DECK_TEMPLATE
        .replace("/*__PLOTLYJS__*/", plotlyjs)
        .replace("/*__FIGS__*/", figs_json)
        .replace("/*__NOTES__*/", notes_json)
        .replace("<!--__SLIDES__-->", slides_html)
    )


DECK_TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"/>
<title>Score Shaping &amp; Pareto Optimality &#8212; NEWCAS 2026</title>
<style>
:root{
  --maroon:#7A003C; --maroon-d:#5e002e; --sig:#2563eb; --lin:#dc2626; --lhs:#16a34a;
  --ink:#111827; --muted:#6b7280; --line:#e5e7eb; --panel:#f8fafc;
}
*{box-sizing:border-box;}
html,body{margin:0;height:100%;background:#1f2937;font-family:Inter,'Segoe UI',Helvetica,Arial,sans-serif;color:var(--ink);overflow:hidden;}
#stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;}
#deck{position:relative;width:100vw;height:100vh;max-width:177.78vh;max-height:56.25vw;background:#fff;
  box-shadow:0 0 60px rgba(0,0,0,.5);overflow:hidden;}
.slide{position:absolute;inset:0;padding:4.2vh 4.4vw;display:none;flex-direction:column;background:#fff;}
.slide.active{display:flex;}

/* heading */
.head{flex:0 0 auto;margin-bottom:1.4vh;}
.kicker{font-size:1.55vh;font-weight:700;letter-spacing:.16em;color:var(--maroon);text-transform:uppercase;margin-bottom:.6vh;}
.kicker.maroon{color:var(--maroon);}
h1{font-size:5.4vh;line-height:1.08;margin:.4vh 0 1.6vh;font-weight:800;letter-spacing:-.01em;}
h2{font-size:3.7vh;line-height:1.1;margin:.2vh 0;font-weight:800;letter-spacing:-.01em;color:var(--ink);}
h3{font-size:2.3vh;margin:0 0 .8vh;font-weight:700;}
.head h2{border-bottom:none;}
.head::after{content:"";display:block;width:5.5vw;height:.5vh;background:var(--maroon);border-radius:2px;margin-top:1.1vh;}
.insight{font-size:2.05vh;line-height:1.4;color:#374151;margin:1.2vh 0 0;max-width:92%;}
.live{display:inline-block;background:var(--sig);color:#fff;font-size:1.2vh;font-weight:800;letter-spacing:.12em;
  padding:.25vh .7vh;border-radius:4px;vertical-align:middle;}
.muted{color:var(--muted);} .small{font-size:1.6vh;} .mono{font-family:ui-monospace,Menlo,Consolas,monospace;}
em{font-style:italic;color:var(--maroon);font-weight:600;} u{text-decoration-color:var(--maroon);}

/* figure slides */
.fig-slide .figwrap{flex:1 1 auto;min-height:0;position:relative;}
.plot{position:absolute;inset:0;width:100%;height:100%;}
.hint{flex:0 0 auto;margin-top:.8vh;font-size:1.7vh;color:var(--muted);text-align:center;}
.hint b{color:var(--ink);}
.eq-in{font-family:ui-monospace,Menlo,Consolas,monospace;background:var(--panel);padding:.1vh .5vh;border-radius:4px;font-size:.92em;}

/* title slide */
.title-slide{padding:0;}
.title-bar{position:absolute;left:0;top:0;bottom:0;width:1.4vw;background:linear-gradient(var(--maroon),var(--maroon-d));}
.title-body{margin:auto 6vw;max-width:80%;}
.subtitle{font-size:2.6vh;color:#374151;line-height:1.4;margin:.5vh 0 4vh;max-width:80%;}
.title-meta{font-size:2.1vh;line-height:1.5;}
.brandmark{position:absolute;left:6vw;bottom:5vh;display:flex;align-items:center;gap:1.2vw;}
.bm-main{font-family:Georgia,'Times New Roman',serif;font-size:2.6vh;font-weight:700;color:var(--maroon);letter-spacing:-.01em;}
.bm-u{font-weight:400;}
.bm-div{width:2px;height:3vh;background:#bbb;}
.bm-eng{font-size:2.4vh;font-weight:800;color:var(--maroon);letter-spacing:.02em;}

/* columns / panels */
.two-col{flex:1;display:grid;grid-template-columns:1fr 1fr;gap:2.4vw;min-height:0;}
.three-col{flex:1;display:grid;grid-template-columns:1fr 1fr 1fr;gap:2vw;min-height:0;align-items:stretch;}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:2.4vh 1.8vw;display:flex;flex-direction:column;}
.panel.accent{background:linear-gradient(150deg,#fff,#fdf2f7);border-color:#f3cfe0;}
.ticks{list-style:none;margin:.6vh 0 0;padding:0;}
.ticks li{position:relative;padding-left:1.5vw;margin-bottom:1.3vh;font-size:2.0vh;line-height:1.38;}
.ticks li::before{content:"";position:absolute;left:0;top:.9vh;width:.7vw;height:.7vw;max-width:11px;max-height:11px;
  background:var(--maroon);border-radius:3px;}
.callout{margin-top:auto;padding:1.6vh 1.4vw;border-radius:10px;font-size:1.85vh;line-height:1.4;}
.lin-callout{background:#fef2f2;border-left:5px solid var(--lin);color:#7f1d1d;}
.bignum{font-size:6vh;font-weight:800;line-height:1;margin-bottom:1vh;}
.maroon{color:var(--maroon);} .sig{color:var(--sig);} .lin{color:var(--lin);} .lhs{color:var(--lhs);}
.big-claim{font-size:2.1vh;font-weight:700;margin:.2vh 0 1vh;}
.thesis{font-size:2.35vh;line-height:1.42;color:#1f2937;margin:0;}
.thesis strong{color:var(--maroon);}

/* equations */
.eqlist{margin-top:1vh;}
.eqrow{display:flex;align-items:center;gap:1vw;margin-bottom:1.8vh;}
.tag{font-size:1.4vh;font-weight:800;letter-spacing:.08em;padding:.5vh .8vw;border-radius:6px;color:#fff;min-width:8vw;text-align:center;}
.tag.exceed{background:var(--sig);} .tag.minim{background:var(--lin);} .tag.exact{background:var(--maroon);}
.eq{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:2.3vh;}
.modebox{border-radius:12px;padding:1.6vh 1.4vw;margin-bottom:1.4vh;}
.modebox.infeasible{background:#fef2f2;border:1px solid #fca5a5;}
.modebox.feasible{background:#eff6ff;border:1px solid #bfdbfe;}
.modelab{font-size:1.5vh;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:.6vh;}
.modeeq{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:2.3vh;}

/* case study */
.case-grid{flex:1;display:grid;grid-template-columns:1.25fr 1fr;gap:2.2vw;min-height:0;}
.schematic{background:#fff;border:1px solid var(--line);border-radius:14px;padding:1.6vh 1vw;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:0;}
.schematic img{max-width:100%;max-height:88%;object-fit:contain;}
.schematic .cap{font-size:1.5vh;color:var(--muted);margin-top:1vh;text-align:center;}
.case-side{display:flex;flex-direction:column;}
table.spec{width:100%;border-collapse:collapse;font-size:1.85vh;}
table.spec th{text-align:left;color:var(--muted);font-weight:700;font-size:1.5vh;text-transform:uppercase;letter-spacing:.06em;border-bottom:2px solid var(--line);padding:.7vh .5vw;}
table.spec td{padding:.7vh .5vw;border-bottom:1px solid var(--line);}
table.spec tr.hl td{background:#fdf2f7;font-weight:700;color:var(--maroon);}
.engines{margin-top:1.4vh;display:flex;flex-direction:column;gap:.8vh;}
.eng{font-size:1.9vh;display:flex;align-items:center;gap:.8vw;}
.dot{width:1vw;height:1vw;max-width:14px;max-height:14px;border-radius:50%;display:inline-block;}
.dot.sig{background:var(--sig);} .dot.lin{background:var(--lin);} .dot.lhs{background:var(--lhs);}

/* tool / block diagram */
.blockwrap{flex:1;display:flex;align-items:center;justify-content:center;min-height:0;padding:1vh 0;}
.blocksvg{width:100%;height:100%;max-height:62vh;}
.bx{fill:#fff;stroke:var(--line);stroke-width:1.5;}
.bx-core{fill:#fafafa;stroke:#d1d5db;stroke-dasharray:6 5;}
.bx-cfg{fill:#f3f4f6;stroke:#9ca3af;}
.bx-opt{fill:#eff6ff;stroke:var(--sig);} .bx-spice{fill:#f0fdf4;stroke:var(--lhs);}
.bx-score{fill:#fdf2f7;stroke:var(--maroon);stroke-width:2;}
.bx-viz{fill:#f5f3ff;stroke:#7c3aed;}
.bt{font-family:Inter,sans-serif;text-anchor:middle;fill:var(--ink);}
.bt-core{font-size:15px;font-weight:800;fill:#6b7280;letter-spacing:.04em;}
.bt-h{font-size:16px;font-weight:800;} .bt-s{font-size:13px;fill:#6b7280;}
.bt-mini{font-size:11px;fill:#9ca3af;font-style:italic;}
.bt-lin{font-size:14px;fill:var(--lin);font-family:ui-monospace,Menlo,monospace;}
.bt-sig{font-size:14px;fill:var(--sig);font-family:ui-monospace,Menlo,monospace;}
.arrow{stroke:var(--maroon);stroke-width:2.5;marker-end:url(#ar);}
.arrow-b{stroke:var(--sig);stroke-width:2.5;marker-end:url(#arb);}
.tool-foot{flex:0 0 auto;display:flex;justify-content:space-between;align-items:center;gap:2vw;font-size:1.85vh;color:#374151;margin-top:1vh;}
.tool-foot .repo{font-weight:700;color:var(--maroon);white-space:nowrap;}

/* conclusion */
.concl-grid{flex:0 0 auto;display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.8vw;margin:1vh 0 2vh;}
.concl-card{border-radius:14px;padding:2.4vh 1.6vw;color:#fff;}
.sig-card{background:linear-gradient(150deg,var(--sig),#1e40af);}
.maroon-card{background:linear-gradient(150deg,var(--maroon),var(--maroon-d));}
.lhs-card{background:linear-gradient(150deg,var(--lhs),#15803d);}
.ck{font-size:1.55vh;font-weight:700;letter-spacing:.08em;text-transform:uppercase;opacity:.9;margin-bottom:1vh;}
.cv{font-size:2.5vh;line-height:1.25;font-weight:600;}
.thanks{margin-top:auto;border-top:2px solid var(--line);padding-top:2vh;}
.thanks h3{font-size:3vh;color:var(--maroon);margin-bottom:.6vh;}
.lin-txt{color:var(--lin);font-weight:700;} .sig-txt{color:var(--sig);font-weight:700;}

/* chrome: progress, counter, nav, notes */
#bar{position:fixed;left:0;top:0;height:5px;background:var(--maroon);z-index:50;transition:width .25s;}
#counter{position:fixed;right:14px;bottom:10px;z-index:50;font-size:13px;color:#9ca3af;background:rgba(255,255,255,.85);
  padding:3px 9px;border-radius:20px;font-weight:600;}
#nav{position:fixed;right:14px;bottom:38px;z-index:50;display:flex;gap:6px;}
#nav button{width:34px;height:34px;border:none;border-radius:50%;background:rgba(255,255,255,.9);color:var(--maroon);
  font-size:17px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.2);}
#nav button:hover{background:#fff;}
#notes{position:fixed;left:0;right:0;bottom:0;z-index:60;background:rgba(17,24,39,.95);color:#f3f4f6;
  padding:14px 22px;font-size:16px;line-height:1.45;display:none;}
#notes.show{display:block;}
#notes b{color:#fbbf24;}
#help{position:fixed;left:14px;bottom:10px;z-index:50;font-size:12px;color:#9ca3af;background:rgba(255,255,255,.85);
  padding:3px 9px;border-radius:20px;}
@media print{body{overflow:visible;} #deck{box-shadow:none;}}
</style></head>
<body>
<div id="bar"></div>
<div id="stage"><div id="deck">
<!--__SLIDES__-->
</div></div>
<div id="nav"><button id="prev" title="Previous">&#8249;</button><button id="next" title="Next">&#8250;</button></div>
<div id="counter"><span id="cur">1</span> / <span id="tot">1</span></div>
<div id="help">&#8592;/&#8594; navigate &nbsp;·&nbsp; F fullscreen &nbsp;·&nbsp; N notes</div>
<div id="notes"></div>

<script>/*__PLOTLYJS__*/</script>
<script>
const FIGS = /*__FIGS__*/;
const NOTES = /*__NOTES__*/;
const PCONF = {responsive:true, displaylogo:false, displayModeBar:false,
  toImageButtonOptions:{format:'svg',scale:2}};
const slides = Array.from(document.querySelectorAll('.slide'));
const drawn = {};
let i = 0;
document.getElementById('tot').textContent = slides.length;

function drawFig(slide){
  const id = slide.dataset.fig;
  if(!id || drawn[id]) return;
  const el = slide.querySelector('.plot');
  const spec = FIGS[id];
  Plotly.newPlot(el, spec.data, spec.layout, PCONF).then(()=>{ Plotly.Plots.resize(el); });
  drawn[id] = true;
}
function resizeCurrent(){
  const s = slides[i];
  if(s.dataset.fig && drawn[s.dataset.fig]){
    const el = s.querySelector('.plot');
    if(el) Plotly.Plots.resize(el);
  }
}
function show(n){
  i = Math.max(0, Math.min(slides.length-1, n));
  slides.forEach((s,k)=> s.classList.toggle('active', k===i));
  document.getElementById('cur').textContent = i+1;
  document.getElementById('bar').style.width = ((i+1)/slides.length*100)+'%';
  const nt = document.getElementById('notes');
  nt.innerHTML = '<b>Slide '+(i+1)+'.</b> ' + (NOTES[i]||'');
  drawFig(slides[i]);
  // a couple of delayed resizes to settle layout/fonts
  requestAnimationFrame(resizeCurrent);
  setTimeout(resizeCurrent, 120);
  location.hash = i+1;
}
function next(){ show(i+1); } function prev(){ show(i-1); }

document.getElementById('next').onclick = next;
document.getElementById('prev').onclick = prev;
document.addEventListener('keydown', e=>{
  if(['ArrowRight','PageDown',' ','Spacebar'].includes(e.key)){ e.preventDefault(); next(); }
  else if(['ArrowLeft','PageUp'].includes(e.key)){ e.preventDefault(); prev(); }
  else if(e.key==='Home'){ show(0); } else if(e.key==='End'){ show(slides.length-1); }
  else if(e.key==='f'||e.key==='F'){ if(!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen(); }
  else if(e.key==='n'||e.key==='N'){ document.getElementById('notes').classList.toggle('show'); }
});
window.addEventListener('resize', resizeCurrent);
document.addEventListener('fullscreenchange', ()=> setTimeout(resizeCurrent,150));
const start = parseInt((location.hash||'#1').slice(1)) || 1;
show(start-1);
</script>
</body></html>"""


def main():
    print("building figures ...")
    figs = build_figures()
    schematic = b64(os.path.join(HERE, "assets", "fig2_ota_v2.png"))
    print("loading plotly bundle ...")
    plotlyjs = get_plotlyjs()
    html = build_html(figs, schematic, plotlyjs)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(html)
    print(f"wrote {OUT}  ({len(html)/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
