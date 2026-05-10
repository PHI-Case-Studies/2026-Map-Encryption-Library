# CLAUDE.md — AI Contributor Guide

This file is read automatically by Claude Code at the start of every session.
It describes project conventions, known pitfalls, and effective prompt patterns
for AI-assisted development of this repository.

---

## Project overview

A seventeen-notebook computational geoprivacy research framework built around a
four-step geographic coordinate encryption pipeline (Project → Snap+Shuffle →
Lock → Wobble). The notebooks progress from cryptographic primitives (NB01–NB05)
through a complete system (NB06–NB10), advanced spatial evaluation (NB11–NB13),
dataset augmentation for three public health scenarios (NB14–NB16), and
adversarial re-identification experiments (NB17). Future notebooks (NB18+) are
planned in TODO.md.

All notebooks are self-contained and executable in order using the `crypto` conda
environment defined in `environment.yml`.

---

## Repository structure

```
map_encryption/         Python package — core library
  __init__.py           All crypto logic and public API (was map_encryption.py)
  viz.py                Shared visualisation utilities (was map_viz.py)
geoprivacy/             Separate package — donut geomasking and hex-grid binning
  __init__.py
  donut_geomask.py
  data_geomask.py
  geomask_eval.py
  geomaskedpoint.py
  hexgrid.py
data/                   CSV and GeoJSON datasets for all scenarios
NN-title.ipynb          Notebooks numbered 01–17
environment.yml         Conda environment spec (Python 3.10, crypto env)
NOTEBOOKS.md            Narrative guide and reading paths
TODO.md                 Research roadmap with completion status
```

`map_encryption/` and `geoprivacy/` are intentionally separate packages.
Do not merge them. New shared visualisation helpers belong in `map_encryption/viz.py`.

---

## Notebook formatting conventions

Every notebook must follow this exact cell structure:

### Cell 0 — title (markdown)
```markdown
# Notebook N — Short Title
## Longer Subtitle Describing the Topic

One paragraph explaining what this notebook covers, what it builds on, and
why it matters in the research arc.

**Three-part structure:**   (or however many parts)

- **Part 1** — ...
- **Part 2** — ...
- **Part 3** — ...
```

### Cell 1 — imports (code)
Standard imports only; no computation. Follow existing notebooks for ordering
(stdlib → numpy/pandas → matplotlib/seaborn → spatial libs → map_encryption).

### Cell 2+ — section headers (markdown) then code
Each major section starts with a markdown cell:
```markdown
---
## N.M  Section Title

One paragraph describing what this section demonstrates.
```

The `---` horizontal rule before every `##` section header is required.

### Figure caption cells
Every code cell that calls `plt.show()` must be immediately followed by a
markdown caption cell:
```markdown
**Figure Na** — One sentence describing axes and what the reader should notice.
Key findings stated explicitly (e.g., "jitter-only: 87 %, full pipeline: 0 %").
```

### Table caption cells
Every `show_md_table()` call must include a title argument:
```python
show_md_table(df, 'Table Na — Descriptive title')
```

### Cell ID naming
Use the pattern `nb{NN}c{00}` — two-digit notebook number, two-digit cell
sequence, zero-padded. Examples: `nb17c00`, `nb17c01`, `nb17c04_cap`.
Suffix `_cap` for caption cells, `_title` for the title cell, `_hdr` for
section header cells that are not part of the main sequence.

### Subplot titles
Use the **health condition** (Cholera, Drug Overdose, Respiratory / Environmental),
never the place name (Philadelphia, Houston). This applies to `ax.set_title()`,
`ax.set_xticklabels()`, and any Scenario column in a table.

---

## Generator script pattern

Notebooks are created via a `_gen_nbNN.py` generator script rather than
directly in JupyterLab, to avoid "file modified since read" conflicts.

**Workflow:**
```bash
python3 _gen_nbNN.py                        # write the .ipynb file
/opt/homebrew/Caskroom/miniforge/base/envs/crypto/bin/jupyter nbconvert \
  --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=300 \
  NN-title.ipynb
rm _gen_nbNN.py                             # delete generator after success
git add NN-title.ipynb
```

**Always use the full path to the crypto env Python/Jupyter** —
`conda run -n crypto` resolves to the system Python on this machine:
```bash
# Wrong:
conda run -n crypto python3 script.py
# Right:
/opt/homebrew/Caskroom/miniforge/base/envs/crypto/bin/python script.py
/opt/homebrew/Caskroom/miniforge/base/envs/crypto/bin/jupyter nbconvert ...
```

### Known pitfalls in generator scripts

**1. Triple-quote conflict** — `f"""..."""` inside `code("""\...""")` terminates
the outer string at the first `"""` inside the cell source. Fixes:
- Use `f'''...'''` (triple single-quotes) for f-strings inside cell source
- Or use string concatenation: `"part1" + f"part2{var}" + "part3"`
- Never use `"""docstrings"""` inside a `code("""\...""")` block — use `#` comments

**2. Duplicate column names after rename** — if a DataFrame already has `LAT`
and you rename `LAT_snapped` to `LAT`, pandas creates two columns both named
`LAT`; `df['LAT']` then returns a DataFrame (shape N×2) not a Series:
```python
# Wrong:
df = df.rename(columns={'LAT_snapped': 'LAT'})
# Right:
df = df.drop(columns=['LAT', 'LON']).rename(columns={'LAT_snapped': 'LAT', 'LON_snapped': 'LON'})
```

**3. `groupby` with a list of Series as keys** — passing
`[df['col1'].round(6), df['col2'].round(6)]` as a groupby key raises
`ValueError: Grouper not 1-dimensional`. Use string concatenation instead:
```python
df['loc_id'] = pd.factorize(
    df['LAT'].round(6).astype(str) + ',' + df['LON'].round(6).astype(str))[0]
```

**4. Unicode in generator source strings** — characters like `±`, `≤`, `–`
inside bare Python source strings cause `SyntaxError: invalid character`.
Either escape them (`+/-`, `<=`, `--`) or encode them with `chr()`:
```python
f"offset {chr(177)}{J:.0f} m"   # ±
```

**5. Docstrings inside cell source strings** — triple-quoted docstrings inside
`code("""\...""")` will terminate the outer string. Use `#` comments for any
inline documentation in generated cell source.

---

## Visualisation conventions

**No Plotly.** All charts use matplotlib/seaborn. Plotly 6.x is incompatible
with the JupyterLab extension bundled on conda-forge (max version 1.0.0).

**Colour palette for scenarios:**
- Cholera: `#1f77b4` (blue)
- Drug Overdose: `#ff7f0e` (orange)
- Respiratory / Environmental: `#2ca02c` (green)

**Colour palette for conditions:**
- Jitter-only: `#ff7f0e` (orange)
- Full pipeline: `#2ca02c` (green)

**Maps:** Use `folium` with `cartodbpositron` tiles (not the default OpenStreetMap).

**Shared helpers** in `map_encryption/viz.py`:
- `plot_demographic_bar(acs, title, annotation_x, figsize)` — horizontal grouped
  seaborn bar for racial/ethnic composition + poverty annotation
- `show_md_table(df, title)` — render a DataFrame as a markdown table

---

## Library conventions

**Importing from `map_encryption`:**
```python
from map_encryption import MapEncryption, SchemeParams, _project, _unproject
from map_encryption.viz import plot_demographic_bar, show_md_table
```

**Instantiating `MapEncryption`** — key comes first, then params:
```python
import secrets
MASTER_KEY = secrets.token_bytes(32)
params = SchemeParams(bin_size_m=250, jitter_max_frac=0.25)
enc = MapEncryption(MASTER_KEY, params)
```

**Encoding and display:**
```python
record = enc.encode(lat, lon)          # returns dict with qxp, qyp, nonce, ct_resid
display_lat, display_lon = enc.render_coordinates(record)
```

The PRP tile shuffle relocates display coordinates to a pseudorandom global
location (potentially a different continent). Do not assume display coordinates
are geographically near the original.

---

## Effective AI prompt patterns

### Adding a new notebook

> "Write a generator script `_gen_nbNN.py` that creates `NN-title.ipynb`.
> The notebook should cover [topic]. It depends on [prior notebooks] and uses
> data from [files]. The narrative structure is:
> - Part 1: [description] — Figure Na shows [what]
> - Part 2: [description] — Table Na shows [what]
> Follow the formatting conventions in CLAUDE.md: title cell first, `---` before
> each section, caption cell after every figure, health condition labels not
> place names. Use `map_encryption` and `map_encryption.viz` imports."

### Patching a specific cell

> "In `NN-title.ipynb`, cell `nbNNcXX` currently does [X]. Replace it with
> [Y]. The cell computes [Z] and the output should show [W].
> Clear outputs and re-execute the notebook after patching."

### Converting a Plotly chart to matplotlib

> "Cell `nbNNcXX` in `NN-title.ipynb` uses `px.bar(...)`. Replace it with an
> equivalent `plt.bar()` / `sns.barplot()` chart. Keep the same title, axis
> labels, and data. Remove the `import plotly.express as px` line from the
> imports cell `nbNNcYY`."

### Adding a figure caption

> "Insert a markdown caption cell with id `nbNNcXX_cap` immediately after cell
> `nbNNcXX` in `NN-title.ipynb`. The figure shows [what the axes are, what the
> key finding is]. Follow the **Figure Na** — sentence format from CLAUDE.md."

### Updating documentation after adding a notebook

> "Update `NOTEBOOKS.md` to add NB[N] to the overview table, add a per-notebook
> description paragraph, and update the sequential reading path. Update `TODO.md`
> to mark NB[N] as done with a brief findings summary. Update `README.md` Files
> table to list the new notebook file."

---

## Pain points and curation recommendations

**Notebook file size** — NB15 (`15-substance-use-scenario.ipynb`) is ~61 MB
due to embedded Folium map HTML with 108,183 building footprint polygons.
GitHub warns but accepts files up to 100 MB. If this causes CI or clone issues,
consider clearing map cell outputs before commit with:
```bash
jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace NN-title.ipynb
```

**Re-execution after patching** — always re-execute the full notebook after any
cell patch, not just the patched cell. Variable state dependencies can cause
silent errors. Use `--ExecutePreprocessor.timeout=600` for notebooks with
Overpass API calls or Monte Carlo sweeps (NB13, NB14, NB15, NB16).

**Data provenance** — NB14, NB15, NB16 use synthetic data parameterised from
real public health reports. When adding new scenarios, document the source for
each parameter (incident counts, age distributions, substance proportions) in
a data provenance section at the end of the notebook, following NB14's format.

**Scenario labels** — use health condition names, not place names, in all
figure titles, subplot headings, table Scenario columns, and x-axis tick labels.
The mapping is: Cholera → Cholera, Philadelphia → Drug Overdose,
Houston → Respiratory / Environmental.

**Overpass API caching** — NB14, NB15, NB16 fetch OSM building footprints via
the Overpass API and cache results to `data/*.geojson`. If the cache file exists,
the fetch is skipped. Do not delete cached GeoJSON files unnecessarily — the
Overpass API has rate limits and large fetches take 5–15 minutes.

**Three-scenario consistency** — any metric or attack introduced for one scenario
should be applied to all three (Cholera, Drug Overdose, Respiratory/Environmental)
so readers can compare across contexts. NB17 is the reference for this pattern.
