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

## NB11 — DGGS and Advanced Spatial Binning *(in progress)*

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

## NB12 — Advanced Spatial Privacy Evaluation *(planned)*

NB08 introduces first-generation metrics (EDD, MNND, DBSCAN fidelity).
NB12 extends to second-generation spatial structure metrics.

### 12.1 Why spatial statistics matter
- Beyond point displacement: topology, clustering, autocorrelation, epidemiologic interpretation

### 12.2 Ripley's K
- Measures clustering across scales
- Directly relevant for outbreak maps and density preservation

### 12.3 Moran's I
- Spatial autocorrelation
- Tests whether encrypted maps preserve broad spatial trends

### 12.4 Getis-Ord Gi*
- Hotspot persistence before and after encryption + jitter

### 12.5 KDE fidelity
- Compare original vs protected kernel density surfaces

### 12.6 Multi-scale evaluation
- Critical for DGGS systems with hierarchical resolutions

### 12.7 Privacy–utility frontier
- Visualise the tradeoff curve across jitter and bin-size parameter sweeps
- Strongest conceptual section: ties NB08 metrics to NB10 ethics

### 12.8 Failure cases
- Scenarios where metrics disagree with each other

---

## NB13–NB20 — Future extensions *(ideas)*

| Notebook | Topic |
|----------|-------|
| NB13 | Trajectory privacy — sequences of locations, linkage attacks |
| NB14 | Semantic geoprivacy — place type inference, POI linkage |
| NB15 | GeoSPARQL and encrypted spatial RDF |
| NB16 | Privacy-preserving vector tiles |
| NB17 | Differential privacy hybrids — Laplace/Gaussian mechanisms vs AEAD |
| NB18 | Federated geospatial analytics |
| NB19 | Spatial ontology and policy enforcement |
| NB20 | Trusted execution environments for geospatial systems |

---

## Long-term vision

The repository evolves from a map encryption demo into a
**computational geoprivacy research framework**, structured so that:

- The core arc (NB01–NB10) is usable as a self-contained course or executable paper
- Advanced modules (NB11+) are optional graduate-level extensions
- The progression supports Jupyter Book documentation, conference tutorials,
  and integration with ontology-driven spatial systems
