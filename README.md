# Score Shaping — interactive talk figures (NEWCAS 2026)

Interactive Plotly figures explaining how the **sigmoid vs. linear** score-shaping
strategy enforces a performance trade-off in the telescopic-OTA case study. Driven by the
*real* SpiceXplorer Differential-Evolution runs.

## Files
| File | Purpose |
|------|---------|
| `score_shaping_plots.ipynb` | **Start here** — renders all 4 figures inline + exports them |
| `score_shaping.py` | penalty / normalization math (Eqs. 1–2) + data loaders |
| `build_plots.py` | the 4 figure builders + HTML/index export |
| `data/` | read-only copies of the run CSVs (sigmoid, linear, LHS + score traces) |
| `plots/` | exported self-contained HTML (`index.html` = launcher) + PNG thumbnails |

## The four figures
1. **Squashing curves** — linear (unbounded) vs. sigmoid (bounded), α slider.
2. **Masking effect** — how one far-off metric hides another's violation under linear scoring.
3. **Trade-off outcome** — spec-margin bars + top-100 clouds; sigmoid meets all specs, linear
   blows the 25 µA current budget (43.7 µA). Mirrors Table III.
4. **Equi-score landscape** — iso-score contours over bandwidth × current; Linear/Sigmoid
   toggle + α slider, with real visited points overlaid.

## Use
```bash
# regenerate the standalone HTML (each works offline — no kernel/internet)
.venv/bin/python build_plots.py
open plots/index.html
```
Present straight from the browser, or embed a single figure in a slide:
```html
<iframe src="4_equiscore_contours.html" width="100%" height="700" frameborder="0"></iframe>
```

The data CSVs were copied (read-only) from
`SpiceXplorer/examples/OTA/cascode/NEWCAS_SUBMISSION_APPENDIX/`; that repo is not modified.
