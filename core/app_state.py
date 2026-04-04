"""
AppState – Central State Management
Menyimpan semua data runtime aplikasi BatikPro
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class ShopSetting:
    nama_toko: str = "BatikPro Store"
    deskripsi: str = "Toko Batik Berkualitas Premium"
    logo_url: str = ""
    alamat: str = ""
    no_hp: str = ""
    email: str = ""
    instagram: str = ""
    website: str = ""
    footer_text: str = "© 2024 BatikPro – Warisan Budaya Bangsa"
    currency: str = "Rp"
    sheets_id: str = ""
    sheets_api_key: str = ""
    sync_enabled: bool = False
    sync_interval_min: int = 30
    theme_image_url: str = ""

class AppState:
    """Singleton state untuk seluruh aplikasi"""

    def __init__(self):
        # ── Data Master ──
        self.produk: List[Dict] = []   # Master Produk Batik
        self.alat: List[Dict] = []     # Master Alat
        self.bahan: List[Dict] = []    # Master Bahan (kain, dll)
        self.pewarna: List[Dict] = []  # Master Pewarna
        self.malam: List[Dict] = []    # Master Malam
        self.karyawan: List[Dict] = [] # Master Karyawan
        self.overhead: List[Dict] = [] # Master Overhead
        self.proses: List[Dict] = []   # Master Proses

        # ── Transaksi ──
        self.hpp_list: List[Dict] = [] # Kalkulasi HPP tersimpan
        self.diskon: List[Dict] = []   # Master Diskon

        # ── Setting ──
        self.setting = ShopSetting()

        # ── Admin ──
        self.admins: List[Dict] = []   # Data Admin
        self.current_user: Optional[Dict] = None  # User yang sedang login

        # ── UI State ──
        self.current_page: str = "splash"
        self.current_produk_id: Optional[str] = None
        self.cart: List[Dict] = []
        self.search_query: str = ""
        self.filter_jenis: str = "Semua"
        self.is_loading: bool = False
        self.is_logged_in: bool = False
        self.admin_mode: bool = False

        # Responsive Screen
        self.screen_width: float = 480
        self.screen_height: float = 900
        self.is_landscape: bool = False
        self.is_tablet: bool = False
        self.is_tv: bool = False
        self.grid_cols: int = 2

        # ── Database references ──
        self.local_db = None
        self.sheets_db = None
        self.sync_service = None

        # ── Temp HPP Wizard ──
        self.hpp_wizard: Dict = self._empty_hpp_wizard()

    def _empty_hpp_wizard(self) -> Dict:
        return {
            "produk_id": None,
            "nama_produk": "",
            "jenis_produk": "Kain Batik",
            "deskripsi": "",
            "gambar_urls": [],
            
            # Komponen biaya
            "alat_list": [],
            "bahan_list": [],
            "pewarna_list": [],
            "malam_list": [],
            "karyawan_list": [],
            "overhead_list": [],
            
            # Biaya tambahan
            "biaya_desain": 0.0,
            "biaya_pengemasan": 0.0,
            "biaya_pengiriman": 0.0,
            "biaya_pajak": 0.0,
            "biaya_lainnya": 0.0,
            
            # Diskon
            "diskon_persen": 0.0,
            "diskon_nominal": 0.0,
            "diskon_aktif": None,
            
            # Keuntungan
            "margin_persen": 30.0,
            "keuntungan_nominal": 0.0,
            
            # Kuantitas
            "lama_pengerjaan_hari": 1,
            "kuantitas": 1,
            
            # Kalkulasi
            "total_bahan": 0.0,
            "total_pewarna": 0.0,
            "total_malam": 0.0,
            "total_alat": 0.0,
            "total_upah": 0.0,
            "total_overhead": 0.0,
            "total_biaya_tambahan": 0.0,
            "total_biaya_produksi": 0.0,
            "hpp_per_unit": 0.0,
            "harga_jual": 0.0,
            "harga_setelah_diskon": 0.0,
            "harga_final": 0.0,
            "keuntungan_akhir": 0.0,
            "roi": 0.0,
            
            "tanggal": datetime.now().isoformat(),
        }

    def reset_hpp_wizard(self):
        self.hpp_wizard = self._empty_hpp_wizard()

    def hitung_hpp(self):
        """Hitung ulang HPP dengan semua komponen"""
        w = self.hpp_wizard
        
        w["total_bahan"] = sum(i.get("subtotal", 0) for i in w["bahan_list"])
        w["total_pewarna"] = sum(i.get("subtotal", 0) for i in w["pewarna_list"])
        w["total_malam"] = sum(i.get("subtotal", 0) for i in w["malam_list"])
        w["total_alat"] = sum(i.get("subtotal", 0) for i in w["alat_list"])
        w["total_upah"] = sum(i.get("subtotal", 0) for i in w["karyawan_list"])
        w["total_overhead"] = sum(i.get("subtotal", 0) for i in w["overhead_list"])
        
        w["total_biaya_tambahan"] = (
            w.get("biaya_desain", 0) +
            w.get("biaya_pengemasan", 0) +
            w.get("biaya_pengiriman", 0) +
            w.get("biaya_pajak", 0) +
            w.get("biaya_lainnya", 0)
        )
        
        w["total_biaya_produksi"] = (
            w["total_bahan"] + w["total_pewarna"] + w["total_malam"] +
            w["total_alat"] + w["total_upah"] + w["total_overhead"] +
            w["total_biaya_tambahan"]
        )
        
        kuantitas = max(w["kuantitas"], 1)
        w["hpp_per_unit"] = w["total_biaya_produksi"] / kuantitas
        
        margin = w["margin_persen"] / 100
        w["harga_jual"] = w["hpp_per_unit"] * (1 + margin)
        
        w["harga_setelah_diskon"] = self._apply_diskon(w["harga_jual"], w)
        
        w["keuntungan_akhir"] = w["harga_setelah_diskon"] - w["hpp_per_unit"]
        w["keuntungan_nominal"] = w["keuntungan_akhir"] * kuantitas
        
        if w["hpp_per_unit"] > 0:
            w["roi"] = (w["keuntungan_akhir"] / w["hpp_per_unit"]) * 100
        else:
            w["roi"] = 0
        
        w["harga_final"] = w["harga_setelah_diskon"]
        
        return w

    def _apply_diskon(self, harga: float, wizard: Dict) -> float:
        if wizard.get("diskon_persen", 0) > 0:
            harga = harga * (1 - wizard["diskon_persen"] / 100)
        
        if wizard.get("diskon_nominal", 0) > 0:
            harga = max(0, harga - wizard["diskon_nominal"])
        
        diskon = wizard.get("diskon_aktif")
        if diskon:
            tipe = diskon.get("tipe", "persen")
            nilai = diskon.get("nilai", 0)
            if tipe == "persen":
                harga = harga * (1 - nilai / 100)
            elif tipe == "nominal":
                harga = max(0, harga - nilai)
        
        return max(0, harga)

    def get_produk_by_id(self, pid: str) -> Optional[Dict]:
        return next((p for p in self.produk if p.get("ID") == pid), None)

    def format_currency(self, value: float) -> str:
        return f"{self.setting.currency} {value:,.0f}".replace(",", ".")