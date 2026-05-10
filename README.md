# Map Encryption Library

A Python library for reversible encryption of geographic coordinates that
hides both tile identity (via a Feistel PRP) and sub-tile precision (via
ChaCha20-Poly1305 AEAD), while enabling a display tier to render jittered
map pins without ever decrypting precise GPS coordinates.

All spatial examples use the **1854 Soho cholera outbreak dataset** (John Snow):
250 death locations and 8 water pump locations from `data/cholera_deaths.csv`
and `data/pumps.csv`.

## How It Works

- **Project** — Convert (lat, lon) to Web Mercator metres (NB02)
- **Snap + Shuffle** — Quantise to a 250 m tile; permute tile indices with a
  Feistel pseudorandom permutation keyed by `prp_key` (NB03)
- **Lock** — AEAD-encrypt the sub-tile residual (rx, ry) with ChaCha20-Poly1305,
  binding the ciphertext to (qx, qy, tweak) via associated data (NB04)
- **Wobble** — Add per-record jitter using only `jitter_key` for display;
  no precise coordinates are exposed to the display tier (NB05)

```mermaid
flowchart TD
    classDef coord  fill:#d4edda,stroke:#155724,color:#333
    classDef record fill:#d1ecf1,stroke:#0c5460,color:#333

    IN["(lat, lon)\noriginal GPS coordinate"]:::coord

    subgraph ENC["encode()  ·  NB01 / NB06  ·  prp_key + aead_key"]
        direction TB
        E1["① Project  ·  NB02\n_project() — Web Mercator\n(lat, lon) → (x, y) metres"]
        E2["② Snap to 250 m tile  ·  NB03\nqx = round(x/250)   qy = round(y/250)\nrx = x − qx·250      ry = y − qy·250"]
        E3["③ Feistel PRP  ·  NB03\n_prp_encrypt(qx, qy, prp_key)\n→ shuffled (qxp, qyp)"]
        E4["④ AEAD encrypt residual  ·  NB04\n_AEAD(aead_key).encrypt(nonce, (rx, ry), AD)\nChaCha20-Poly1305  →  ct_resid"]
    end

    REC[["Encrypted record\nqxp · qyp · nonce · ct_resid · tweak · version"]]:::record

    subgraph DIS["render_coordinates()  ·  NB05  ·  jitter_key only"]
        direction TB
        D1["BLAKE2s jitter  ·  NB05\nseed = (qxp, qyp, nonce)   key = jitter_key\noffset ≤ ±62.5 m per axis"]
        D2["Display pin\napproximate position only"]:::coord
    end

    subgraph DEC["decode()  ·  NB06  ·  prp_key + aead_key"]
        direction TB
        F1["⑤ Feistel PRP⁻¹  ·  NB06\n_prp_decrypt(qxp, qyp, prp_key)\n→ original (qx, qy)"]
        F2["⑥ AEAD decrypt + verify  ·  NB06\n_AEAD(aead_key).decrypt(nonce, ct_resid, AD)\nreturns None if tag fails  →  (rx, ry)"]
        F3["⑦ Reconstruct metres  ·  NB06\nx = qx·250 + rx\ny = qy·250 + ry"]
        F4["⑧ Unproject  ·  NB06\n_unproject() — Web Mercator\n(x, y) metres → (lat, lon)"]
    end

    OUT["(lat, lon)\nexact — lossless round-trip"]:::coord

    IN  --> E1 --> E2
    E2  --> E3 --> REC
    E2  --> E4 --> REC
    REC --> D1 --> D2
    REC --> F1 --> F2 --> F3 --> F4 --> OUT
```

## Quick Start

```bash
conda env create -f environment.yml
conda activate crypto
jupyter lab 01-introduction.ipynb
```

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/PHI-Case-Studies/2026-Map-Encryption-Library/HEAD)

> **Binder note:** Open and run **one notebook at a time**. Keeping multiple
> notebooks active simultaneously will exhaust Binder's memory limit and crash
> the session. Shut down a notebook's kernel before opening the next one.

## Relationship to the 2023 Geoprivacy Case Study

This repository builds on the earlier
[`2023-Ethical-Practice-Geospatial-Data-Science`](https://github.com/PHI-Case-Studies/2023-Ethical-Practice-Geospatial-Data-Science)
digital case study, which introduced geoprivacy concepts through an executable
Jupyter/Docker learning module based on the 1854 Soho cholera outbreak using
public, non-sensitive data. That prior work is treated here as pedagogical and
ethical prior art.

The present repository extends that foundation from ethical case-study instruction
into a computational geoprivacy research framework. It adds reversible coordinate
encryption, Feistel PRP tile shuffling, AEAD-protected residuals, display-tier
jitter without precise-coordinate access, DGGS-style tile identifiers, advanced
spatial utility evaluation, public-health scenario augmentation, and adversarial
re-identification experiments.

The two repositories are therefore complementary: the 2023 project frames *why*
geoprivacy matters in public-health education, while the 2026 project explores
*how* protected spatial workflows might be implemented, evaluated, and
stress-tested.

## Files

| File | Description |
|------|-------------|
| `map_encryption/` | Python package — core library (`__init__.py`) and visualisation helpers (`viz.py`) |
| `geoprivacy/` | Python package — donut geomasking and H3 hex-grid binning utilities |
| `00-geoprivacy-intro.ipynb` | Geoprivacy problem, donut masking overview, H3 hex-grid binning overview |
| `00a-donut-geomasking.ipynb` | Donut geomasking (50-125 m band) on 250 cholera deaths; re-identification experiment |
| `00b-donut-geomasking-evaluation.ipynb` | WMC displacement, re-ID rate sweep, EDD vs re-ID tradeoff table |
| `00c-hex-grid-binning.ipynb` | H3 hex-grid aggregation at resolutions 7-9; spatial k-anonymity tradeoff |
| `01-introduction.ipynb` | Problem statement, pipeline overview, 250 cholera death locations |
| `02-coordinate-projection.ipynb` | Web Mercator derivation, scale distortion, 8-pump round-trip |
| `03-grid-snapping-and-prp.ipynb` | Grid quantisation, Feistel PRP walkthrough, rejection sampling |
| `04-residual-encryption-aead.ipynb` | ChaCha20-Poly1305, AD construction, tamper-detection demo |
| `05-key-derivation-and-display-jitter.ipynb` | HKDF-style KDF, jitter mechanics, key privilege separation |
| `06-complete-pipeline.ipynb` | Public-API end-to-end with 250 cholera records and failure modes |
| `07-security-and-limitations.ipynb` | Threat model, 5 limitations, improvement directions |
| `08-evaluation.ipynb` | EDD, MNND, DBSCAN cluster fidelity metrics (Lin 2023) on cholera data |
| `09-ct-resid-externalization.ipynb` | Split storage architecture, AEAD-PRP mutual dependency |
| `10-geoprivacy-ethics.ipynb` | Six ethical tensions, three public health scenarios, principle mapping |
| `11-dggs-tile-identifiers.ipynb` | H3 hexagonal DGGS as alternative tile identifier; equal-area cells, multi-resolution privacy |
| `12-advanced-evaluation-part1.ipynb` | Ripley's K, Moran's I, Getis-Ord Gi* — point pattern and autocorrelation analysis |
| `13-advanced-evaluation-part2.ipynb` | KDE fidelity, multi-scale K sweep, privacy–utility frontier, failure cases |
| `14-cholera-dataset-augmentation.ipynb` | Building footprints, spatial snapping, synthetic demographics; full data provenance and sources |
| `15-substance-use-scenario.ipynb` | Synthetic Philadelphia overdose dataset; OSM building footprints + spatial snapping; ACS 2022 demographic context for six ZIP codes |
| `16-houston-environmental-scenario.ipynb` | Curated TRI 2022 facility dataset; synthetic respiratory incidents; OSM building footprints + spatial snapping; ACS 2022 demographic context for seven Houston Ship Channel ZIP codes |
| `17-adversarial-experiments.ipynb` | QI-only, nearest-record spatial, and compound geographic+QI re-identification attacks across all three scenarios; jitter-only vs full pipeline |
| `18-formal-threat-model.ipynb` | Four adversary capability tiers, trust boundaries, AEAD-PRP key dependency demo, access-pattern side channel, formal security definitions |
| `19-baseline-comparison.ipynb` | Empirical comparison of seven geoprivacy mechanisms on EDD, AUC-L, spatial attack, and compound attack; privacy-utility frontier |
| `data/cholera_deaths.csv` | 250 death locations from the 1854 Soho outbreak (John Snow) |
| `data/cholera_deaths_snapped.csv` | 250 death locations with 131 street-side points snapped to nearest building interior (≤10 m displacement) |
| `data/cholera_deaths_individual.csv` | 489 one-row-per-death records with synthetic date_of_death (Snow 1855 daily distribution), age (Farr 1854 Registrar General), and sex |
| `data/soho_1854_buildings.geojson` | 2,112 current OSM building footprints for the Soho study area (used as spatial proxy for 1854 buildings) |
| `data/pumps.csv` | 8 water pump locations used in Snow's investigation |
| `data/phila_zipcodes.geojson` | 48 Philadelphia ZIP code polygons from OpenDataPhilly (used in NB15) |
| `data/phila_buildings.geojson` | 108,183 OSM building footprints for the six-ZIP Philadelphia study area (NB15) |
| `data/phila_overdose_snapped.csv` | 516 one-row-per-incident synthetic overdose records with LAT\_snapped, LON\_snapped, disp\_m columns (NB15) |
| `data/houston_zipcodes.geojson` | Census TIGER/Line ZCTA boundaries for the seven Houston Ship Channel ZIP codes (NB16) |
| `data/houston_buildings.geojson` | 88,666 OSM building footprints for the seven-ZIP Houston study area (NB16) |
| `data/houston_incidents_snapped.csv` | 925 one-row-per-incident synthetic respiratory records with LAT\_snapped, LON\_snapped, disp\_m columns (NB16) |
| `NOTEBOOKS.md` | Narrative guide, reading paths, per-notebook descriptions |
| `TODO.md` | Research roadmap: completion status NB00–NB19 and future extensions NB20+ |
| `environment.yml` | Conda environment specification |
| `archive/` | Original prototype notebook (`map-encryption-v3-validated.ipynb`) |

## Dependencies

- **Python 3.10**
- **numpy** — numerical arrays
- **matplotlib / seaborn** — all static charts (NB01–NB17)
- **folium** — interactive maps in NB02, NB03, NB05, NB06, NB08, NB11–NB16
- **pandas** — CSV loading and DataFrame construction
- **scipy** — nearest-neighbour distance (MNND) in NB08; KDE in NB13; KDTree in NB17
- **scikit-learn** — DBSCAN cluster evaluation in NB08 and NB10
- **h3-py** — H3 hexagonal DGGS cell encoding in NB11
- **libpysal / esda / pointpats** — spatial weights, Moran's I, Getis-Ord Gi*, Ripley's K in NB12–NB13
- **cryptography** (preferred) — ChaCha20-Poly1305 AEAD via
  `cryptography.hazmat.primitives.ciphers.aead`

**Fallback:** If `cryptography` is not installed, the library falls back to
XOR + HMAC-SHA256 using only the Python standard library. The fallback preserves
the notebook demonstrations and integrity-checking behaviour via HMAC-SHA256, but
does not provide the authenticated encryption (IND-CCA) guarantees of
ChaCha20-Poly1305. Use the `cryptography` package for any real deployment.

> **Note:** BLAKE2s is used throughout (key derivation, PRF, jitter) via
> `hashlib.blake2s` in the Python standard library — no external dependency
> is required for the non-AEAD cryptographic operations.

Each notebook ends with a References section citing the sources relevant to that topic.

## Development

This repository was developed with **Claude Sonnet 4.6** (Anthropic) via
[Claude Code](https://claude.ai/code), an AI-assisted development environment.
All commits carry a `Co-Authored-By: Claude Sonnet 4.6` trailer reflecting this.

**What AI contributed:** notebook structure and cell sequencing, matplotlib/seaborn
chart code, data pipeline code (Overpass API fetches, spatial snapping, ACS census
queries), the `_gen_nbNN.py` generator script pattern, documentation prose, and
iterative debugging of execution errors across all notebooks.

**Cross-platform AI review:** ChatGPT was used as an independent reviewer on
selected notebooks and on the overall methodological approach, covering pipeline
design soundness, geospatial data science accuracy, adversarial experiment design,
and visualisation quality. Disagreements between Claude and ChatGPT were resolved
by the human author. See [`CLAUDE.md`](CLAUDE.md) for the review process and
prompt templates.

**What was human-directed:** research design and narrative arc (which topics, in
which order, using which datasets), selection and vetting of all external data
sources and their provenance, cryptographic design decisions in `map_encryption/`,
ethical framing in NB10, technical review of geospatial data science methods,
verification of all bibliographic references, and review of all quantitative
results for correctness and interpretability.

**Curation and AI-assisted contribution guidance** is documented in [`CLAUDE.md`](CLAUDE.md),
which covers notebook formatting conventions, the generator script workflow and its
known pitfalls, library structure, and effective prompt patterns for common tasks
(adding a notebook, patching a cell, converting a chart, adding captions).

**Large notebook outputs:** `15-substance-use-scenario.ipynb` is approximately
61 MB due to embedded Folium map HTML containing 108,183 building-footprint
polygons. For publication, Jupyter Book builds, or CI pipelines, clear heavy
Folium outputs before processing:
```bash
jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace 15-substance-use-scenario.ipynb
```
GitHub accepts the file as-is (under the 100 MB limit) but will warn; Binder
should be used one notebook at a time (see the Binder note above).

**Pain points encountered during AI-assisted development:**
- Plotly 6.x incompatibility with JupyterLab's bundled extension — all charts
  were migrated to matplotlib/seaborn
- Triple-quote conflicts in generator scripts (`f"""..."""` inside `code("""\...""")`)
  require triple-single-quotes or string concatenation inside cell source strings
- Duplicate column names arise when renaming a column that shares a name with an
  existing column — always `drop` before `rename`
- `conda run -n crypto` resolves to system Python on this machine — use the full
  path `/opt/homebrew/Caskroom/miniforge/base/envs/crypto/bin/python` instead

## References

Andrés, M. E., Bordenabe, N. E., Chatzikokolakis, K., & Palamidessi, C. (2013). Geo-indistinguishability: Differential privacy for location-based systems.
In Proceedings of the 2013 ACM SIGSAC Conference on Computer & Communications Security (CCS '13). https://doi.org/10.1145/2508859.2516735

Arcolezi, H. H., Cerna Ñahuis, S. L., Guyeux, C., & Couchot, J.-F. (2021). Preserving geo-indistinguishability of the emergency scene to predict ambulance response time.
Mathematical and Computational Applications. https://doi.org/10.3390/mca26030056

Chatzikokolakis, K., ElSalamouny, E., & Palamidessi, C. (2017). Efficient utility improvement for location privacy.
Proceedings on Privacy Enhancing Technologies. https://doi.org/10.1515/popets-2017-0051

Chatzikokolakis, K., ElSalamouny, E., Palamidessi, C., & Pazii, A. (2017). Methods for location privacy: A comparative overview.
Foundations and Trends in Privacy and Security. https://doi.org/10.1561/3300000017

Chatzikokolakis, K., Palamidessi, C., & Stronati, M. (2015). Constructing elastic distinguishability metrics for location privacy.
Proceedings on Privacy Enhancing Technologies. https://doi.org/10.1515/popets-2015-0023

Chatzikokolakis, K., Palamidessi, C., & Stronati, M. (2015). Geo-indistinguishability: A principled approach to location privacy.
In Distributed Computing and Internet Technology, LNCS 8956. https://doi.org/10.1007/978-3-319-14977-6_4

Chatzikokolakis, K., Palamidessi, C., & Stronati, M. (2015). Location privacy via geo-indistinguishability. 
In Theoretical Aspects of Computing - ICTAC 2015, LNCS 9399. https://doi.org/10.1007/978-3-319-25150-9_2

Jin, F., Ruan, B., Hua, W., Li, L., & Zhou, X. (2024). Preserving location privacy with semantic-aware indistinguishability.
In Database Systems for Advanced Applications, LNCS 14853. https://doi.org/10.1007/978-981-97-5562-2_15

Kim, J., & Lim, B. (2023). Effective and privacy-preserving estimation of the density distribution of LBS users under geo-indistinguishability.
Electronics, 12(4), 917. https://doi.org/10.3390/electronics12040917

Lin, Y. (2023). Geo-indistinguishable masking: Enhancing privacy protection in spatial point mapping. Cartography and Geographic Information Science. https://doi.org/10.1080/15230406.2023.2267967

Mendes, R., Cunha, M., & Vilela, J. P. (2020). Impact of frequency of location reports on the privacy level of geo-indistinguishability. 
Proceedings on Privacy Enhancing Technologies. https://doi.org/10.2478/popets-2020-0032

Min, M., Zhu, H., Ding, J., Li, S., Xiao, L., Pan, M., & Han, Z. (2024). 
Personalized 3D location privacy protection with differential and distortion geo-perturbation.
IEEE Transactions on Dependable and Secure Computing. https://doi.org/10.1109/TDSC.2023.3335374

Min, M., Zhu, H., Li, S., Zhang, H., Xiao, L., Pan, M., & Han, Z. (2024). Semantic adaptive geo-indistinguishability for location privacy protection in mobile networks.
IEEE Transactions on Vehicular Technology. https://doi.org/10.1109/TVT.2024.3354881

Oya, S., Troncoso, C., & Pérez-González, F. (2017). Back to the drawing board: Revisiting the design of optimal location privacy-preserving mechanisms.
In Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security. https://doi.org/10.1145/3133956.3134004

Qiu, C., Squicciarini, A., Pang, C., Wang, N., & Wu, B. (2022). Location privacy protection in vehicle-based spatial crowdsourcing via geo-indistinguishability.
IEEE Transactions on Mobile Computing. https://doi.org/10.1109/TMC.2020.3037911

Ren, W., & Tang, S. (2020). EGeoIndis: An effective and efficient location privacy protection framework in traffic density detection.
Vehicular Communications. https://doi.org/10.1016/j.vehcom.2019.100187

Song, S. M., & Kim, J. W. (2022). Privacy-preserving estimation of users' density distribution in location-based services through geo-indistinguishability. 
Journal of The Korea Society of Computer and Information. https://doi.org/10.9708/jksci.2022.27.12.161

Song, S., & Kim, J. (2023). Adapting geo-indistinguishability for privacy-preserving collection of medical microdata.
Electronics, 12(13), 2793. https://doi.org/10.3390/electronics12132793

Squicciarini, A. C., & Qiu, C. (2019). Location privacy protection in vehicle-based spatial crowdsourcing via geo-indistinguishability.
In 2019 IEEE 39th International Conference on Distributed Computing Systems (ICDCS). https://doi.org/10.1109/ICDCS.2019.00109

Takagi, S., Cao, Y., Asano, Y., & Yoshikawa, M. (2019). Geo-graph-indistinguishability: Protecting location privacy for LBS over road networks.
In Data and Applications Security and Privacy XXXIII. https://doi.org/10.1007/978-3-030-22479-0_8

Takagi, S., Cao, Y., Asano, Y., & Yoshikawa, M. (2023). Geo-graph-indistinguishability: Location privacy on road networks with differential privacy.
IEICE Transactions on Information and Systems. https://doi.org/10.1587/transinf.2022DAP0011

Wang, L., Yang, D., Han, X., Wang, T., Zhang, D., & Ma, X. (2017). Location privacy-preserving task allocation for mobile crowdsensing with differential geo-obfuscation.
In Proceedings of the 26th International Conference on World Wide Web (WWW 2017). https://doi.org/10.1145/3038912.3052696

Wang, L., Zhang, D., Yang, D., Lim, B. Y., & Ma, X. (2016). Differential location privacy for sparse mobile crowdsensing.
In 2016 IEEE 16th International Conference on Data Mining (ICDM). https://doi.org/10.1109/ICDM.2016.41

Yan, Y., Xu, F., Mahmood, A., Dong, Z., & Sheng, Q. Z. (2022). Perturb and optimize users' location privacy using geo-indistinguishability and location semantics.
Scientific Reports. https://doi.org/10.1038/s41598-022-24893-0

Yu, L., Zhang, S., Meng, Y., Chen, Y., Ren, Y.-L., Du, S., & Zhu, H. (2024). Privacy-preserving location-based advertising via longitudinal geo-indistinguishability.
IEEE Transactions on Mobile Computing. https://doi.org/10.1109/TMC.2023.3348136

Zhang, P., Cheng, X., Su, S., & Wang, N. (2022). Area coverage-based worker recruitment under geo-indistinguishability.
Computer Networks, 217, 109340. https://doi.org/10.1016/j.comnet.2022.109340

Zhang, P., Zhu, Y., Liu, X., Wu, B., Sun, L., Han, S., Fang, X., & Zhang, J. (2024). Task allocation with profit maximization under geo-indistinguishability via Q-learning.
In IEEE International Conference on High Performance Computing and Communications (HPCC 2024). https://doi.org/10.1109/HPCC64274.2024.00119

Zhang, S., Duan, B., Chen, Z., & Zhong, H. (2025). Geo-indistinguishable location obfuscation with inference error bounds.
Journal of Complexity, 91, 101970. https://doi.org/10.1016/j.jco.2025.101970

Zhao, Y., Yuan, D., Du, J. T., & Chen, J. (2022). Geo-ellipse-indistinguishability: Community-aware location privacy protection for directional distribution.
IEEE Transactions on Knowledge and Data Engineering. https://doi.org/10.1109/TKDE.2022.3192360


