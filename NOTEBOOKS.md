# Map Encryption Library — Notebook Guide

This is a thirteen-notebook series that walks through the four-step geographic
coordinate encryption pipeline implemented in `map_encryption.py`, evaluates
its privacy properties, examines the ethical tensions that govern when and
how to deploy it, and explores DGGS as an alternative spatial reference layer.
Each notebook is self-contained: import only what you need for that topic, run
cells in order, and you will have a working demonstration.

All spatial examples use the **1854 Soho cholera outbreak dataset** (John Snow):
250 death locations and 8 water pump locations from `data/cholera_deaths.csv`
and `data/pumps.csv`.

## Notebook Overview

| Notebook | Title | Primary Topic | Depends On |
|----------|-------|---------------|------------|
| 01 | Introduction to Map Encryption | Problem statement, 4-step pipeline, encode/decode demo | — |
| 02 | Coordinate Projection | Web Mercator formula, scale distortion, pump round-trips | — |
| 03 | Grid Snapping and the Feistel PRP | Tile quantisation, Feistel bijection, rejection sampling | 02 (concept) |
| 04 | Residual Encryption with AEAD | ChaCha20-Poly1305, AD construction, tamper detection | 03 (concept) |
| 05 | Key Derivation and Display Jitter | HKDF-style KDF, jitter mechanics, key privilege separation | 04 (concept) |
| 06 | Complete Pipeline | Public-API only, 250-record end-to-end demo, failure modes | 01–05 |
| 07 | Security and Limitations | Threat model, 5 limitations, directions for improvement | 01–06 |
| 08 | Evaluation: EDD, MNND, Cluster Fidelity | Privacy metric suite from Lin (2023), jitter sweep | 05–06 |
| 09 | ct_resid Externalization | Split storage architecture, AEAD-PRP mutual dependency | 04–06 |
| 10 | Ethical Perspectives on Geoprivacy | Six tensions, three public health scenarios, principle mapping | 01–08 |
| 11 | DGGS as Tile Identifiers | H3 hexagonal cells, equal-area advantage, multi-resolution privacy, adapted pipeline | 03–04 |
| 12 | Advanced Evaluation Part 1 | Ripley's K, Moran's I, Getis-Ord Gi* on original vs jitter-only vs full pipeline | 08 |
| 13 | Advanced Evaluation Part 2 | KDE fidelity, multi-scale K sweep, privacy–utility frontier, failure cases | 12 |

## Per-Notebook Descriptions

**01 — Introduction to Map Encryption**
Explains why GPS coordinates are quasi-identifying and why field-level encryption
alone is insufficient. Introduces the four-step pipeline (Project, Snap+Shuffle,
Lock, Wobble) with a glossary table. Encodes all 250 cholera death locations and
renders a matplotlib side-by-side before/after scatter chart.

**02 — Coordinate Projection**
Derives the Web Mercator forward and inverse formulae, explains the logarithmic
term (inverse Gudermannian) and the pole singularity. Projects the 8 John Snow
pump locations within Soho, verifies round-trip fidelity to 1e-10 degrees, and
charts scale distortion vs latitude. Shows why projected metre-based tiles have
consistent index semantics.

**03 — Grid Snapping and the Feistel PRP**
Demonstrates quantisation of projected coordinates to 250 m tiles using the
Broadwick Street pump as the reference point. Explains why a bijection is required
and walks through the Feistel round structure manually — verifying the output
matches the library's `_prp_encrypt`. Maps all 250 cholera death locations to
their snapped tile centres. Includes a rejection-sampling explanation and
interactive scatter showing the PRP shuffling 625 tiles.

**04 — Residual Encryption with AEAD**
Shows semantic security of ChaCha20-Poly1305: same plaintext, three nonces, three
completely different ciphertexts. Explains the length-prefixed associated data
construction and why it prevents boundary-shift attacks. Runs six tamper scenarios
(flipped bit, changed nonce, wrong AD, wrong key) using a Broadwick Street pump
record and presents results in a markdown table.

**05 — Key Derivation and Display Jitter**
Explains domain separation in the BLAKE2s-based KDF: why three independent subkeys
are required and what each protects. Verifies distinctness, avalanche, and
determinism properties. Demonstrates display jitter on 50 co-located records
at the Broadwick Street pump and plots the jitter displacement histogram for
1000 records.

**06 — The Complete Pipeline**
Public-API-only showcase. Encodes all 250 cholera death locations, verifies
round-trip fidelity (max error < 4e-14 degrees), renders two interactive Folium
maps (original/decoded at Soho zoom; display positions at world zoom), and runs
six failure-mode scenarios. A parameter tuning table closes the notebook.

**07 — Security Properties and Limitations**
Provides a structured threat model table, then honestly documents five limitations:
no formal anonymity, access-pattern leakage, Web Mercator distortion (coarser at
high latitudes), catastrophic key compromise, and the bespoke construction caveat.
Closes with five concrete improvement directions and a reference list.

**08 — Evaluation: EDD, MNND, and Cluster Fidelity**
Implements three metrics from Lin (2023): Expected Displacement Distance, Mean
Nearest-Neighbour Distance, and DBSCAN cluster fidelity. Co-location jitter
quality is measured on the cholera dataset; the privacy demonstration assigns
deaths to their nearest pump and shows PRP destroys the cluster structure
(171 deaths near Broadwick Street collapse to 0 DBSCAN clusters in display space).
A jitter sweep shows EDD and MNND scale linearly with `jitter_max_frac`.

**09 — ct_resid Externalization and Split Storage**
Builds on NB04's AEAD knowledge to explore what each combination of keys and
record fields can unlock. A four-level unlock demonstration shows that `aead_key`
alone cannot decrypt `ct_resid` — `prp_key` is also required to build the correct
Associated Data. Part 2 shows split storage in action using 10 real cholera
death records: primary store (display fields) vs ct_resid vault (FID → ciphertext).
Part 3 demonstrates that publishing `ct_resid` + `nonce` in a public API response
is safe as long as keys are not exposed.

**10 — Ethical Perspectives on Geoprivacy**
Translates the six core tensions from public health geoprivacy ethics into
concrete scenarios using the cholera dataset. A `SchemeParams` sweep shows
the utility/disclosure tradeoff numerically (EDD and DBSCAN cluster count vs
`bin_size_m`). Three public health scenarios (infectious disease, substance use,
environmental mapping) demonstrate that the same scheme may be ethical in one
context and inappropriate in another. Closes with an eight-principle table
mapping each ethical concept to a specific scheme property.

**11 — DGGS as Tile Identifiers**
Introduces H3 (Uber's hexagonal Discrete Global Grid System) as an alternative
to Web Mercator squares for the snapping step. Encodes all 250 cholera death
locations to H3 resolution 9 cells (~201 m average edge), visualises cell
boundaries on a Folium map, and demonstrates multi-resolution privacy (resolutions
7–9 nested at Broadwick Street pump). Shows how a keyed PRF can shuffle 64-bit
H3 cell IDs analogously to the current Feistel PRP, computes intra-cell residuals,
and plots Web Mercator area distortion vs latitude to motivate the equal-area
advantage of DGGS. Closes with a side-by-side comparison table and adapted
pipeline description.

**12 — Advanced Spatial Privacy Evaluation Part 1**
Introduces second-generation spatial structure metrics alongside NB08's
first-generation EDD/MNND/DBSCAN. Three comparison scenarios are used
throughout: original coordinates, jitter-only displacement (±62.5 m,
no PRP shuffle), and full-pipeline display (PRP + jitter). Ripley's K
and the L-function quantify clustering intensity across 10–300 m scales;
the AUC-L scalar summarises clustering preservation. Moran's I tests
global spatial autocorrelation of death counts with 400 m distance-band
weights. Getis-Ord Gi* identifies persistent local hotspots; a Folium map
colours each death location by hotspot status (persists, lost, or gained).

**13 — Advanced Spatial Privacy Evaluation Part 2**
Continues with surface-level and system-level metrics. Part 1 compares
KDE density surfaces for original vs jitter-only using Pearson r and
KL divergence on a 60 × 60 grid, with a linked `folium.plugins.DualMap`
(pan and zoom synchronised between panels) replacing the static heatmap.
Part 2 sweeps `jitter_max_frac` from 0 to 0.5 and plots how the AUC-L
clustering index degrades. Part 3 builds the privacy–utility frontier:
EDD on the x-axis vs KDE Pearson r and AUC-L ratio on the y-axis, showing
that `jitter_max_frac=0.25` sits near the Pareto-optimal knee. Part 4
examines three failure cases where metrics give conflicting verdicts:
co-location inflating Moran's I, boundary records lost from Gi* hotspots,
and scale-specific K-ring sensitivity missed by the AUC aggregate.

## Reading Paths

**Sequential (full course):** 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13

**API users (skip internals):** 01 → 06 → 10
Understand the encode/decode/render interface, failure modes, and ethical
deployment considerations without deep-diving into cryptographic internals.

**Crypto readers (primitives focus):** 03 + 04 + 09 + 11
Grid snapping and Feistel PRP (NB03), AEAD and tamper detection (NB04),
split storage dependency chain (NB09), and DGGS cell ID permutation (NB11).

**Ethics / policy readers:** 07 + 08 + 10
Threat model and limitations (NB07), quantitative privacy evaluation (NB08),
and ethical tensions with scenario matrices (NB10).

**Spatial evaluation readers:** 08 → 12 → 13
First-generation metrics EDD/MNND/DBSCAN (NB08), second-generation point
pattern and autocorrelation metrics (NB12), density surface fidelity and
the privacy–utility frontier (NB13).
