# Map Encryption Library — Notebook Guide

This is a bottom-up series of seven Jupyter notebooks that walk through the
four-step geographic coordinate encryption pipeline implemented in
`map_encryption.py`. Each notebook is self-contained: import only what you
need for that topic, run cells in order, and you will have a working
demonstration with interactive charts.

## Notebook Overview

| Notebook | Title | Primary Topic | Depends On |
|----------|-------|---------------|------------|
| 01 | Introduction to Map Encryption | Problem statement, 4-step pipeline, full encode/decode demo | — |
| 02 | Coordinate Projection | Web Mercator formula, scale distortion, grid dimensions | — |
| 03 | Grid Snapping and the Feistel PRP | Tile quantisation, Feistel bijection, rejection sampling | 02 (concept) |
| 04 | Residual Encryption with AEAD | ChaCha20-Poly1305, AD construction, tamper detection | 03 (concept) |
| 05 | Key Derivation and Display Jitter | HKDF-style KDF, jitter mechanics, key privilege separation | 04 (concept) |
| 06 | Complete Pipeline | Public-API only, 500-point end-to-end demo, failure modes | 01–05 |
| 07 | Security and Limitations | Threat model, 5 limitations, directions for improvement | 01–06 |

## Per-Notebook Descriptions

**01 — Introduction to Map Encryption**
Explains why GPS coordinates are quasi-identifying and why field-level encryption
alone is insufficient. Introduces the four-step pipeline (Project, Snap+Shuffle,
Lock, Wobble) with a glossary table. Encodes 200 synthetic points near Times Square
and renders a matplotlib side-by-side before/after scatter chart.

**02 — Coordinate Projection**
Derives the Web Mercator forward and inverse formulae, explains the logarithmic
term (inverse Gudermannian) and the pole singularity. Projects 8 benchmark cities,
verifies round-trip fidelity to 1e-10 degrees, and charts scale distortion vs
latitude with Plotly. Shows why projected metre-based tiles have consistent
index semantics.

**03 — Grid Snapping and the Feistel PRP**
Demonstrates quantisation of projected coordinates to 250 m tiles and residual
extraction. Explains why a bijection is required and walks through the Feistel
round structure manually — verifying the output matches the library's
`_prp_encrypt`. Includes a rejection-sampling explanation and interactive
scatter showing the PRP shuffling 625 tiles.

**04 — Residual Encryption with AEAD**
Shows semantic security of ChaCha20-Poly1305: same plaintext, three nonces, three
completely different ciphertexts. Explains the length-prefixed associated data
construction and why it prevents boundary-shift attacks. Runs six tamper scenarios
(flipped bit, changed nonce, wrong AD, wrong key) and presents results in a
Plotly table.

**05 — Key Derivation and Display Jitter**
Explains domain separation in the BLAKE2s-based KDF: why three independent subkeys
are required and what each protects. Verifies distinctness, avalanche, and
determinism properties. Demonstrates display jitter on 50 co-located records
and plots the jitter displacement histogram for 1000 records.

**06 — The Complete Pipeline**
Public-API-only showcase. Encodes 500 synthetic points, verifies round-trip
fidelity (max error < 1e-9 degrees), renders three interactive maps (original /
display / decoded), draws displacement lines from render to decoded, and runs
six failure-mode scenarios. A parameter tuning table closes the notebook.

**07 — Security Properties and Limitations**
Provides a structured threat model table, then honestly documents five limitations:
no formal anonymity, access-pattern leakage, Web Mercator distortion, catastrophic
key compromise, and the bespoke construction caveat. Closes with five concrete
improvement directions and a reference list.

## Reading Paths

**Sequential (full course):** 01 → 02 → 03 → 04 → 05 → 06 → 07

**API users (skip internals):** 01 → 06
Understand the encode/decode/render interface and failure modes without
deep-diving into cryptographic internals.

**Crypto readers (primitives focus):** 03 + 04
Grid snapping and Feistel PRP (NB03) followed by AEAD and tamper detection
(NB04) covers the two core cryptographic layers in depth.
