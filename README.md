# Map Encryption Library

A Python library for reversible encryption of geographic coordinates that
hides both tile identity (via a Feistel PRP) and sub-tile precision (via
ChaCha20-Poly1305 AEAD), while enabling a display tier to render jittered
map pins without ever decrypting precise GPS coordinates.

## How It Works

- **Project** — Convert (lat, lon) to Web Mercator metres (NB02)
- **Snap + Shuffle** — Quantise to a 250 m tile; permute tile indices with a
  Feistel pseudorandom permutation keyed by `prp_key` (NB03)
- **Lock** — AEAD-encrypt the sub-tile residual (rx, ry) with ChaCha20-Poly1305,
  binding the ciphertext to (qx, qy, tweak) via associated data (NB04)
- **Wobble** — Add per-record jitter using only `jitter_key` for display;
  no precise coordinates are exposed to the display tier (NB05)

## Quick Start

```bash
conda env create -f environment.yml
conda activate crypto
jupyter lab 01-introduction.ipynb
```

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/PHI-Case-Studies/2026-Map-Encryption-Library/HEAD)

## Files

| File | Description |
|------|-------------|
| `map_encryption.py` | Core library: all crypto logic, public API and private helpers |
| `01-introduction.ipynb` | Problem statement, pipeline overview, matplotlib demo |
| `02-coordinate-projection.ipynb` | Web Mercator derivation, scale distortion, 8-city round-trip |
| `03-grid-snapping-and-prp.ipynb` | Grid quantisation, Feistel PRP walkthrough, rejection sampling |
| `04-residual-encryption-aead.ipynb` | ChaCha20-Poly1305, AD construction, tamper-detection demo |
| `05-key-derivation-and-display-jitter.ipynb` | HKDF-style KDF, jitter mechanics, key privilege separation |
| `06-complete-pipeline.ipynb` | Public-API end-to-end demo with 500 points and failure modes |
| `07-security-and-limitations.ipynb` | Threat model, 5 limitations, improvement directions |
| `NOTEBOOKS.md` | Narrative guide, reading paths, per-notebook descriptions |
| `environment.yml` | Conda environment specification |

## Dependencies

- **Python 3.10**
- **numpy** — numerical arrays for synthetic point generation
- **matplotlib** — NB01 only (side-by-side scatter)
- **plotly** — interactive charts and maps in NB02–NB07
- **cryptography** (preferred) — ChaCha20-Poly1305 AEAD via
  `cryptography.hazmat.primitives.ciphers.aead`
- **pandas** — DataFrame construction for Plotly inputs

**Fallback:** If `cryptography` is not installed, the library falls back to
XOR + HMAC-SHA256 using only the Python standard library. All security
properties are preserved; ChaCha20-Poly1305 is preferred for performance
and standards compliance.

> **Note:** BLAKE2s is used throughout (key derivation, PRF, jitter) via
> `hashlib.blake2s` in the Python standard library — no external dependency
> is required for the non-AEAD cryptographic operations.
