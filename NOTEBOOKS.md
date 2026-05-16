# Map Encryption Library — Notebook Guide

This is a twenty-five-notebook series spanning a Module 0 on pre-cryptographic
geoprivacy approaches, the four-step geographic coordinate encryption pipeline
implemented in `map_encryption/`, privacy evaluation, ethical analysis, DGGS
alternative spatial indexing, augmented public health datasets, adversarial
re-identification experiments, a formal threat model, demonstrations of Gaussian
and Laplace geo-indistinguishability mechanisms, and an empirical baseline
comparison across seven geographic privacy mechanisms.
Each notebook is self-contained: import only what you need for that topic, run
cells in order, and you will have a working demonstration.

All spatial examples use the **1854 Soho cholera outbreak dataset** (John Snow):
250 death locations and 8 water pump locations from `data/cholera_deaths.csv`
and `data/pumps.csv`.

## Notebook Overview

Difficulty levels: **Intro** (no prior geoprivacy required) · **Intermediate** (requires NB01–06) · **Advanced** (spatial stats or crypto background) · **Research** (graduate synthesis)

| Notebook | Title | Primary Topic | Difficulty | Bloom Level | Depends On |
|----------|-------|---------------|------------|-------------|------------|
| 00 | Introduction to Geoprivacy | Problem statement, donut masking, H3 hex binning overview | Intro | Understand | — |
| 00a | Donut Geomasking | Random displacement 50-125 m, re-identification experiment | Intro | Understand/Apply | 00 |
| 00b | Donut Geomasking Evaluation | WMC analysis, re-ID rate sweep, performance tradeoff | Intro | Apply/Analyze | 00a |
| 00c | H3 Hex-Grid Binning | Hexagonal cell aggregation, multi-resolution privacy, tradeoff table | Intro | Understand/Apply | 00 |
| 01 | Introduction to Map Encryption | Problem statement, 4-step pipeline, encode/decode demo | Intro | Understand | — |
| 02 | Coordinate Projection | Web Mercator formula, scale distortion, pump round-trips | Intermediate | Apply | — |
| 03 | Grid Snapping and the Feistel PRP | Tile quantisation, Feistel bijection, rejection sampling | Intermediate | Apply/Analyze | 02 (concept) |
| 04 | Residual Encryption with AEAD | ChaCha20-Poly1305, AD construction, tamper detection | Intermediate | Apply/Analyze | 03 (concept) |
| 05 | Key Derivation and Display Jitter | HKDF-style KDF, jitter mechanics, key privilege separation | Intermediate | Apply/Analyze | 04 (concept) |
| 06 | Complete Pipeline | Public-API only, 250-record end-to-end demo, failure modes | Intermediate | Apply | 01–05 |
| 07 | Security and Limitations | Threat model, 5 limitations, directions for improvement | Intermediate | Analyze/Evaluate | 01–06 |
| 08 | Evaluation: EDD, MNND, Cluster Fidelity | Privacy metric suite from Lin (2023), jitter sweep | Intermediate | Apply/Analyze | 05–06 |
| 09 | ct_resid Externalization | Split storage architecture, AEAD-PRP mutual dependency | Intermediate | Analyze | 04–06 |
| 10 | Ethical Perspectives on Geoprivacy | Six tensions, three public health scenarios, principle mapping | Intermediate | Analyze/Evaluate | 01–08 |
| 11 | DGGS as Tile Identifiers | H3 hexagonal cells, more globally regular cell areas than Web Mercator bins, multi-resolution privacy, adapted pipeline | Advanced | Analyze | 03–04 |
| 12 | Advanced Evaluation Part 1 | Ripley's K, Moran's I, Getis-Ord Gi* on original vs jitter-only vs full pipeline | Advanced | Analyze/Evaluate | 08 |
| 13 | Advanced Evaluation Part 2 | KDE fidelity, multi-scale K sweep, privacy–utility frontier, failure cases | Advanced | Analyze/Evaluate | 12 |
| 14 | Cholera Dataset Augmentation | Building footprints (OSM proxy), spatial snapping, synthetic demographics; full data provenance notes | Advanced | Apply/Analyze | 06–08 |
| 15 | Data Setup: Substance Use Scenario | Synthetic Philadelphia overdose dataset; OSM building footprints; spatial snapping; ACS 2022 demographic context | Advanced | Apply/Analyze | 06, 10, 14 |
| 16 | Data Setup: Tuberculosis Scenario | OSM building footprints for Old Naledi, Gaborone; 305 synthetic TB records (Kopanyo 2013–2015); population-weighted spatial snapping; extent-derived SchemeParams | Advanced | Apply/Analyze | 06, 10, 14 |
| 17 | Adversarial Experiments | QI-only, nearest-record spatial, and compound geographic+QI attacks across all three scenarios; jitter-only vs full pipeline | Research | Evaluate | 14–16 |
| 18 | Formal Threat Model | Adversary capability tiers, trust boundaries, key access/leakage channels, access-pattern side channel, formal security definitions | Research | Evaluate/Create | 04–09 |
| 19 | Gaussian and Laplace Mechanisms | Gaussian perturbation (Rayleigh displacement), planar Laplace geo-indistinguishability (Andrés et al. 2013), epsilon vs EDD, three-way comparison | Research | Analyze/Evaluate | 05 |
| 20 | Baseline Comparison | Seven mechanisms (uniform jitter, Gaussian, Laplace, spatial cloaking, H3 hex-grid, donut geomasking, full pipeline) on EDD, AUC-L, spatial attack, compound attack | Research | Evaluate | 08, 12–13, 17, 19 |
| 21 | Research Synthesis | Contributions, limitations, DP comparison, condensed operational deployment, unresolved gaps, future directions, open questions summary | Research | Evaluate/Create | 01–20 |
| 22 | Privacy, Utility, and Adoption | Complexity as a third axis; better-than-nothing baseline; seven-mechanism complexity rubric; three-axis deployment guidance; open questions extended | Research | Evaluate/Create | 20–21 |

## Per-Notebook Descriptions

**00 — Introduction to Geoprivacy**
Introduces the geoprivacy problem: why GPS coordinates are quasi-identifying even
without names. Surveys two pre-cryptographic baseline approaches — donut geomasking
and H3 hex-grid binning — and demonstrates each briefly on the Broadwick Street pump
location. Closes by mapping each approach's limitations onto the four properties the
cryptographic pipeline (NB01+) adds: formal security, tamper detection, key-based
access control, and cluster-structure destruction.

**00a — Donut Geomasking**
Applies the `geoprivacy.data_geomask()` function to all 250 cholera death locations
using a 50-125 m band. Shows an interactive Folium map (original vs masked), a
displacement histogram, and a nearest-neighbour re-identification experiment showing
~1-3% of masked records can be recovered within 20 m.

**00b — Donut Geomasking Evaluation**
Self-contained evaluation (no cross-notebook file dependencies). Part 1: weighted mean
center displacement over 20 independent masking runs shows population-level summaries
are preserved (~10 m WMC shift despite 87 m mean individual displacement). Part 2:
re-identification rate sweep across four band configurations (25-50 m, 50-125 m,
100-200 m, 200-400 m). Part 3: utility-privacy tradeoff table comparing EDD vs
re-identification rate across configurations.

**00c — H3 Hex-Grid Binning**
Applies H3 hexagonal cell aggregation at resolutions 7, 8, and 9 to all 250 cholera
deaths. Renders cell boundaries and centroids on a Folium map. Part 2 shows nested
multi-resolution cells at the Broadwick Street pump. Part 3 presents a tradeoff table:
unique cell count, mean EDD, minimum spatial k-anonymity, and mean spatial k-anonymity
across all three resolutions.

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
deaths to their nearest pump and shows PRP disperses the display-space cluster structure
(171 deaths near Broadwick Street collapse to 0 DBSCAN clusters in display space).
A jitter sweep shows EDD and MNND scale linearly with `jitter_max_frac`.

**09 — ct_resid Externalization and Split Storage**
Builds on NB04's AEAD knowledge to explore what each combination of keys and
record fields can unlock. A four-level unlock demonstration shows that `aead_key`
alone cannot decrypt `ct_resid` — `prp_key` is also required to build the correct
Associated Data. Part 2 shows split storage in action using 10 real cholera
death records: primary store (display fields) vs ct_resid vault (FID → ciphertext).
Part 3 demonstrates that publishing `ct_resid` + `nonce` in a public API response
does not expose the plaintext residual unless the required keys and associated data
are also available.

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
and plots Web Mercator area distortion vs latitude to motivate the more globally
regular cell-area behaviour of DGGS. Closes with a side-by-side comparison table and adapted
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

**14 — Cholera Dataset Augmentation**
Documents the three spatial and demographic layers constructed from Snow's
original 250-location dataset. Part 1 presents OSM building footprints as a
1854 proxy, with a rationale based on Soho's Georgian/Victorian building stock
and acknowledged limitations. Part 2 shows the spatial snapping procedure that
moves 131 street-side death points into the nearest building interior (median
displacement 3.5 m, max 7.4 m using Shapely `nearest_points` + 1 m inward
nudge). Part 3 documents the synthetic demographic generation: date of death
from Snow's (1855) daily fatal-attack table (peak Sep 2: 143 deaths, pump
handle removed Sep 8), age from Farr's (1854) Registrar General age-stratified
cholera mortality table (0–4: 32 %, 60+: 9 %), and sex by uniform Bernoulli.
Closes with a data provenance notes section containing verifiable primary
sources, inference logic, caveats about synthetic attributes, and references
to re-identification literature (Sweeney 2002; El Emam et al. 2011).

**13 — Advanced Spatial Privacy Evaluation Part 2**
Continues with surface-level and system-level metrics. Part 1 compares
KDE density surfaces for original vs jitter-only using Pearson r and
KL divergence on a 60 × 60 grid, with a linked `folium.plugins.DualMap`
(pan and zoom synchronised between panels) using stable georeferenced
ImageOverlay rather than screen-pixel HeatMap. Part 2 sweeps
`jitter_max_frac` from 0 to 0.5 and presents two views: Figure 13b
(single Monte Carlo draw, showing inherent noise in the AUC-L estimate)
and Figure 13c (20-draw average with ±1 std band, revealing the true
monotone decay). Part 3 builds the privacy–utility frontier (Figure 13d):
EDD on the x-axis vs KDE Pearson r and AUC-L ratio on the y-axis, showing
that `jitter_max_frac=0.25` sits near the Pareto-optimal knee. Part 4
examines three failure cases where metrics give conflicting verdicts:
co-location inflating Moran's I, boundary records lost from Gi* hotspots,
and scale-specific K-ring sensitivity missed by the AUC aggregate.

**15 — Data Setup: Substance Use Scenario**
Constructs the three-layer research dataset for Philadelphia overdose data,
applying the same augmentation pattern as NB14 but for Scenario B (substance
use / stigmatised population). Part 1 generates a synthetic dataset of 516
fatal overdose incidents across six Philadelphia ZIP codes (2022), parameterised
from the Philadelphia Department of Public Health CHART Vol. 8 No. 3 report,
and maps the geographic distribution by substance type (Figure 15a). Part 2
fetches OSM building footprints for the six-ZIP study area (108,183 polygons)
via the Overpass API and snaps all 516 synthetic incident points to the nearest
building interior using Shapely `nearest_points` (median displacement 6.1 m,
max 882.9 m); outputs `data/phila_buildings.geojson` and
`data/phila_overdose_snapped.csv`. Part 3 retrieves 2022 ACS 5-year estimates
for all six ZIP codes (B01003, B02001, B03003, B17001, B19013) and presents
racial/ethnic composition and poverty rates (Figure 15c, Table 15a): all six
ZIPs are majority-minority with poverty rates between 28 % and 40 %.

**16 — Data Setup: Tuberculosis Scenario**
Constructs the synthetic tuberculosis (TB) dataset used in NB17 as Scenario C.
Old Naledi is a high-density residential neighbourhood in Gaborone, Botswana
(population ~20,330; ~14,800 persons/km²) with the highest TB cumulative incidence
in the Gaborone study area (Kopanyo Programme, 2013–2015). The scenario demonstrates
how settlement scale, infectious-disease stigma, and HIV co-infection jointly shape the
privacy-utility calibration decision. Part 1 fetches OSM building footprints for Old
Naledi (Overpass API) and renders them on a Folium map (Figure 16a). Part 2 generates
305 synthetic TB records parameterised from Kopanyo 2013–2015 data: age and sex from
census distributions, HIV co-infection status at 62.7 % (Kopanyo rate), onset date
from a seasonal incidence curve. Part 3 applies population-weighted spatial snapping —
buildings are weighted by floor area as a proxy for household density — assigning each
record to a building interior; outputs `data/old_naledi_buildings.geojson` and
`data/old_naledi_tb_snapped.csv`. Part 4 derives SchemeParams from the settlement
extent (~2.55 km diagonal) rather than a fixed absolute distance, producing
privacy bins proportionate to the study-area scale.

**17 — Adversarial Experiments**
Runs three classes of re-identification attack against the three public health scenario
datasets (cholera, Philadelphia overdose, Old Naledi TB), comparing jitter-only
geomasking with the full encryption pipeline. Part 1 measures k-anonymity under
progressively finer quasi-identifier subsets (sex/age/date for cholera;
ZIP/substance/age for Philadelphia; age/sex/HIV status for Old Naledi), finding that
fine QI combinations already create k = 1 records independently of location. Part 2
runs the nearest-record spatial attack: under jitter-only success reflects building
density — high in spread-out Philadelphia (Drug Overdose 86.6 %), moderate in compact
Old Naledi (Tuberculosis 34.8 %, where ~14,800 persons/km² places many buildings within
the jitter radius), and lowest in dense Soho (Cholera 10.0 %); the full pipeline
collapses all three to ≈ 0 %. Part 3 runs the compound geographic-proximity + QI
attack with a 500 m radius: jitter-only allows 31.2 % unique matches for Philadelphia;
both Cholera and Old Naledi yield 0 % even under jitter-only because QI combinations
are not sparse enough to uniquely identify records within any 500 m neighbourhood;
under this tested threat model, the full pipeline reduces all three datasets to 0 %.

**18 — Formal Threat Model**
Formalises the informal threat model from NB07 by defining four adversary capability
tiers (external observer, display-tier operator, decode-tier operator, full key
compromise) and mapping each to a concrete deployment role. Part 1 demonstrates
what each tier can and cannot do using `enc.encode`, `enc.render_coordinates`, and
`enc.decode`. Part 2 demonstrates the deterministic access-pattern side channel:
encoding the same location five times produces identical `(qxp, qyp)` pairs but
distinct nonces. Part 3 shows the AEAD-PRP mutual dependency: `aead_key` alone
cannot decrypt `ct_resid` because the Associated Data requires `(qx, qy)` from the
PRP inverse; `_AEAD.decrypt()` returns `None` on wrong AD. Part 4 demonstrates
tamper detection (single-bit flip → `None`). Part 5 documents formal security
definitions: what the scheme achieves (IND-CPA for tiles, IND-CCA for residuals,
tamper detection) and does not achieve (k-anonymity, epsilon-DP, forward secrecy,
access-pattern privacy). Part 6 maps the NB17 empirical attack results onto the
formal tiers: nearest-record spatial and compound attacks are Tier 1 (display-tier)
and fail because PRP globally disperses display coordinates; QI-only attacks are
outside the scheme's scope.

**19 — Gaussian Perturbation and Laplace Geo-Indistinguishability**
Introduces two alternative perturbation mechanisms from the geoprivacy literature
and demonstrates them on the 489-individual Soho cholera dataset. Part 1 covers
Gaussian perturbation: independent N(0, sigma) noise per coordinate axis produces
displacement magnitudes that follow a Rayleigh distribution (E[r] = sigma * sqrt(pi/2));
a displacement histogram with Rayleigh theoretical fit and an EDD vs sigma parameter
sweep confirm the linear relationship. Part 2 covers the planar Laplace
geo-indistinguishability mechanism (Andrés et al. 2013, DOI: 10.1145/2508859.2516735):
displacement is sampled in polar coordinates with radius r ~ Gamma(2, 1/epsilon) and
uniform bearing, providing a formal epsilon-geo-indistinguishability privacy guarantee
(E[r] = 2/epsilon metres). Displacement histogram with Gamma(2, 1/epsilon) theoretical
fit and EDD vs 1/epsilon parameter sweep are shown. Part 3 compares all three
perturbation approaches (uniform jitter, Gaussian, planar Laplace) at matched expected
displacement, showing that Laplace has the heaviest tail (most extreme outliers at the
same mean displacement). A summary table of EDD, median, 95th-percentile, and maximum
displacement closes the notebook. Neither Gaussian nor Laplace globally disperses
spatial clustering structure in these demonstrations; both remain vulnerable to the
tested spatial re-identification attacks,
as quantified in NB20.

**20 — Baseline Comparison**
Positions the map encryption pipeline in the geoprivacy literature by empirically
comparing it against six other mechanisms on the 489-individual Soho cholera dataset.
Part 1 applies all seven mechanisms (uniform jitter +/-62.5 m, Gaussian sigma=45 m,
Laplace scale=45 m, spatial cloaking k=15 NN centroid, H3 hex-grid at resolution 9,
donut geomasking 50-125 m, full PRP+AEAD+jitter pipeline) and tabulates EDD per
mechanism (Table 20a). Part 2 computes EDD and AUC-L clustering preservation ratio;
H3 and spatial cloaking show AUC-L ratios above 100% due to point-mass collapse,
while the full pipeline reports 0% because display coordinates are globally dispersed.
Part 3 runs the nearest-record spatial attack and compound proximity+QI attack from
NB17; perturbation-based mechanisms remain vulnerable (40-80% spatial attack success)
because they stay geographically near the original study area. Part 4 presents a
four-metric summary table (Table 20b) and a privacy-utility frontier scatter
(Figure 20e): the full pipeline achieves ~0% attack success under the tested
spatial and compound attacks at ~35 m EDD, matching the displacement utility of
uniform jitter while providing display coordinates that are globally dispersed under
the current PRP domain policy. The main limitation is access-pattern leakage (tile frequencies are
deterministic and observable without keys, as formalised in NB18).

**22 — Privacy, Utility, and Adoption**
Extends the NB20 baseline comparison with a third evaluation axis: implementation
complexity. Part 1 establishes the better-than-nothing baseline — any evaluated
mechanism reduces the nearest-record spatial attack from ~100 % (no protection) to
under 10 % — and introduces the adoption-weighted argument: a simpler mechanism
deployed universally may provide more aggregate privacy protection than a
sophisticated one deployed rarely. Part 2 scores all seven NB20 mechanisms on four
complexity sub-dimensions (implementation effort, key management, infrastructure
dependency, auditability) and assigns Low / Medium / High overall ratings. Part 3
maps each mechanism's position in the three-axis privacy-utility-complexity space and
gives deployment guidance for three practitioner tiers (no infrastructure, regulatory
compliance required, full key infrastructure available). Part 4 develops the five open
questions from NB21.7 with additional context and adds a sixth question about whether
complexity sub-dimensions empirically predict non-adoption. Part 5 outlines future
directions including a managed key service, an empirical adoption study, and NB23
(DP hybrids). References: Hampton et al. (2010), Keßler and McKenzie (2018), Kounadi
and Resch (2018), Li (2025), npj Digital Medicine (2025), Sharma et al. (2025).

## Reading Paths

**Sequential (full course):** 00 → 00a → 00b → 00c → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18 → 19 → 20 → 21 → 22

**Minimal core (self-contained executable paper):** 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 10
NB01–NB10 form the minimal complete system. Each notebook is self-contained and
executable in order. Readers who want only the cryptographic pipeline and its
evaluation can stop here; NB11+ are optional graduate-level extensions.

**Geoprivacy primer (Module 0 only):** 00 → 00a → 00b → 00c
Pre-cryptographic approaches — donut geomasking (NB00a), re-identification
evaluation (NB00b), and H3 hex-grid binning (NB00c) — without any cryptography.

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

**Data augmentation readers:** 14 → 15 → 16
Dataset construction pattern: building footprints, spatial snapping, and
demographic enrichment for cholera (NB14), Philadelphia substance use (NB15),
and Old Naledi tuberculosis burden (NB16).

**Adversarial / security readers:** 07 → 17 → 18 → 19 → 20
Threat model and limitations (NB07), empirical re-identification experiments
(NB17), formal adversary capability tiers and security definitions (NB18),
Gaussian and Laplace mechanism demonstrations (NB19), and comparative
positioning against seven geoprivacy mechanisms (NB20).

**Practitioners / policy readers:** 20 → 21 → 22
Baseline mechanism comparison (NB20), research synthesis and limitations (NB21),
and the adoption-focused discussion of complexity as a third axis with deployment
guidance and open questions (NB22).
