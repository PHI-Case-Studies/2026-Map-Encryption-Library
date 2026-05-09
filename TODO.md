# Map Encryption Library — Research Roadmap

## Notebook phases

| Phase | Notebooks | Theme |
|-------|-----------|-------|
| Core mechanisms | NB01–NB05 | Projection, quantisation, PRP, AEAD, jitter |
| System implications | NB06–NB10 | Full pipeline, security, evaluation, split storage, ethics |
| Research extensions | NB11+ | Advanced geospatial architecture and evaluation |

NB01–NB10 form a coherent minimal complete system. NB11 onward are
graduate-level modules that can be read independently or in sequence.

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

## NB15–NB20 — Future extensions *(ideas)*

| Notebook | Topic |
|----------|-------|
| NB15 | Infectious disease scenario — household inference attacks using NB14 layers |
| NB16 | Substance use / environmental scenario — SAMHSA / EPA TRI data |
| NB17 | Adversarial experiments — linkage, re-identification, quasi-identifier attacks |
| NB18 | Differential privacy hybrids — Laplace/Gaussian mechanisms vs AEAD |
| NB19 | Federated geospatial analytics |
| NB20 | Trusted execution environments for geospatial systems |

---

## Long-term vision

The repository evolves from a map encryption demo into a
**computational geoprivacy research framework**, structured so that:

- The core arc (NB01–NB10) is usable as a self-contained course or executable paper
- Advanced modules (NB11+) are optional graduate-level extensions
- The progression supports Jupyter Book documentation, conference tutorials,
  and integration with ontology-driven spatial systems
