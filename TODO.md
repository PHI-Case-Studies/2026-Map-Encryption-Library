# Map Encryption Library — Research Roadmap

## Notebook phases

| Phase | Notebooks | Theme |
|-------|-----------|-------|
| Prior art (Module 0) | NB00–NB00c | Donut masking, H3 hex-grid binning |
| Core mechanisms | NB01–NB05 | Projection, quantisation, PRP, AEAD, jitter |
| System implications | NB06–NB10 | Full pipeline, security, evaluation, split storage, ethics |
| Research extensions | NB11–NB13 | Advanced geospatial architecture and evaluation |
| Scenario datasets | NB14–NB16 | Cholera augmentation, Philadelphia overdose, Old Naledi TB |
| Adversarial + formal | NB17–NB20 | Re-ID attacks, formal threat model, Gaussian/Laplace mechanisms, baseline comparison |

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

Replacing Web Mercator squares with more globally regular hierarchical cells.

- [x] 11.1 Why go beyond square tiles (Mercator distortion, area variation, edge artifacts)
- [x] 11.2 H3 resolution selection and cell-area regularity comparison
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

## NB16 — Data Setup: Tuberculosis Scenario *(done)*

Old Naledi, Gaborone, Botswana — Kopanyo Programme TB data (2013–2015).
A global-health case study demonstrating privacy-utility calibration at settlement scale.

- [x] OSM building footprints for Old Naledi neighbourhood, Gaborone (Overpass API)
- [x] Folium map of building footprints (Figure 16a)
- [x] Synthetic TB dataset: 305 records parameterised from Kopanyo Programme 2013–2015
      (cumulative incidence 799.2/100k; HIV co-infection 62.7%; seasonal onset curve)
- [x] Synthetic demographics: age/sex from Botswana 2022 census distributions,
      hiv_status at Kopanyo rates, onset_date from seasonal curve
- [x] Population-weighted spatial snapping: buildings weighted by floor area as
      household-density proxy; median displacement documented
- [x] Part 4: extent-derived SchemeParams (~2.55 km diagonal → proportionate bin size)

**Data files:** `data/old_naledi_buildings.geojson`, `data/old_naledi_tb_snapped.csv`,
`data/old_naledi_age_sex.csv`

---

## NB17 — Adversarial Experiments *(done)*

Three re-identification attacks across all three public health scenarios.

- [x] 17.1 Adversary model (QI-only, spatial, compound)
- [x] 17.2 Quasi-identifier k-anonymity: three QI levels per scenario; Table 17a
- [x] 17.3 Figure 17a: k=1 fraction by scenario and QI granularity
- [x] 17.4 Nearest-record spatial attack: jitter-only vs full pipeline; Figure 17b
- [x] 17.5 Compound geographic-proximity + QI attack; Figure 17c
- [x] 17.6 Attack summary table (Table 17b) and conclusions

**Key findings:** Full pipeline reduces spatial re-ID from 10–87 % (jitter-only) to ≈ 0 %;
compound attack from 31 % (Philadelphia jitter-only; Cholera and Old Naledi already 0 % due
to density) to 0 %; QI-only attack unchanged (pipeline does not encrypt metadata — requires
separate QI generalisation). Old Naledi jitter-only spatial success (34.8 %) is moderate
due to high settlement density compared with Philadelphia (86.6 %).

---

## NB18 — Formal Threat Model *(done)*

NB07 provides a structured but informal threat model. NB18 formalises it:

- [x] Adversary capability tiers: external observer (Tier 0), display-tier operator (Tier 1), decode-tier operator (Tier 2), full-key compromise (Tier 3)
- [x] Trust boundaries: what each pipeline layer protects and what it explicitly does not
- [x] Key access and leakage channels: `_AEAD.decrypt()` returns None on wrong AD; correct AD requires prp_key to compute (qx, qy)
- [x] Access-pattern leakage: same (lat, lon) → same (qxp, qyp); tile frequency observable without keys
- [x] Formal security definitions: IND-CPA for tiles, IND-CCA for residuals, tamper detection; NOT k-anonymity, NOT epsilon-DP, NOT forward secrecy
- [x] Mapping of NB17 empirical attack results onto the formal tiers

**Key findings:**
- Tier 1 adversary (jitter_key only): render display coordinates but cannot reverse PRP or decrypt residual
- AEAD-PRP mutual dependency: aead_key alone cannot decrypt because correct AD requires prp_key
- Access-pattern leakage: tile frequency distribution is observable without keys (structural side channel)
- NB17 spatial/compound attacks are Tier 1 and fail because PRP globally disperses display coordinates

*Rationale from cross-AI review (ChatGPT, 2025-05-10):* NB17 makes strong
empirical claims about attack success rates; these claims need a formal adversary
model to scope them correctly and avoid over- or under-stating security guarantees.

---

## NB19 — Gaussian and Laplace Mechanisms *(done)*

Demonstrates Gaussian perturbation and planar Laplace geo-indistinguishability on the
489-individual Soho cholera dataset, providing the conceptual and mathematical foundation
used in NB20's baseline comparison.

- [x] Gaussian perturbation: Rayleigh displacement distribution, EDD = sigma * sqrt(pi/2), EDD vs sigma sweep
- [x] Planar Laplace (Andrés et al. 2013): r ~ Gamma(2, 1/epsilon), E[r] = 2/epsilon, EDD vs 1/epsilon sweep
- [x] Three-way comparison: uniform jitter vs Gaussian vs Laplace at matched EDD (~55-60 m)
- [x] Summary table: EDD, median, 95th-percentile, max displacement per mechanism

**Key findings:**
- Laplace has heavier tails than Gaussian at same mean displacement (higher 95th-percentile)
- Uniform jitter is hard-bounded at J*sqrt(2); Gaussian and Laplace are unbounded
- Neither Gaussian nor Laplace globally disperses spatial clustering in this demonstration — both remain in the Soho area
- Planar Laplace provides formal epsilon-geo-indistinguishability guarantee; Gaussian does not

---

## NB20 — Baseline Comparison *(done)*

The repository cited geo-indistinguishability and related mechanisms but did not
compare them empirically against the custom PRP+AEAD+jitter pipeline. Laplace
mechanism uses the proper planar Laplace from NB19 (epsilon=1/30 per m, E[r]=60 m).

- [x] Random uniform jitter (current jitter-only baseline, +/-62.5 m)
- [x] Gaussian perturbation (sigma=45 m per axis)
- [x] Planar Laplace geo-indistinguishability (epsilon=1/30 per m, E[r]=60 m, NB19)
- [x] Spatial cloaking (k=15 nearest-neighbour centroid)
- [x] H3 hex-grid aggregation (resolution 9, from NB11/geoprivacy package)
- [x] Donut geomasking (band 50-125 m, from geoprivacy package)
- [x] Full PRP+AEAD+jitter pipeline
- [x] Common evaluation metrics: EDD, AUC-L ratio, nearest-record spatial attack, compound attack

**Key findings:**
- Full pipeline achieves ~35 m EDD (same as uniform jitter) with ~0% spatial attack and ~0% compound attack
- Perturbation mechanisms (jitter, Gaussian, Laplace, donut): EDD 35-90 m, spatial attack 40-80%
- H3 hex-grid and spatial cloaking: EDD 100-200+ m, AUC-L > 100% (artificial super-clusters), spatial attack reduced but not zero
- Full pipeline: unique privacy-utility position — jitter-level EDD with globally-randomising privacy
- Residual limitation: access-pattern leakage (tile frequencies) remains (formalised in NB18)

*Rationale from cross-AI review (ChatGPT, 2025-05-10):* The repo was centred on its
custom pipeline without empirical positioning against the established literature it cites.

---

## NB21 — Research Synthesis *(done)*

Capstone notebook synthesising the full NB01–NB20 arc.

- [x] Contributions and boundaries of the PRP+AEAD+jitter framework
- [x] Explicit distinction between cryptographic confidentiality, empirical attack resistance, and differential privacy
- [x] Operational deployment considerations: key custody, access tiers, incident response, auditability
- [x] Open attack surfaces and future research directions

## NB22 — Privacy, Utility, and Adoption *(done)*

Complexity as a third dimension; better-than-nothing baseline; seven-mechanism
complexity rubric; three-axis deployment guidance; open questions extended.

- [x] Part 1: Better-than-nothing baseline (no-protection vs. protection gradient)
- [x] Part 2: Complexity scoring table (implementation effort, key management,
      infrastructure dependency, auditability) for all seven NB20 mechanisms
- [x] Part 3: Three-axis view — mechanism positions and deployment tier guidance
- [x] Part 4: Six open questions (five from NB21.7 + adoption/complexity question)
- [x] Part 5: Future directions including managed key service and empirical adoption study
- [x] References: Hampton 2010, Keßler & McKenzie 2018, Kounadi & Resch 2018,
      Li 2025, npj Digital Medicine 2025, Sharma et al. 2025, Andrés et al. 2013, Lin 2023

**NB21 also simplified:** Parts 4–7 compressed (3 tables → 1 summary, prose → table,
future directions updated for NB22/NB23 renumbering, open questions → summary table
pointing to NB22). Three new references added to NB21.

## NB23–NB24 — Further extensions *(ideas)*

| Notebook | Topic |
|----------|-------|
| NB23 | Differential privacy hybrids — combining planar Laplace (NB19) with the PRP+AEAD pipeline |
| NB24 | Federated geospatial analytics |

---

## Long-term vision

The repository evolves from a map encryption demo into a
**computational geoprivacy research framework**, structured so that:

- The core arc (NB01–NB10) is usable as a self-contained course or executable paper
- Advanced modules (NB11+) are optional graduate-level extensions
- The progression supports Jupyter Book documentation, conference tutorials,
  and integration with ontology-driven spatial systems
