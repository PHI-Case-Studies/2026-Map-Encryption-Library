# Map Encryption Library — Research Roadmap

## Notebook phases

| Phase | Notebooks | Theme |
|-------|-----------|-------|
| Prior art (Module 0) | NB00–NB00c | Donut masking, H3 hex-grid binning |
| Core mechanisms | NB01–NB05 | Projection, quantisation, PRP, AEAD, jitter |
| System implications | NB06–NB10 | Full pipeline, security, evaluation, split storage, ethics |
| Research extensions | NB11+ | Advanced geospatial architecture and evaluation |

NB01–NB10 form a coherent minimal complete system. NB11 onward are
graduate-level modules that can be read independently or in sequence.
Module 0 (NB00–NB00c) is a self-contained primer on pre-cryptographic
geoprivacy that provides motivation and prior-art context for NB01+.

---

## Module 0 — Prior Art: Pre-Cryptographic Geoprivacy *(done)*

Four notebooks from the companion `2023-Ethical-Practice-Geospatial-Data-Science`
repository, adapted to use this repo's `geoprivacy/` package and cartodbpositron
tile convention. Documents what donut masking and hex-grid binning achieve and where
they fall short, motivating the full cryptographic pipeline.

- [x] NB00: Introduction — geoprivacy problem, overview of two baseline approaches
- [x] NB00a: Donut geomasking on 250 cholera deaths; Folium map; re-ID experiment (~1-3%)
- [x] NB00b: Self-contained evaluation — WMC displacement, re-ID rate sweep, EDD tradeoff table
- [x] NB00c: H3 hex-grid binning at resolutions 7-9; spatial k-anonymity tradeoff table
- [x] geoprivacy/ package: fixed 4 issues (pd.concat, osmnx import, h3 4.x API, gmIDeffort bug)
- [x] NB01 patched: prior art forward reference added
- [x] NB07 patched: comparison table (donut, H3, full pipeline) added before References

**Key findings:**
- Donut geomasking (50-125 m): ~87 m EDD, ~1-3% re-ID rate, cluster structure preserved
- H3 hex binning (res 9): ~100-150 m EDD, ~0% re-ID within cell, individual precision lost
- Full pipeline: ~35 m EDD, ~0% re-ID, cluster structure destroyed, tamper detectable

---

## NB11 — DGGS and Advanced Spatial Binning *(done)*

Replacing Web Mercator squares with equal-area hierarchical cells.

- [x] 11.1 Why go beyond square tiles (Mercator distortion, unequal area, edge artifacts)
- [x] 11.2 H3 resolution selection and equal-area comparison
- [x] 11.3 Encoding cholera data into H3 cells, Folium cell-boundary map
- [x] 11.4 Multi-resolution privacy (res 7/8/9 nested at Broadwick Street pump)
- [x] 11.5 PRP over H3 cell IDs via keyed PRF
- [x] 11.6 Intra-cell residual and adapted pipeline table

**Planned additions:**
- [ ] 11.3 Comparing DGGS systems — H3 hexagons vs S2 spherical quads vs rHEALPix vs ISEA3H
- [ ] 11.7 Hierarchy leakage, semantic inference, irregular adjacency (limitations)

---

## NB12 — Advanced Spatial Privacy Evaluation Part 1 *(done)*

- [x] Ripley's K / L-function — clustering across 10–300 m scales
- [x] AUC-L scalar summary of clustering preservation
- [x] Moran's I — global spatial autocorrelation of death counts
- [x] Getis-Ord Gi* — local hotspot persistence; Folium map
- [x] Three-scenario framework: original / jitter-only / full pipeline

## NB13 — Advanced Spatial Privacy Evaluation Part 2 *(done)*

- [x] KDE surface fidelity (Pearson r, KL divergence) on 60×60 grid
- [x] Multi-scale Ripley's K sweep over jitter_max_frac 0–0.5
- [x] Privacy–utility frontier curve (EDD vs KDE r and AUC-L)
- [x] Failure cases: co-location, boundary records, K-ring sensitivity

---

## NB14 — Cholera Dataset Augmentation *(done)*

Spatial and demographic enrichment of Snow's 250-location dataset.

- [x] OSM building footprints as 1854 proxy (2,112 polygons, Overpass API)
- [x] Spatial snapping: 131 street-side death points → nearest building interior
      (Shapely nearest_points + 1 m inward nudge; median 3.5 m, max 7.4 m)
- [x] Synthetic demographics: date of death (Snow 1855 daily table),
      age (Farr 1854 Registrar General), sex (Bernoulli 0.5)
- [x] Data provenance notes with verifiable primary sources and re-ID literature

**Output files:** `data/soho_1854_buildings.geojson`,
`data/cholera_deaths_snapped.csv`, `data/cholera_deaths_individual.csv`

---

## NB15 — Data Setup: Substance Use Scenario *(done)*

Three-layer dataset construction for Philadelphia overdose data (Scenario B from NB10).
Parallels NB14 but for a stigmatised population with equity analysis.

- [x] Synthetic dataset: 516 incidents across 6 Philadelphia ZIP codes (2022)
      parameterised from Philadelphia DPH CHART Vol. 8 No. 3
- [x] Figure 15a: geographic distribution coloured by substance type
- [x] Part 2: OSM building footprints via Overpass (108,183 polygons within study area)
- [x] Spatial snapping: 368 street-side points → nearest building interior
      (Shapely nearest_points + 1 m inward nudge; median 6.1 m displacement)
- [x] Figure 15b: Folium map — footprints + original/snapped layers
- [x] Part 3: ACS 2022 demographics (B01003/B02001/B03003/B17001/B19013 for 6 ZIPs)
- [x] Figure 15c: racial/ethnic composition + poverty bar chart
- [x] Table 15a: demographics by ZIP code

**Data files:** `data/phila_zipcodes.geojson`, `data/phila_buildings.geojson`,
`data/phila_overdose_snapped.csv`

---

## NB16 — Data Setup: Environmental Scenario *(done)*

Houston Ship Channel — TRI industrial facilities + residential proximity.

- [x] Curated TRI 2022 dataset: 18 major Ship Channel facilities with coordinates
- [x] 7 target ZIP codes: 77011, 77012, 77015, 77020, 77023, 77026, 77029
- [x] OSM building footprints for study area (88,666 polygons via Overpass)
- [x] Synthetic respiratory/asthma/cardiovascular incident dataset (925 records)
      parameterised from Texas DSHS and Harris County Public Health data
- [x] Spatial snapping to buildings (797/925 moved; median 17.9 m, max 1,071.2 m)
- [x] ACS 2022 demographics (B01003/B02001/B03003/B17001/B19013 for 7 ZIPs)
- [x] Figure 16a: TRI facility locations + incident distribution (Folium)
- [x] Figure 16c: racial/ethnic composition + poverty bar chart (seaborn)
- [x] Table 16a: demographics by ZIP (Plotly CDN)

**Data files:** `data/houston_zipcodes.geojson`, `data/houston_buildings.geojson`,
`data/houston_incidents_snapped.csv`

---

## NB17 — Adversarial Experiments *(done)*

Three re-identification attacks across all three public health scenarios.

- [x] 17.1 Adversary model (QI-only, spatial, compound)
- [x] 17.2 Quasi-identifier k-anonymity: three QI levels per scenario; Table 17a
- [x] 17.3 Figure 17a: k=1 fraction by scenario and QI granularity
- [x] 17.4 Nearest-record spatial attack: jitter-only vs full pipeline; Figure 17b
- [x] 17.5 Compound geographic-proximity + QI attack; Figure 17c
- [x] 17.6 Attack summary table (Table 17b) and conclusions

**Key findings:** Full pipeline reduces spatial re-ID from 10–90 % (jitter-only) to ≈ 0 %;
compound attack from 31–48 % (jitter-only) to ≈ 0 %; QI-only attack unchanged (pipeline
does not encrypt metadata — requires separate QI generalisation).

---

## NB18 — Formal Threat Model *(planned)*

NB07 provides a structured but informal threat model. NB18 should formalise it:

- [ ] Adversary capability tiers: external observer, partial-key insider, full-key compromise
- [ ] Trust boundaries: what each pipeline layer protects and what it explicitly does not
- [ ] Key access and leakage channels: what an attacker with only qxp/qyp can infer
- [ ] Access-pattern leakage: what repeated queries to the display tier reveal over time
- [ ] Formal security definitions appropriate for the PRP+AEAD construction
- [ ] Mapping of NB17 empirical attack results onto the formal tiers

*Rationale from cross-AI review (ChatGPT, 2025-05-10):* NB17 makes strong
empirical claims about attack success rates; these claims need a formal adversary
model to scope them correctly and avoid over- or under-stating security guarantees.

---

## NB19 — Baseline Comparison *(planned)*

The repository cites geo-indistinguishability and related mechanisms extensively
but does not compare them empirically against the custom PRP+AEAD+jitter pipeline.

- [ ] Random uniform jitter (current jitter-only baseline)
- [ ] Gaussian perturbation at equivalent standard deviation
- [ ] Laplace mechanism (geo-indistinguishability, Andrés et al. 2013)
- [ ] Spatial cloaking (k-nearest-neighbour anonymisation)
- [ ] H3 hex-grid aggregation (from NB11)
- [ ] Donut geomasking (from `geoprivacy/` package)
- [ ] Full PRP+AEAD+jitter pipeline
- [ ] Common evaluation metrics across all mechanisms: EDD, AUC-L, k=1 rate, compound attack success

*Rationale from cross-AI review (ChatGPT, 2025-05-10):* The repo is currently
centred on its custom pipeline without empirical positioning against the established
literature it cites. NB19 is the "next quality jump" that transforms the repo from
a self-contained demo into a contribution to the comparative geoprivacy literature.

---

## NB20–NB21 — Further extensions *(ideas)*

| Notebook | Topic |
|----------|-------|
| NB20 | Differential privacy hybrids — Laplace/Gaussian mechanisms as complement to AEAD |
| NB21 | Federated geospatial analytics |

---

## Long-term vision

The repository evolves from a map encryption demo into a
**computational geoprivacy research framework**, structured so that:

- The core arc (NB01–NB10) is usable as a self-contained course or executable paper
- Advanced modules (NB11+) are optional graduate-level extensions
- The progression supports Jupyter Book documentation, conference tutorials,
  and integration with ontology-driven spatial systems
