# CLAUDE.md — AI Contributor Guide

This file is read automatically by Claude Code at the start of every session.
It describes project conventions, known pitfalls, and effective prompt patterns
for AI-assisted development of this repository.

---

## Project overview

A twenty-five-notebook computational geoprivacy research framework built around a
four-step geographic coordinate encryption pipeline (Project → Snap+Shuffle →
Lock → Wobble). The notebooks progress from cryptographic primitives (NB01–NB05)
through a complete system (NB06–NB10), advanced spatial evaluation (NB11–NB13),
dataset augmentation for three public health scenarios (NB14–NB16), adversarial
re-identification experiments and formal analysis (NB17–NB20), and capstone
synthesis (NB21). Future extensions are tracked in TODO.md.

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
NN-title.ipynb          Notebooks numbered 00–21, including Module 0 variants
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

## Cross-AI platform review

Independent review by a second AI system (ChatGPT or equivalent) provides a check
on methodological blind spots that Claude may have. Different models have different
training emphases and tendencies — disagreements between them reliably surface genuine
ambiguity or weakness in the content. This practice has been used on selected notebooks
in this repository and is recommended before publishing any new notebook (NB18+).

**The core rule:** give ChatGPT the content without telling it what Claude said.
Ask for an independent opinion. Do not prime it toward or away from Claude's position.

---

### When to request cross-AI review

- Before finalising a new notebook
- After significant methodological changes to an existing notebook
- When making a strong empirical claim (e.g., "the full pipeline reduces attack
  success to ≈ 0 %")
- When choosing between two analytic approaches and neither has an obvious precedent
  in the existing notebooks

---

### Scope 1 — Overall methodological approach

Submit the README "How It Works" section and the research arc summary from NOTEBOOKS.md.

> "I am building a computational geoprivacy research framework. The pipeline encrypts
> geographic coordinates using a Feistel pseudorandom permutation for tile shuffling
> and ChaCha20-Poly1305 AEAD for sub-tile residual encryption. The notebooks progress
> from cryptographic primitives through full-system evaluation, dataset construction
> for three public health scenarios (cholera / opioid overdose / environmental health),
> and adversarial re-identification experiments.
>
> Please review the overall methodological approach. Specific questions:
> (1) Are there gaps or blind spots in the pipeline design?
> (2) Are there well-established geoprivacy mechanisms that should be compared or
>     discussed but are currently absent?
> (3) Is the progression from primitive cryptography to applied public health
>     scenarios a coherent research arc, or are there missing links?
> (4) Are there methodological concerns with using synthetic parameterised datasets
>     rather than real records for the public health scenarios?
> Respond as a reviewer for a computational social science venue."

---

### Scope 2 — Specific notebook content

Export the notebook as markdown (`jupyter nbconvert --to markdown NN-title.ipynb`)
and paste the relevant sections.

> "Please review the following Jupyter notebook on [topic]. I want feedback on:
> (1) Correctness of the [spatial analysis methods / privacy metrics / cryptographic
>     claims] — are any interpretations wrong or overstated?
> (2) Do the figures and tables support the conclusions drawn in the text?
> (3) Are there missing failure cases, edge cases, or confounds that should be
>     acknowledged?
> (4) Is the narrative clear for a reader with a background in [data science /
>     public health / cryptography] but not necessarily all three?
>
> Do not comment on Python code style. Focus on methodological correctness and
> interpretive accuracy."

---

### Scope 3 — Geospatial data science accuracy

Target this at NB11–NB13 (DGGS, Ripley's K, Moran's I, KDE) and NB17 (k-anonymity).

> "Please review the following spatial statistics methodology for correctness.
> Specific claims to verify:
> (1) [Paste the Ripley's K / Moran's I / Getis-Ord Gi* interpretation text]
>     — is the interpretation of the statistic correct? Are the distance parameters
>     and spatial weight choices justified?
> (2) [Paste the DGGS cell-area regularity comparison] — is the H3 resolution 9
>     area-regularity claim accurate, and is the comparison with Web Mercator tiles fair?
> (3) [Paste the k-anonymity computation] — is the equivalence-class definition
>     correct, and are the QI levels appropriate for the sensitivity of each dataset?
>
> Respond as a reviewer with expertise in spatial statistics and location privacy."

---

### Scope 4 — Adversarial experiment design

Target this at NB17 before publishing any new adversarial notebook (NB18+).

> "The following notebook runs three re-identification attacks against encrypted
> geographic health records: (1) quasi-identifier k-anonymity analysis, (2) a
> nearest-record spatial attack using a KD-tree, and (3) a compound geographic-
> proximity + QI attack with a 500 m radius. Two protection regimes are compared:
> additive jitter-only (±62.5 m) and a full cryptographic pipeline (PRP tile shuffle
> + AEAD). [Paste the adversary model table and attack results.]
>
> Please evaluate:
> (1) Are the three attack classes representative of real-world re-identification
>     threats for location health data, or are important threat types missing?
> (2) Is the jitter-only baseline a fair comparator for the full pipeline?
> (3) Are the attack success metrics (fraction of records where nearest original
>     record == true record; fraction with exactly 1 QI+proximity match) the right
>     operationalisation of re-identification risk?
> (4) Are the conclusions appropriately hedged given that the datasets are synthetic?"

---

### Scope 5 — Map and visualisation quality

Export Folium maps as screenshots (browser → Save as PNG) and include matplotlib
figures. Paste code if ChatGPT needs context.

> "Please review the following maps and charts from a data visualisation perspective.
> (1) [Folium maps] — are the tile layer, zoom level, colour scheme, and legend
>     choices appropriate for the data? Are there readability issues?
> (2) [matplotlib/seaborn figures] — are axis labels, titles, and annotations
>     sufficient for a reader who has not read the surrounding notebook text?
> (3) Are colour choices accessible to readers with common colour vision deficiencies
>     (deuteranopia, protanopia)?
> (4) Are the figure captions informative enough to stand alone?
>
> Do not suggest switching to a different plotting library."

---

### Conflict resolution

When Claude and ChatGPT give different guidance:

1. **Document the disagreement** — note what each system said and on which specific
   claim they differ. Do not silently adopt one position.
2. **A human domain expert decides** — neither AI defers to the other automatically.
   The human author reviews both positions and makes the final call.
3. **If no human is immediately available** — take the more conservative position
   (smaller claim, wider uncertainty interval, additional caveat) until the
   disagreement can be reviewed.
4. **Record the resolution** — add a comment in the relevant commit message or
   notebook prose noting that a cross-AI disagreement existed and how it was resolved.

---

### What cross-AI review cannot replace

- Human expert verification of **references** (both AIs hallucinate citations)
- Human authorship of **learning objectives** (requires curriculum design intent)
- Domain expert review of **glossary definitions** (requires technical accuracy check)
- **Code execution** — ChatGPT cannot run the notebooks; only Claude Code (in this
  environment) or `jupyter nbconvert --execute` can verify that code runs correctly
- **Data provenance** — neither AI can verify that synthetic data parameters match
  the cited primary sources; a human must check each claim against the original report

---

## Content that requires human authorship and verification

The following three content types must be written or verified by a human expert.
Do not generate them autonomously. If asked to produce any of these, draft a
placeholder and flag it explicitly for human review.

### Learning objectives

Learning objectives encode the pedagogical intent of a notebook — what a reader
should be able to do after completing it. They reflect curriculum design decisions
that depend on the intended audience, prior knowledge assumptions, and assessment
context. AI can suggest candidate objectives based on notebook content, but the
final wording must be approved by the course designer. Do not add a learning
objectives section to any notebook without explicit human instruction.

### References and citations

All bibliographic references in this repository were selected and verified by a
human researcher. AI language models hallucinate plausible-sounding but non-existent
citations, including fabricated DOIs, incorrect author lists, wrong publication
years, and journals that do not exist.

Rules:
- **Never add a reference without a verifiable DOI or stable URL.**
- **Never invent or infer a citation** from a partial description.
- If a notebook needs a new reference, insert a clearly marked placeholder:
  `[CITATION NEEDED: description of the claim that needs a source]`
  and leave it for the human to supply.
- The reference list in `README.md` and per-notebook References sections are
  authoritative; do not modify them without instruction.

### Glossary entries

The glossary defines domain-specific terms for readers who may not have backgrounds
in both cryptography and geospatial data science. Definitions must be:
- Technically accurate as reviewed by a domain expert
- Consistent in terminology with the rest of the notebooks
- Free of circular definitions and unexplained jargon

AI can draft glossary entries, but they must be reviewed for technical accuracy
before publication. Do not add a glossary section to any notebook autonomously.
If a glossary term is needed, mark it with `[GLOSSARY: term — draft definition]`
for human review.

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

**Synthetic data disclaimer** — NB14, NB15, and NB16 use synthetic individual
records parameterised from published public health statistics. Every notebook that
introduces or uses synthetic records must include this statement in its title cell
or a prominent early markdown cell:

> The individual records in this notebook are synthetic datasets parameterised from
> published public health statistics. They are not real patient records, not
> epidemiological estimates, and should not be interpreted as such. They serve
> solely as privacy-risk testbeds for evaluating geographic coordinate encryption.

Do not omit or abbreviate this statement when adding new scenario notebooks.

**H3 cell-area claims** — H3 hexagonal cells are useful as a more globally
regular index than Web Mercator square bins, but strict equal-area claims are
contestable. Unless a notebook explicitly quantifies cell-area variation across
the study area, use the phrase "more globally regular cell areas than Web Mercator
square bins at equivalent resolution" rather than "equal-area." NB11 should be
checked against this guidance.
