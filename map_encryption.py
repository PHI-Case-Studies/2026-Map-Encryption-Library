"""Reversible geographic coordinate encryption.

Security properties
-------------------
- Unbiased PRP via rejection sampling (no modular skew)
- Length-prefixed Associated Data (no boundary-shift ambiguity)
- Per-record jitter derived from nonce (no co-location fingerprinting)
- Record ID bound into tweak (no record-substitution attacks)
- Single master key with HKDF-style KDF (clean key separation)
- Scheme version field in every record (forward-compatible migration)
"""

__all__ = ["MapEncryption", "SchemeParams", "SCHEME_VERSION"]

import hashlib
import hmac
import math
import secrets
import struct
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

SCHEME_VERSION: int = 1

_R_EARTH: float = 6_378_137.0          # WGS84 equatorial radius in metres
_HALF_WORLD: float = 20_037_508.342789244  # half Earth circumference in metres

try:
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305 as _ChaCha20Poly1305
    _CHACHA_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CHACHA_AVAILABLE = False


# ---------------------------------------------------------------------------
# Public configuration
# ---------------------------------------------------------------------------

@dataclass
class SchemeParams:
    """Tuning parameters shared by all participants (encoder, decoder, display tier).

    These are NOT stored per-record; treat them as system configuration.
    All parties must agree on identical values.
    """
    bin_size_m: int = 250          # grid tile side-length in metres
    jitter_max_frac: float = 0.25  # display wobble: up to +-(bin_size_m * frac) metres
    prp_rounds: int = 10           # Feistel rounds (>= 8 recommended)


# ---------------------------------------------------------------------------
# Coordinate projection  (Web Mercator / EPSG:3857)
# ---------------------------------------------------------------------------

def _clamp_lat(lat_deg: float) -> float:
    # Web Mercator is undefined at the poles; clamp to the conventional limit.
    return max(-85.05112878, min(85.05112878, lat_deg))


def _project(lat_deg: float, lon_deg: float) -> Tuple[float, float]:
    lat = math.radians(_clamp_lat(lat_deg))
    lon = math.radians(lon_deg)
    x = _R_EARTH * lon
    y = _R_EARTH * math.log(math.tan(math.pi / 4.0 + lat / 2.0))
    return x, y


def _unproject(x: float, y: float) -> Tuple[float, float]:
    lon_deg = math.degrees(x / _R_EARTH)
    lat_deg = math.degrees(2.0 * math.atan(math.exp(y / _R_EARTH)) - math.pi / 2.0)
    return lat_deg, lon_deg


# ---------------------------------------------------------------------------
# Pseudorandom Permutation (Feistel over the Web Mercator grid)
# ---------------------------------------------------------------------------

def _grid_range(bin_size_m: int) -> Tuple[int, int]:
    """Return (min_q, M) where M is the total number of cells per axis."""
    lo = int(math.floor(-_HALF_WORLD / bin_size_m))
    hi = int(math.floor(+_HALF_WORLD / bin_size_m))
    return lo, hi - lo + 1


def _prf_upto(key: bytes, data: bytes, modulo: int) -> int:
    """Unbiased PRF output in [0, modulo) via rejection sampling.

    Naive hash % N is biased when 2^256 is not divisible by N. Rejection
    sampling fixes this: discard values >= floor(2^256/N)*N and retry.
    Rejection probability < N/2^256 ~ 10^-71 for N ~ 161 000.
    """
    cutoff = ((1 << 256) // modulo) * modulo
    counter = 0
    while True:
        h = hashlib.blake2s(key=key, digest_size=32)
        h.update(data + struct.pack(">I", counter))
        val = int.from_bytes(h.digest(), "big")
        if val < cutoff:
            return val % modulo
        counter += 1  # virtually never reached


def _prp_encrypt(qx: int, qy: int, key: bytes, tweak: bytes,
                 bin_size_m: int, rounds: int) -> Tuple[int, int]:
    min_q, M = _grid_range(bin_size_m)
    L, Rv = qx - min_q, qy - min_q
    for r in range(rounds):
        F = _prf_upto(key, tweak + struct.pack(">II", r, Rv), M)
        L = (L + F) % M
        L, Rv = Rv, L
    if rounds % 2 == 1:
        L, Rv = Rv, L
    return L + min_q, Rv + min_q


def _prp_decrypt(qx_p: int, qy_p: int, key: bytes, tweak: bytes,
                 bin_size_m: int, rounds: int) -> Tuple[int, int]:
    min_q, M = _grid_range(bin_size_m)
    L, Rv = qx_p - min_q, qy_p - min_q
    if rounds % 2 == 1:
        L, Rv = Rv, L
    for r in reversed(range(rounds)):
        L, Rv = Rv, L
        F = _prf_upto(key, tweak + struct.pack(">II", r, Rv), M)
        L = (L - F) % M
    return L + min_q, Rv + min_q


# ---------------------------------------------------------------------------
# AEAD  (ChaCha20-Poly1305 preferred; XOR+HMAC-SHA256 fallback)
# ---------------------------------------------------------------------------

def _keystream(key: bytes, seed: bytes, n: int) -> bytes:
    out = bytearray()
    ctr = 0
    while len(out) < n:
        h = hashlib.blake2s(key=key, digest_size=32)
        h.update(seed + struct.pack(">I", ctr))
        out += h.digest()
        ctr += 1
    return bytes(out[:n])


class _AEAD:
    def __init__(self, key: bytes):
        if _CHACHA_AVAILABLE:
            self._chacha = _ChaCha20Poly1305(hashlib.blake2s(key, digest_size=32).digest())
        else:
            stretched = hashlib.blake2b(b"KDF|" + key, digest_size=64).digest()
            self._sk = stretched[:32]
            self._mk = stretched[32:]

    @staticmethod
    def _mac_input(ad: bytes, nonce: bytes, ct: bytes) -> bytes:
        # Length-prefix each variable-length field to prevent boundary-shift ambiguity.
        return (
            struct.pack(">I", len(ad)) + ad
            + struct.pack(">I", len(nonce)) + nonce
            + ct
        )

    def encrypt(self, nonce: bytes, plaintext: bytes, ad: bytes) -> bytes:
        if _CHACHA_AVAILABLE:
            return self._chacha.encrypt(nonce, plaintext, ad)
        ks = _keystream(self._sk, nonce + ad, len(plaintext))
        ct = bytes(p ^ k for p, k in zip(plaintext, ks))
        tag = hmac.digest(self._mk, self._mac_input(ad, nonce, ct), "sha256")
        return ct + tag

    def decrypt(self, nonce: bytes, blob: bytes, ad: bytes) -> Optional[bytes]:
        if _CHACHA_AVAILABLE:
            try:
                return self._chacha.decrypt(nonce, blob, ad)
            except Exception:
                return None
        if len(blob) < 32:
            return None
        ct, tag = blob[:-32], blob[-32:]
        expected = hmac.digest(self._mk, self._mac_input(ad, nonce, ct), "sha256")
        if not hmac.compare_digest(expected, tag):
            return None
        ks = _keystream(self._sk, nonce + ad, len(ct))
        return bytes(c ^ k for c, k in zip(ct, ks))


# ---------------------------------------------------------------------------
# Key derivation
# ---------------------------------------------------------------------------

@dataclass
class _Keys:
    prp_key: bytes
    aead_key: bytes
    jitter_key: bytes


def _derive_keys(master_key: bytes) -> _Keys:
    def _kdf(label: str) -> bytes:
        h = hashlib.blake2s(digest_size=32)
        h.update(struct.pack(">I", SCHEME_VERSION))
        h.update(label.encode())
        h.update(master_key)
        return h.digest()

    return _Keys(
        prp_key=_kdf("prp-v1"),
        aead_key=_kdf("aead-v1"),
        jitter_key=_kdf("jitter-v1"),
    )


# ---------------------------------------------------------------------------
# Associated Data construction
# ---------------------------------------------------------------------------

def _build_ad(qx: int, qy: int, tweak: bytes) -> bytes:
    # Length-prefix the tweak so (qy=23, tweak=b'6') != (qy=236, tweak=b'').
    return struct.pack(">iiI", qx, qy, len(tweak)) + tweak


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class MapEncryption:
    """Reversible encryption of geographic coordinates.

    Instantiate once per deployment with a master key loaded from a secrets
    manager (AWS KMS, HashiCorp Vault, GCP Secret Manager, …). Never hard-code
    or commit the master key.

    Example
    -------
    >>> enc = MapEncryption(master_key)
    >>> tweak = MapEncryption.make_tweak(record_id=42)
    >>> record = enc.encode(40.758, -73.985, tweak=tweak)
    >>> lat, lon = enc.decode(record)
    >>> display_lat, display_lon = enc.render_coordinates(record)
    """

    def __init__(self, master_key: bytes, params: Optional[SchemeParams] = None):
        self._params = params or SchemeParams()
        self._keys = _derive_keys(master_key)

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def encode(self, lat: float, lon: float, tweak: bytes = b"") -> Dict[str, Any]:
        """Encrypt a geographic coordinate and return a storable record.

        The record dict is safe to persist in a database:
          qxp, qyp   — shuffled tile indices (reveal nothing without the PRP key)
          nonce      — 12-byte random value, public, must be unique per call
          ct_resid   — AEAD-encrypted sub-tile offset
          tweak      — stored to allow AD reconstruction during decode
          version    — scheme version for future migration
        """
        p, k = self._params, self._keys

        x, y = _project(lat, lon)
        qx = int(round(x / p.bin_size_m))
        qy = int(round(y / p.bin_size_m))
        rx = x - qx * p.bin_size_m
        ry = y - qy * p.bin_size_m

        qxp, qyp = _prp_encrypt(qx, qy, k.prp_key, tweak, p.bin_size_m, p.prp_rounds)

        nonce = secrets.token_bytes(12)
        ct = _AEAD(k.aead_key).encrypt(nonce, struct.pack(">dd", rx, ry), _build_ad(qx, qy, tweak))

        return {
            "qxp": int(qxp),
            "qyp": int(qyp),
            "nonce": nonce,
            "ct_resid": ct,
            "tweak": tweak,
            "version": SCHEME_VERSION,
        }

    def decode(self, record: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """Decrypt a record and return (lat, lon), or None on any failure.

        Returns None for wrong key, tampered ciphertext, mismatched tweak,
        or version mismatch. Treat None as a hard failure.
        """
        if record.get("version", 1) != SCHEME_VERSION:
            return None

        p, k = self._params, self._keys
        tweak = record.get("tweak", b"")
        qxp, qyp = int(record["qxp"]), int(record["qyp"])

        qx, qy = _prp_decrypt(qxp, qyp, k.prp_key, tweak, p.bin_size_m, p.prp_rounds)

        pt = _AEAD(k.aead_key).decrypt(record["nonce"], record["ct_resid"], _build_ad(qx, qy, tweak))
        if pt is None:
            return None

        rx, ry = struct.unpack(">dd", pt)
        return _unproject(qx * p.bin_size_m + rx, qy * p.bin_size_m + ry)

    def render_coordinates(self, record: Dict[str, Any]) -> Tuple[float, float]:
        """Return a jittered display coordinate without decrypting the residual.

        Requires only jitter_key — aead_key can stay in a separate vault.
        The nonce is mixed into the jitter seed so two records in the same
        shuffled tile still display at different positions.
        """
        p, k = self._params, self._keys
        B = p.bin_size_m
        x = record["qxp"] * B
        y = record["qyp"] * B

        seed = struct.pack(">ii", record["qxp"], record["qyp"]) + record["nonce"]
        h = hashlib.blake2s(key=k.jitter_key, digest_size=16)
        h.update(seed)
        js = h.digest()

        J = B * p.jitter_max_frac
        jx = (int.from_bytes(js[:8], "big") / (2**64 - 1) * 2.0 - 1.0) * J
        jy = (int.from_bytes(js[8:], "big") / (2**64 - 1) * 2.0 - 1.0) * J
        return _unproject(x + jx, y + jy)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def make_tweak(record_id: int, extra: bytes = b"") -> bytes:
        """Build a per-record tweak that binds a ciphertext to a specific record ID.

        record_id is packed as uint64 so any database primary key fits.
        The scheme version is included to block cross-version record reuse.
        """
        return struct.pack(">QI", record_id, SCHEME_VERSION) + extra

    @property
    def params(self) -> SchemeParams:
        return self._params
