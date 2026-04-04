"""
BatikPro ERP - Utility Helpers
"""
from datetime import datetime
import re

def format_rupiah(amount: float, currency: str = "Rp") -> str:
    """Format number to Indonesian Rupiah string."""
    try:
        amount = float(amount)
        if amount >= 1_000_000:
            return f"{currency} {amount/1_000_000:.1f}jt"
        return f"{currency} {amount:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return f"{currency} 0"

def format_rupiah_full(amount: float, currency: str = "Rp") -> str:
    """Format number to full Rupiah string with dots."""
    try:
        amount = float(amount)
        return f"{currency} {amount:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return f"{currency} 0"

def parse_rupiah(text: str) -> float:
    """Parse Rupiah string back to float."""
    try:
        cleaned = re.sub(r"[^0-9,.]", "", text).replace(".", "").replace(",", ".")
        return float(cleaned) if cleaned else 0.0
    except (ValueError, TypeError):
        return 0.0

def format_date(dt: datetime = None, fmt: str = "%d %b %Y") -> str:
    """Format datetime to readable string."""
    dt = dt or datetime.now()
    return dt.strftime(fmt)

def format_datetime(dt: datetime = None) -> str:
    """Format datetime with time."""
    dt = dt or datetime.now()
    return dt.strftime("%d %b %Y %H:%M")

def now_str() -> str:
    """Get current datetime as string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def now_id() -> str:
    """Get current datetime as ID-safe string."""
    return datetime.now().strftime("%Y%m%d%H%M%S")

def safe_float(value, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value) if value not in (None, "", "-") else default
    except (ValueError, TypeError):
        return default

def safe_int(value, default: int = 0) -> int:
    """Safely convert value to int."""
    try:
        return int(float(value)) if value not in (None, "", "-") else default
    except (ValueError, TypeError):
        return default

def truncate(text: str, max_len: int = 50, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if not text:
        return ""
    text = str(text)
    return text[:max_len] + suffix if len(text) > max_len else text

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return (0, 0, 0)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def is_dark_color(hex_color: str) -> bool:
    """Check if color is dark (for contrast text color)."""
    r, g, b = hex_to_rgb(hex_color)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance < 0.5

def generate_id(prefix: str, existing: list = None, field: str = "id") -> str:
    """Generate unique ID with prefix and timestamp."""
    base = f"{prefix}{now_id()}"
    if not existing:
        return base
    existing_ids = {item.get(field, "") for item in existing if isinstance(item, dict)}
    counter = 0
    candidate = base
    while candidate in existing_ids:
        counter += 1
        candidate = f"{base}_{counter}"
    return candidate

def validate_required(fields: dict) -> list:
    """Validate required fields, return list of missing field names."""
    missing = []
    for name, value in fields.items():
        if not value or (isinstance(value, str) and not value.strip()):
            missing.append(name)
    return missing

def calc_margin_percent(hpp: float, harga_jual: float) -> float:
    """Calculate margin percentage."""
    if hpp <= 0:
        return 0.0
    return ((harga_jual - hpp) / hpp) * 100

def calc_harga_jual(hpp: float, margin_pct: float) -> float:
    """Calculate selling price from HPP and margin %."""
    return hpp * (1 + margin_pct / 100)

def apply_diskon(harga: float, diskon: dict) -> float:
    """Apply discount to price."""
    tipe = diskon.get("tipe", "persen")
    nilai = safe_float(diskon.get("nilai", 0))

    if tipe == "persen" or tipe == "flash_sale" or tipe == "cashback":
        max_d = safe_float(diskon.get("max_diskon", 0))
        disc = harga * (nilai / 100)
        if max_d > 0:
            disc = min(disc, max_d)
        return max(0, harga - disc)

    elif tipe == "nominal":
        return max(0, harga - nilai)

    elif tipe == "gratis_ongkir":
        # No price reduction, just free shipping
        return harga

    elif tipe == "member":
        disc = harga * (nilai / 100)
        return max(0, harga - disc)

    elif tipe == "beli_x_gratis_y":
        # Applied at cart level; return original price per unit
        return harga

    elif tipe == "bundling":
        # Bundling discount applied as nominal
        return max(0, harga - nilai)

    return harga

JENIS_PRODUK = [
    "Kain Batik", "Kemeja Batik", "Dress Batik", "Rok Batik",
    "Selendang", "Sarung", "Taplak", "Sandal Batik",
    "Tas Batik", "Aksesoris", "Gantungan Kunci", "Lainnya"
]

JENIS_WARNA = ["Sintetis", "Alami", "Campuran"]

JENIS_MALAM = ["Parafin", "Tawon (Lebah)", "Kelebet", "Campuran"]

JENIS_KAIN = [
    "Primissima", "Prima", "Mori Biru", "Sutra", "Rayon",
    "Doby", "Paris", "Sifon", "Katun Jepang", "Lainnya"
]

ASAL_BATIK = [
    "Solo", "Yogyakarta", "Pekalongan", "Cirebon", "Madura",
    "Lasem", "Indramayu", "Banyumas", "Garut", "Jambi",
    "Palembang", "Kalimantan", "Papua", "Lainnya"
]

TINGKAT_KESULITAN = ["Mudah", "Sedang", "Sulit", "Sangat Sulit", "Masterpiece"]

STATUS_DISKON = ["Aktif", "Nonaktif", "Terjadwal", "Kedaluwarsa"]

HARI_BERLAKU = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
