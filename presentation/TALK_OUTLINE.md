# NEWCAS 2026 — Talk Scaffold

**Paper:** Score Shaping and Pareto Optimality in Analog IC Design Automation
**Speaker:** Danial Noori Zadeh · MacAnalog, McMaster University
**Slot:** Monday June 22, 2026 · Lecture · **12 min talk + 3 min Q&A** (hard limit)
**Format rules (from NEWCAS guidelines):** PPTX or PDF, filename = *paper number*, Windows-standard fonts only, **no embedded video** (animations must auto-run; the venue laptop runs your file). Bring it on a USB and a backup.

---

## 1. Design intent

The submitted deck title is broad ("Accelerating Analog IC Design with AI"). For a 12-minute paper talk that is too wide. This scaffold narrows to **one message**:

> **Problem formulation matters as much as the solver. A bounded (sigmoid) score function meets every spec where the unbounded (linear) baseline silently violates the current budget — and finds ~2x lower-power designs.**

Everything earns its place by serving that message. The GNN / RL / agentic survey material from the original deck moves to **backup** (appendix), pulled up only if a Q&A question invites it.

### Timing budget (12 min)

| Segment | Slides | Time |
|---|---|---|
| Hook + problem | 1–3 | 2.0 min |
| Method (score shaping) | 4–6 | 3.0 min |
| Case study + results | 7–10 | 4.5 min |
| Tool + future + close | 11–14 | 2.5 min |

Rule of thumb: ~50 s/slide. If you overrun, the results slides (8–10) are where you compress, not the method (4–6).

---

## 2. Slide-by-slide

Legend — **[FIG]** = figure on slide · **NOTE** = speaker cue (1 breath) · existing slide # refers to the original 37-slide deck.

### Slide 1 — Title  *(0:20)*
- Title, your name, affiliation, paper number, NEWCAS 2026.
- **NOTE:** "Today: why the *shape* of your score function decides whether automated sizing succeeds."
- *(from existing slide 1)*

### Slide 2 — Speaker / group  *(0:20)*
- Your bio block + MacAnalog. Keep tight.
- *(from existing slide 4 — kept per your request)*

### Slide 3 — The problem: sizing is a constrained trade-off  *(1:20)*
- Analog specs are multi-objective and *application-dependent*; FOM maximization under hard constraints.
- The gap: research over-fixates on the *solver*; the *score function* is under-studied. An ill-shaped objective stalls even a strong optimizer.
- **NOTE:** "A 500 MHz bandwidth error and a 100% power error live on totally different scales — how you normalize them decides what the optimizer chases."
- *(condense existing slides 7–8; one slide)*

### Slide 4 — Framing: CSP + single-objective fitness  *(1:00)*
- Sizing as search for parameter vector **x** meeting targets **T**. Feasibility first, then maximize FOM (dual-mode `F(x)`, Eq. 3).
- Raw penalties: EXCEED / MINIMIZE / EXACT.
- **[FIG]** small equation block (Eqs. on raw penalty + dual-mode fitness).
- *(from existing slide 19)*

### Slide 5 — Score shaping: linear vs. sigmoid  *(1:30)*
- Linear (Eq. 1): `P̂ = p/S`, unbounded → one far-off metric dominates the cost.
- Sigmoid (Eq. 2): `P = 2/(1+e^(-αP̂)) − 1`, bounded [0,1) → outliers can't dominate; α sets saturation.
- **[FIG]** interactive **squashing curves** (`plots/1_squashing_curves.html`) live, or its PNG fallback.
- **NOTE:** "Bounding the penalty is a *soft feasibility barrier* — balance beats peaks."
- *(from existing slide 20)*

### Slide 6 — Why it matters: the masking effect  *(0:30)*
- Under linear scoring, a metric just outside spec loses its share of the cost as another metric drifts → its violation is *masked*.
- **[FIG]** interactive **masking demo** (`plots/2_masking_demo.html`) or PNG.
- *(new conceptual slide; reuse fig 2)*

### Slide 7 — Case study: telescopic OTA, IHP 130nm  *(1:00)*
- Improved telescopic cascode OTA, ideal bias. 14-D design space (W/L + bias). Targets from Table I: UGF >200 MHz, gain >40 dB, noise <1.2 mV, **I_DD <25 µA**, PM 60±10°, t_settle <15 µs.
- Three engines: LHS baseline (12k sims), **DE** (2k), BFGS (2k). DE is the workhorse.
- **[FIG]** OTA schematic (paper Fig. 2) + compact Table I.
- *(new; pull schematic from paper PDF page 2)*

### Slide 8 — Result 1: convergence  *(1:30)*
- Sigmoid crosses into feasibility (score ≥ 0) and banks reward beyond spec; **linear never reaches feasibility** in 2k sims (0 fully-feasible points in the run). LHS/BFGS stall (excluded).
- **[FIG]** **NEW** `plots/talk/convergence_trace.png` (interactive: `plots/5_convergence_trace.html`).
- **NOTE:** "Same solver, same budget — only the score shape changed."

### Slide 9 — Result 2: the trade-off outcome  *(1:30)*
- Top-100 clouds over LHS baseline. Sigmoid best meets *every* spec at **20.6 µA**; linear best maximizes UGF/gain but lands at **43.7 µA — 1.7x over the 25 µA budget**. Table III side-by-side.
- The linear failure is *exactly* the masking effect: large MHz/dB magnitudes drowned the µA violation.
- **[FIG]** **NEW** `plots/talk/tradeoff_clouds.png` (current-vs-gain, current-vs-UGF, spec-margin bars). Interactive: `plots/3_tradeoff_outcome.html` + `plots/4_equiscore_contours.html`.

### Slide 10 — Result 3: exploration behaviour  *(1:30)*
- Histograms of all visited designs. Sigmoid keeps **UGF diversity** while pulling current **below 25 µA**; linear over-concentrates at high UGF and higher current; LHS stalls at the ≈5 µA sub-threshold bias.
- Takeaway: sigmoid explores the *useful* low-power region without over-fitting one metric.
- **[FIG]** **NEW** `plots/talk/metric_distributions.png` (interactive: `plots/6_metric_distributions.html`).

### Slide 11 — SpiceXplorer: the open tool behind this  *(0:50)*
- Python framework: YAML config orchestrates black-box optimizers (Nevergrad / Ax) ↔ SPICE; metric extraction, score calculation, Pareto/exploration viz. Open-source.
- **NOTE:** "Everything you just saw is one config file away — github.com/MacAnalog/SpiceXplorer."
- **[FIG]** SpiceXplorer block diagram (paper Fig. 1).
- *(from existing slide 23)*

### Slide 12 — Future: agentic, topology-aware sizing  *(0:40)*
- Warm-start initialization from circuit theory; constraint synthesis (symmetry, gm/I_D); manager-agent multi-fidelity orchestration.
- Keep to 3 bullets; this is the "where it's going" beat.
- *(condense existing slide 31)*

### Slide 13 — Conclusion  *(0:30)*
- Problem formulation is a first-class lever. Sigmoid shaping: constraint satisfaction where linear failed, **~50% lower power**. Tool is open-source.
- *(from existing slide 34)*

### Slide 14 — Thank you / Q&A  *(0:00)*
- Contact, repo links, paper number.
- *(from existing slide 36)*

---

## 3. Figure inventory

### Reuse from the paper (vector/screenshot from the PDF)
- **Fig. 1** — SpiceXplorer block diagram → Slide 11.
- **Fig. 2** — OTA schematic → Slide 7.
- **Table I** — targets → Slide 7. **Table III** — best-design comparison → Slide 9.
- (Paper Figs. 3–5 are superseded by the cleaner new plots below.)

### New plots generated from your dataset
| File | Slide | Story |
|---|---|---|
| `plots/talk/convergence_trace.png` | 8 | Sigmoid reaches feasibility @ iter 1050; linear never does |
| `plots/talk/tradeoff_clouds.png` | 9 | Sigmoid meets all specs; linear blows 25 µA → 43.7 µA |
| `plots/talk/metric_distributions.png` | 10 | Exploration behaviour: diversity + low power vs. over-concentration |

### Interactive (Plotly) — for live demo / backup
`plots/index.html` launches all six: squashing, masking, trade-off outcome, equi-score landscape, **convergence (new)**, **distributions (new)**. Rebuild with `python build_plots.py`.

> **Interactivity strategy (important):** the venue cannot support embedded HTML/video. **Submit the self-contained PPTX with the static PNGs.** Use the Plotly `index.html` only as a live demo *from your own laptop* if the session chair allows it, or to answer a Q&A "what if α changes?" question. Never make the interactive the critical path.

---

## 4. Backup / appendix (after Slide 14, hidden)
Pull up only if Q&A invites it: Gm/ID method, symbolic tools (SymXplorer), circuits-as-graphs / GNN, RL transfer (GCN-RL, RoSE-Opt), LLM context generation. These are strong but off-message for a 12-min score-shaping talk.

## 5. Pre-flight checklist
- [ ] Rename file to your **paper number**.pptx before USB.
- [ ] Replace any non-Windows fonts in the template with Calibri/Arial; test on a Windows machine.
- [ ] Confirm the 3 new PNGs are embedded (not linked) in the PPTX.
- [ ] Dry-run at 12:00 with a timer; trim Slide 10 first if long.
- [ ] Bring a PDF export as backup.
