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

__all__ = [
    "MapEncryption", "SchemeParams", "SCHEME_VERSION",
    "haversine_m", "edd", "mnnd", "dbscan_f1",
]

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

try:
    import h3 as _h3_lib
    _H3_AVAILABLE = True
except ImportError:  # pragma: no cover
    _H3_AVAILABLE = False


# ---------------------------------------------------------------------------
# Public configuration
# ---------------------------------------------------------------------------

@dataclass
class SchemeParams:
    """Tuning parameters shared by all participants (encoder, decoder, display tier).

    These are NOT stored per-record; treat them as system configuration.
    All parties must agree on identical values.
    """
    bin_size_m: int = 250           # grid tile side-length in metres (Mercator path)
    jitter_max_frac: float = 0.25   # display wobble: up to +-(bin_size_m * frac) metres
    prp_rounds: int = 10            # Feistel rounds (>= 8 recommended)
    tile_system: str = 'mercator'   # 'mercator' | 'h3'
    h3_resolution: int = 9          # H3 resolution level (0–15); used when tile_system='h3'


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
# Associated Data construction  (Mercator path)
# ---------------------------------------------------------------------------

def _build_ad(qx: int, qy: int, tweak: bytes) -> bytes:
    # Length-prefix the tweak so (qy=23, tweak=b'6') != (qy=236, tweak=b'').
    return struct.pack(">iiI", qx, qy, len(tweak)) + tweak


# ---------------------------------------------------------------------------
# H3 DGGS helpers
# ---------------------------------------------------------------------------

def _h3_snap(lat: float, lon: float, resolution: int) -> str:
    """Return the H3 cell ID string containing (lat, lon) at given resolution."""
    if not _H3_AVAILABLE:
        raise ImportError("h3-py is required for tile_system='h3': pip install h3")
    return _h3_lib.latlng_to_cell(lat, lon, resolution)


def _h3_residual(lat: float, lon: float, cell: str) -> Tuple[float, float]:
    """Intra-cell residual in Web Mercator metres from the H3 cell centroid.

    Returns (rx, ry) where rx = x - cx, ry = y - cy in EPSG:3857 metres.
    The same coordinate system used by the Mercator residual, so the AEAD
    layer (struct.pack('>dd', rx, ry)) is identical for both tile systems.
    """
    clat, clon = _h3_lib.cell_to_latlng(cell)
    x,  y  = _project(lat,  lon)
    cx, cy = _project(clat, clon)
    return x - cx, y - cy


def _h3_recover(cell: str, rx: float, ry: float) -> Tuple[float, float]:
    """Recover (lat, lon) from an H3 cell and its Web Mercator residual."""
    clat, clon = _h3_lib.cell_to_latlng(cell)
    cx, cy = _project(clat, clon)
    return _unproject(cx + rx, cy + ry)


def _h3_prp_encrypt(cell_int: int, prp_key: bytes, tweak: bytes,
                    rounds: int) -> int:
    """Balanced XOR Feistel over the two 32-bit halves of a 64-bit H3 cell integer.

    Round function: BLAKE2s(key=prp_key, data=b'h3prp|'+tweak+pack(r, R))[:4 bytes].
    Output is an opaque 64-bit integer stored as cell_int_p in the record.
    It does NOT need to be a valid H3 cell — analogous to qxp/qyp in the
    Mercator path, which also don't correspond to real geographic tiles.
    """
    L = (cell_int >> 32) & 0xFFFF_FFFF
    R = cell_int & 0xFFFF_FFFF
    prefix = b'h3prp|' + tweak
    for r in range(rounds):
        h = hashlib.blake2s(key=prp_key, digest_size=32)
        h.update(prefix + struct.pack(">II", r, R))
        F = int.from_bytes(h.digest()[:4], "big")
        L, R = R, L ^ F
    return (L << 32) | R


def _h3_prp_decrypt(cell_int_p: int, prp_key: bytes, tweak: bytes,
                    rounds: int) -> int:
    """Inverse of _h3_prp_encrypt — recovers the original 64-bit cell integer.

    Inverse step derivation: forward pass sets (L_new, R_new) = (R_old, L_old ^ F(R_old)).
    Given (L_new, R_new): R_old = L_new; F uses R_old = L_new; L_old = R_new ^ F(L_new).
    So each reversed round applies: L, R = R ^ F(L), L.
    """
    L = (cell_int_p >> 32) & 0xFFFF_FFFF
    R = cell_int_p & 0xFFFF_FFFF
    prefix = b'h3prp|' + tweak
    for r in reversed(range(rounds)):
        h = hashlib.blake2s(key=prp_key, digest_size=32)
        h.update(prefix + struct.pack(">II", r, L))
        F = int.from_bytes(h.digest()[:4], "big")
        L, R = R ^ F, L
    return (L << 32) | R


def _build_ad_h3(cell: str, resolution: int, tweak: bytes) -> bytes:
    """Associated data for H3 records.

    Binds ciphertext to: real cell ID (64-bit int) | resolution (1 byte) |
    tweak length (4 bytes) | tweak bytes. Parallel structure to _build_ad.
    """
    cell_int = int(cell, 16)
    return struct.pack(">QBI", cell_int, resolution, len(tweak)) + tweak


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class MapEncryption:
    """Reversible encryption of geographic coordinates.

    Instantiate once per deployment with a master key loaded from a secrets
    manager (AWS KMS, HashiCorp Vault, GCP Secret Manager, …). Never hard-code
    or commit the master key.

    Example — Mercator (default)
    ----------------------------
    >>> enc = MapEncryption(master_key)
    >>> tweak = MapEncryption.make_tweak(record_id=42)
    >>> record = enc.encode(40.758, -73.985, tweak=tweak)
    >>> lat, lon = enc.decode(record)
    >>> display_lat, display_lon = enc.render_coordinates(record)

    Example — H3 DGGS
    -----------------
    >>> params = SchemeParams(tile_system='h3', h3_resolution=9)
    >>> enc = MapEncryption(master_key, params)
    >>> record = enc.encode(40.758, -73.985)
    >>> lat, lon = enc.decode(record)
    """

    def __init__(self, master_key: bytes, params: Optional[SchemeParams] = None):
        self._params = params or SchemeParams()
        self._keys = _derive_keys(master_key)

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def encode(self, lat: float, lon: float, tweak: bytes = b"") -> Dict[str, Any]:
        """Encrypt a geographic coordinate and return a storable record.

        Mercator record keys: qxp, qyp, nonce, ct_resid, tweak, version
        H3 record keys:       cell_int_p, nonce, ct_resid, tweak, version,
                              tile_system, h3_resolution
        """
        if self._params.tile_system == 'h3':
            return self._encode_h3(lat, lon, tweak)
        return self._encode_mercator(lat, lon, tweak)

    def decode(self, record: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """Decrypt a record and return (lat, lon), or None on any failure.

        Returns None for wrong key, tampered ciphertext, mismatched tweak,
        or version mismatch. Treat None as a hard failure.
        """
        if record.get("version", 1) != SCHEME_VERSION:
            return None
        if record.get("tile_system") == "h3":
            return self._decode_h3(record)
        return self._decode_mercator(record)

    def render_coordinates(self, record: Dict[str, Any]) -> Tuple[float, float]:
        """Return a jittered display coordinate without decrypting the residual.

        Requires only jitter_key — aead_key can stay in a separate vault.
        For H3 records the permuted cell_int_p (not a valid H3 cell) drives
        the display location; for Mercator records, qxp/qyp drive it.
        """
        if record.get("tile_system") == "h3":
            return self._render_h3(record)
        return self._render_mercator(record)

    # ------------------------------------------------------------------
    # Mercator path (internal)
    # ------------------------------------------------------------------

    def _encode_mercator(self, lat: float, lon: float, tweak: bytes) -> Dict[str, Any]:
        p, k = self._params, self._keys

        x, y = _project(lat, lon)
        qx = int(round(x / p.bin_size_m))
        qy = int(round(y / p.bin_size_m))
        rx = x - qx * p.bin_size_m
        ry = y - qy * p.bin_size_m

        qxp, qyp = _prp_encrypt(qx, qy, k.prp_key, tweak, p.bin_size_m, p.prp_rounds)

        nonce = secrets.token_bytes(12)
        ct = _AEAD(k.aead_key).encrypt(
            nonce, struct.pack(">dd", rx, ry), _build_ad(qx, qy, tweak))

        return {
            "qxp": int(qxp),
            "qyp": int(qyp),
            "nonce": nonce,
            "ct_resid": ct,
            "tweak": tweak,
            "version": SCHEME_VERSION,
        }

    def _decode_mercator(self, record: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        p, k = self._params, self._keys
        tweak = record.get("tweak", b"")
        qxp, qyp = int(record["qxp"]), int(record["qyp"])

        qx, qy = _prp_decrypt(qxp, qyp, k.prp_key, tweak, p.bin_size_m, p.prp_rounds)

        pt = _AEAD(k.aead_key).decrypt(
            record["nonce"], record["ct_resid"], _build_ad(qx, qy, tweak))
        if pt is None:
            return None

        rx, ry = struct.unpack(">dd", pt)
        return _unproject(qx * p.bin_size_m + rx, qy * p.bin_size_m + ry)

    def _render_mercator(self, record: Dict[str, Any]) -> Tuple[float, float]:
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
    # H3 path (internal)
    # ------------------------------------------------------------------

    def _encode_h3(self, lat: float, lon: float, tweak: bytes) -> Dict[str, Any]:
        if not _H3_AVAILABLE:
            raise ImportError("tile_system='h3' requires h3-py: pip install h3")
        p, k = self._params, self._keys

        cell = _h3_snap(lat, lon, p.h3_resolution)
        rx, ry = _h3_residual(lat, lon, cell)

        cell_int = int(cell, 16)
        cell_int_p = _h3_prp_encrypt(cell_int, k.prp_key, tweak, p.prp_rounds)

        nonce = secrets.token_bytes(12)
        ct = _AEAD(k.aead_key).encrypt(
            nonce, struct.pack(">dd", rx, ry),
            _build_ad_h3(cell, p.h3_resolution, tweak))

        return {
            "cell_int_p": int(cell_int_p),
            "nonce": nonce,
            "ct_resid": ct,
            "tweak": tweak,
            "version": SCHEME_VERSION,
            "tile_system": "h3",
            "h3_resolution": p.h3_resolution,
        }

    def _decode_h3(self, record: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        if not _H3_AVAILABLE:
            raise ImportError("tile_system='h3' requires h3-py: pip install h3")
        p, k = self._params, self._keys
        tweak = record.get("tweak", b"")
        resolution = record.get("h3_resolution", p.h3_resolution)

        cell_int_p = int(record["cell_int_p"])
        cell_int = _h3_prp_decrypt(cell_int_p, k.prp_key, tweak, p.prp_rounds)
        cell = f'{cell_int:015x}'

        pt = _AEAD(k.aead_key).decrypt(
            record["nonce"], record["ct_resid"],
            _build_ad_h3(cell, resolution, tweak))
        if pt is None:
            return None

        rx, ry = struct.unpack(">dd", pt)
        return _h3_recover(cell, rx, ry)

    def _render_h3(self, record: Dict[str, Any]) -> Tuple[float, float]:
        """H3 display: map permuted cell_int_p bits to a Mercator coordinate + jitter.

        Uses only jitter_key. The permuted integer's two 32-bit halves are
        mapped to x ∈ [-HALF_WORLD, +HALF_WORLD] and y ∈ [-MAX_Y, +MAX_Y],
        placing the display point at a pseudorandom global location unrelated
        to the original — identical privacy model to the Mercator render path.
        """
        p, k = self._params, self._keys
        cell_int_p = int(record["cell_int_p"])
        L = (cell_int_p >> 32) & 0xFFFF_FFFF
        R = cell_int_p & 0xFFFF_FFFF

        # MAX_Y: Mercator y at the pole clamp latitude (≈ HALF_WORLD)
        _MAX_Y = _R_EARTH * math.log(
            math.tan(math.pi / 4.0 + math.radians(85.05112878) / 2.0))
        x = (L / 0xFFFF_FFFF) * 2.0 * _HALF_WORLD - _HALF_WORLD
        y = (R / 0xFFFF_FFFF) * 2.0 * _MAX_Y - _MAX_Y

        seed = struct.pack(">Q", cell_int_p) + record["nonce"]
        h = hashlib.blake2s(key=k.jitter_key, digest_size=16)
        h.update(seed)
        js = h.digest()

        J = p.bin_size_m * p.jitter_max_frac
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


# ---------------------------------------------------------------------------
# Evaluation metrics  (require scipy / scikit-learn — optional dependencies)
# ---------------------------------------------------------------------------

def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres between two WGS84 coordinate pairs."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2.0 * _R_EARTH * math.asin(math.sqrt(a))


def edd(true_coords: list, display_coords: list) -> float:
    """Expected Displacement Distance: mean haversine distance (metres) between
    true and display coordinate pairs (same-order sequences of (lat, lon) tuples).
    """
    if len(true_coords) != len(display_coords):
        raise ValueError("true_coords and display_coords must have the same length")
    return sum(
        haversine_m(t[0], t[1], d[0], d[1])
        for t, d in zip(true_coords, display_coords)
    ) / len(true_coords)


def mnnd(coords: list) -> float:
    """Mean Nearest-Neighbour Distance (metres) for a set of (lat, lon) coordinates.

    Projects to Web Mercator for distance computation. Requires scipy.
    """
    try:
        import numpy as np
        from scipy.spatial import cKDTree
    except ImportError as exc:
        raise ImportError("mnnd() requires scipy: pip install scipy") from exc
    xy = np.array([_project(lat, lon) for lat, lon in coords])
    tree = cKDTree(xy)
    dists, _ = tree.query(xy, k=2)   # k=2: [self-distance=0, nearest neighbour]
    return float(dists[:, 1].mean())


def dbscan_f1(
    true_coords: list,
    display_coords: list,
    eps_m: float = 400.0,
    min_samples: int = 5,
) -> Dict[str, Any]:
    """DBSCAN cluster-detection evaluation: precision, recall, and F1.

    Applies DBSCAN (eps in metres, Web Mercator coordinates) to both the true and
    display coordinate sets. Cluster quality is measured by pairwise same-cluster
    agreement (Rand-index style): precision is the fraction of display same-cluster
    pairs that are also true same-cluster pairs; recall is the fraction of true
    same-cluster pairs recovered in the display clustering. Noise points (label -1)
    are excluded from all pair counts.

    Requires scikit-learn and numpy.
    """
    try:
        import numpy as np
        from sklearn.cluster import DBSCAN
    except ImportError as exc:
        raise ImportError(
            "dbscan_f1() requires scikit-learn: pip install scikit-learn"
        ) from exc

    true_xy = np.array([_project(lat, lon) for lat, lon in true_coords])
    disp_xy = np.array([_project(lat, lon) for lat, lon in display_coords])

    true_labels = DBSCAN(eps=eps_m, min_samples=min_samples).fit_predict(true_xy)
    disp_labels = DBSCAN(eps=eps_m, min_samples=min_samples).fit_predict(disp_xy)

    tl = true_labels[:, None]
    dl = disp_labels[:, None]
    true_same = (tl == tl.T) & (tl != -1) & (tl.T != -1)
    disp_same = (dl == dl.T) & (dl != -1) & (dl.T != -1)

    upper = np.triu(np.ones(true_same.shape, dtype=bool), k=1)
    tp = int(np.sum(true_same & disp_same & upper))
    fp = int(np.sum(~true_same & disp_same & upper))
    fn = int(np.sum(true_same & ~disp_same & upper))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (
        2.0 * precision * recall / (precision + recall)
        if (precision + recall) > 0 else 0.0
    )

    return {
        "precision":          round(precision, 4),
        "recall":             round(recall, 4),
        "f1":                 round(f1, 4),
        "n_true_clusters":    int(len(set(true_labels)  - {-1})),
        "n_display_clusters": int(len(set(disp_labels)  - {-1})),
        "n_noise_true":       int(np.sum(true_labels  == -1)),
        "n_noise_display":    int(np.sum(disp_labels  == -1)),
    }
