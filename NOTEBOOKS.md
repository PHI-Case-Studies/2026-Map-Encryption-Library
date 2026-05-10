# Map Encryption Library — Notebook Guide

This is a twenty-four-notebook series spanning a Module 0 on pre-cryptographic
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

| Notebook | Title | Primary Topic | Depends On |
|----------|-------|---------------|------------|
| 00 | Introduction to Geoprivacy | Problem statement, donut masking, H3 hex binning overview | — |
| 00a | Donut Geomasking | Random displacement 50-125 m, re-identification experiment | 00 |
| 00b | Donut Geomasking Evaluation | WMC analysis, re-ID rate sweep, performance tradeoff | 00a |
| 00c | H3 Hex-Grid Binning | Hexagonal cell aggregation, multi-resolution privacy, tradeoff table | 00 |
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
| 14 | Cholera Dataset Augmentation | Building footprints (OSM proxy), spatial snapping, synthetic demographics; full data provenance notes | 06–08 |
| 15 | Data Setup: Substance Use Scenario | Synthetic Philadelphia overdose dataset; OSM building footprints; spatial snapping; ACS 2022 demographic context | 06, 10, 14 |
| 16 | Data Setup: Environmental Scenario | Curated TRI 2022 facilities; synthetic respiratory incidents; OSM building footprints; spatial snapping; ACS 2022 demographic context | 06, 10, 14 |
| 17 | Adversarial Experiments | QI-only, nearest-record spatial, and compound geographic+QI attacks across all three scenarios; jitter-only vs full pipeline | 14–16 |
| 18 | Formal Threat Model | Adversary capability tiers, trust boundaries, key access/leakage channels, access-pattern side channel, formal security definitions | 04–09 |
| 19 | Gaussian and Laplace Mechanisms | Gaussian perturbation (Rayleigh displacement), planar Laplace geo-indistinguishability (Andrés et al. 2013), epsilon vs EDD, three-way comparison | 05 |
| 20 | Baseline Comparison | Seven mechanisms (uniform jitter, Gaussian, Laplace, spatial cloaking, H3 hex-grid, donut geomasking, full pipeline) on EDD, AUC-L, spatial attack, compound attack | 08, 12–13, 17, 19 |

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

**16 — Data Setup: Environmental Scenario**
Constructs the three-layer research dataset for Houston Ship Channel environmental
burden data (Scenario C from NB10). Part 1 embeds a curated TRI 2022 facility dataset
(18 major facilities, coordinates from EPA TRI geocoding) and generates a synthetic
dataset of 925 respiratory/cardiovascular emergency visits across seven Ship Channel
ZIP codes (2022), parameterised from Texas DSHS environmental public health tracking
data; maps incident distribution and facility locations by chemical class (Figure 16a).
Part 2 fetches OSM building footprints for the seven-ZIP study area (88,666 polygons)
via the Overpass API and snaps all 925 synthetic incident points to the nearest
building interior using Shapely `nearest_points` (median displacement 17.9 m,
max 1,071.2 m); outputs `data/houston_buildings.geojson` and
`data/houston_incidents_snapped.csv`. Part 3 retrieves 2022 ACS 5-year estimates
for all seven ZIP codes (B01003, B02001, B03003, B17001, B19013) and presents
racial/ethnic composition and poverty rates (Figure 16c, Table 16a): all seven
ZIPs are majority-Hispanic environmental-justice communities with poverty rates
between 18 % and 32 %.

**17 — Adversarial Experiments**
Runs three classes of re-identification attack against the three public health scenario
datasets (cholera, Philadelphia overdose, Houston environmental), comparing jitter-only
geomasking with the full encryption pipeline. Part 1 measures k-anonymity under
progressively finer quasi-identifier subsets (sex/age/date for cholera;
ZIP/substance/age for Philadelphia; ZIP/symptom/age for Houston), finding that fine QI
combinations already create k = 1 records independently of location (cholera 12.3 %,
Philadelphia 4.5 %, Houston 1.5 %). Part 2 runs the nearest-record spatial attack:
under jitter-only the attacker recovers the true snapped building with high success
for spread-out scenarios (Philadelphia 86.6 %, Houston 90.5 %) but lower success in
dense Soho (cholera 10.0 %); the full pipeline collapses all three to ≈ 0 %. Part 3
runs the compound geographic-proximity + QI attack with a 500 m radius: jitter-only
allows 31.2 % (Philadelphia) and 47.7 % (Houston) unique matches; the full pipeline
neutralises this attack entirely across all scenarios.

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
displacement closes the notebook. Neither Gaussian nor Laplace destroys spatial
clustering structure; both remain vulnerable to spatial re-identification attacks,
as quantified in NB20.

**20 — Baseline Comparison**
Positions the map encryption pipeline in the geoprivacy literature by empirically
comparing it against six other mechanisms on the 489-individual Soho cholera dataset.
Part 1 applies all seven mechanisms (uniform jitter +/-62.5 m, Gaussian sigma=45 m,
Laplace scale=45 m, spatial cloaking k=15 NN centroid, H3 hex-grid at resolution 9,
donut geomasking 50-125 m, full PRP+AEAD+jitter pipeline) and tabulates EDD per
mechanism (Table 19a). Part 2 computes EDD and AUC-L clustering preservation ratio;
H3 and spatial cloaking show AUC-L ratios above 100% due to point-mass collapse,
while the full pipeline reports 0% because display coordinates are globally dispersed.
Part 3 runs the nearest-record spatial attack and compound proximity+QI attack from
NB17; perturbation-based mechanisms remain vulnerable (40-80% spatial attack success)
because they stay geographically near the original study area. Part 4 presents a
four-metric summary table (Table 19b) and a privacy-utility frontier scatter
(Figure 19e): the full pipeline achieves ~0% attack success at ~35 m EDD, matching
the utility of uniform jitter while providing the privacy of a globally randomising
scheme. The main limitation is access-pattern leakage (tile frequencies are
deterministic and observable without keys, as formalised in NB18).

## Reading Paths

**Sequential (full course):** 00 → 00a → 00b → 00c → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18 → 19 → 20

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
and Houston environmental burden (NB16).

**Adversarial / security readers:** 07 → 17 → 18 → 19 → 20
Threat model and limitations (NB07), empirical re-identification experiments
(NB17), formal adversary capability tiers and security definitions (NB18),
Gaussian and Laplace mechanism demonstrations (NB19), and comparative
positioning against seven geoprivacy mechanisms (NB20).
