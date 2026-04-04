"""
SheetsDB – Google Sheets sebagai Database Online
Menggunakan Google Sheets API v4
Struktur sheet: sama persis dengan referensi aplikasi_hpp.py namun diperluas
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Dict, Any, Optional
from datetime import datetime

# ── Nama Sheet (Tab) di Google Spreadsheet ──
SHEETS = {
    "setting":    "Setting",
    "produk":     "Master_Produk",
    "alat":       "Master_Alat",
    "bahan":      "Master_Bahan",
    "pewarna":    "Master_Pewarna",
    "malam":      "Master_Malam",
    "karyawan":   "Master_Karyawan",
    "overhead":   "Master_Overhead",
    "proses":     "Master_Proses",
    "hpp":        "Kalkulasi_HPP",
    "diskon":     "Master_Diskon",
    "transaksi":  "Transaksi",
}

# ── Header Kolom per Sheet ──
HEADERS = {
    "setting": [
        "Key", "Value"
    ],
    "produk": [
        "ID", "Nama", "Jenis_Produk", "Motif", "Asal_Daerah", "Deskripsi",
        "Dimensi", "Berat_Gram", "Halal", "Eco_Friendly", "Tingkat_Kesulitan",
        "Warna_Dominan", "Gambar_URL", "Harga_Jual", "Harga_Diskon",
        "Status", "Stok", "Tanggal_Dibuat", "Hpp_ID"
    ],
    "alat": [
        "ID", "Nama", "Kategori", "Deskripsi", "Biaya_Sewa_Per_Menit",
        "Biaya_Sewa_Per_Hari", "Status", "Catatan"
    ],
    "bahan": [
        "ID", "Nama", "Jenis", "Satuan", "Harga_Per_Satuan",
        "Supplier", "Catatan"
    ],
    "pewarna": [
        "ID", "Nama", "Jenis", "Kode_Warna", "Satuan",
        "Harga_Per_Satuan", "Halal", "Eco_Friendly", "Catatan"
    ],
    "malam": [
        "ID", "Nama", "Jenis", "Satuan", "Harga_Per_Satuan",
        "Halal", "Catatan"
    ],
    "karyawan": [
        "ID", "Nama", "Spesialisasi", "Upah_Per_Jam", "Upah_Per_Hari",
        "Status", "No_HP", "Tanggal_Masuk"
    ],
    "overhead": [
        "ID", "Nama", "Kategori", "Satuan", "Biaya_Per_Satuan", "Catatan"
    ],
    "proses": [
        "ID", "Nama", "Kategori", "Urutan", "Rata_Durasi_Menit", "Deskripsi"
    ],
    "hpp": [
        "ID", "Produk_ID", "Nama_Produk", "Jenis_Produk", "Tanggal",
        "Kuantitas", "Total_Bahan", "Total_Pewarna", "Total_Malam",
        "Total_Alat", "Total_Upah", "Total_Overhead", "Total_HPP",
        "HPP_Per_Unit", "Margin_Persen", "Harga_Jual", "Diskon_ID",
        "Harga_Final", "Detail_JSON", "Catatan"
    ],
    "diskon": [
        "ID", "Nama", "Tipe", "Nilai", "Min_Pembelian", "Max_Diskon",
        "Berlaku_Mulai", "Berlaku_Sampai", "Jam_Mulai", "Jam_Selesai",
        "Hari_Berlaku", "Kode_Promo", "Deskripsi", "Status"
    ],
    "transaksi": [
        "ID", "Produk_ID", "Hpp_ID", "Tanggal", "Kuantitas",
        "Harga_Satuan", "Diskon_ID", "Total_Bayar", "Catatan"
    ],
}

class SheetsDB:
    """
    Connector ke Google Sheets API.
    - Read: pakai API Key (public read)
    - Write: pakai Service Account / OAuth token (disimpan di Setting)
    """

    def __init__(self):
        self.spreadsheet_id: str = ""
        self.api_key: str = ""
        self.access_token: str = ""   # OAuth / Service Account token
        self._base_url = "https://sheets.googleapis.com/v4/spreadsheets"

    def configure(self, spreadsheet_id: str, api_key: str = "", access_token: str = ""):
        self.spreadsheet_id = spreadsheet_id
        self.api_key = api_key
        self.access_token = access_token

    def is_configured(self) -> bool:
        return bool(self.spreadsheet_id and (self.api_key or self.access_token))

    # ─────────────────────────────────────────────
    # LOW-LEVEL: HTTP Request
    # ─────────────────────────────────────────────
    def _get(self, endpoint: str) -> Dict:
        sep = "&" if "?" in endpoint else "?"
        auth = f"{sep}key={self.api_key}" if self.api_key else ""
        url = f"{self._base_url}/{self.spreadsheet_id}{endpoint}{auth}"
        try:
            req = urllib.request.Request(url)
            if self.access_token:
                req.add_header("Authorization", f"Bearer {self.access_token}")
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}

    def _post(self, endpoint: str, body: Dict) -> Dict:
        url = f"{self._base_url}/{self.spreadsheet_id}{endpoint}"
        if self.api_key:
            url += f"?key={self.api_key}"
        data = json.dumps(body).encode()
        try:
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Content-Type", "application/json")
            if self.access_token:
                req.add_header("Authorization", f"Bearer {self.access_token}")
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}

    def _put(self, endpoint: str, body: Dict) -> Dict:
        sep = "?" if "?" not in endpoint else "&"
        url = f"{self._base_url}/{self.spreadsheet_id}{endpoint}"
        if self.api_key:
            url += f"{sep}key={self.api_key}"
        data = json.dumps(body).encode()
        try:
            req = urllib.request.Request(url, data=data, method="PUT")
            req.add_header("Content-Type", "application/json")
            if self.access_token:
                req.add_header("Authorization", f"Bearer {self.access_token}")
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}

    # ─────────────────────────────────────────────
    # CRUD Generic
    # ─────────────────────────────────────────────
    def read_sheet(self, sheet_key: str) -> List[Dict]:
        """Baca seluruh sheet, return list of dict dengan key = header baris 1"""
        if not self.is_configured():
            return []
        sheet_name = SHEETS.get(sheet_key, sheet_key)
        resp = self._get(f"/values/{urllib.parse.quote(sheet_name)}")
        if "error" in resp or "values" not in resp:
            return []
        rows = resp["values"]
        if len(rows) < 2:
            return []
        headers = rows[0]
        result = []
        for row in rows[1:]:
            row_padded = row + [""] * (len(headers) - len(row))
            result.append(dict(zip(headers, row_padded)))
        return result

    def append_row(self, sheet_key: str, row_dict: Dict) -> bool:
        """Tambah baris baru ke sheet"""
        if not self.is_configured():
            return False
        sheet_name = SHEETS.get(sheet_key, sheet_key)
        headers = HEADERS.get(sheet_key, list(row_dict.keys()))
        values = [[str(row_dict.get(h, "")) for h in headers]]
        body = {"values": values}
        resp = self._post(
            f"/values/{urllib.parse.quote(sheet_name)}!A1:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS",
            body
        )
        return "error" not in resp

    def update_row(self, sheet_key: str, row_index: int, row_dict: Dict) -> bool:
        """Update baris tertentu (row_index = indeks data, bukan baris sheet; sheet row = row_index + 2)"""
        if not self.is_configured():
            return False
        sheet_name = SHEETS.get(sheet_key, sheet_key)
        headers = HEADERS.get(sheet_key, list(row_dict.keys()))
        sheet_row = row_index + 2
        range_notation = f"{urllib.parse.quote(sheet_name)}!A{sheet_row}:{chr(65+len(headers)-1)}{sheet_row}"
        values = [[str(row_dict.get(h, "")) for h in headers]]
        body = {"values": values, "range": range_notation, "majorDimension": "ROWS"}
        resp = self._put(
            f"/values/{range_notation}?valueInputOption=USER_ENTERED",
            body
        )
        return "error" not in resp

    def delete_row(self, sheet_key: str, row_index: int) -> bool:
        """Hapus baris dengan menggunakan batchUpdate (deleteRows request)"""
        if not self.is_configured():
            return False
        # Dapatkan sheetId numerik
        meta = self._get("")
        if "error" in meta:
            return False
        sheet_name = SHEETS.get(sheet_key, sheet_key)
        sheet_id = None
        for s in meta.get("sheets", []):
            if s["properties"]["title"] == sheet_name:
                sheet_id = s["properties"]["sheetId"]
                break
        if sheet_id is None:
            return False
        body = {
            "requests": [{
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": row_index + 1,  # +1 karena header baris 0
                        "endIndex": row_index + 2
                    }
                }
            }]
        }
        resp = self._post(":batchUpdate", body)
        return "error" not in resp

    def init_sheets(self) -> bool:
        """Buat semua sheet + header jika belum ada"""
        if not self.is_configured():
            return False
        # Buat sheet yang belum ada
        meta = self._get("")
        existing = [s["properties"]["title"] for s in meta.get("sheets", [])]
        requests = []
        for key, name in SHEETS.items():
            if name not in existing:
                requests.append({"addSheet": {"properties": {"title": name}}})
        if requests:
            self._post(":batchUpdate", {"requests": requests})
        # Tulis header
        for key, headers in HEADERS.items():
            sheet_name = SHEETS[key]
            range_notation = f"{urllib.parse.quote(sheet_name)}!A1:{chr(65+len(headers)-1)}1"
            body = {"values": [headers], "range": range_notation, "majorDimension": "ROWS"}
            self._put(f"/values/{range_notation}?valueInputOption=RAW", body)
        return True

    # ─────────────────────────────────────────────
    # Helper: generate ID
    # ─────────────────────────────────────────────
    @staticmethod
    def generate_id(prefix: str, existing: List[Dict]) -> str:
        ids = [r.get("ID", "") for r in existing if r.get("ID", "").startswith(prefix)]
        nums = []
        for i in ids:
            try:
                nums.append(int(i[len(prefix):]))
            except:
                pass
        next_num = max(nums, default=0) + 1
        return f"{prefix}{next_num:04d}"

    # ─────────────────────────────────────────────
    # OFFLINE DEMO DATA (ketika belum ada Sheets)
    # ─────────────────────────────────────────────
    def demo_produk(self) -> List[Dict]:
        return [
            {
                "ID": "PRD0001", "Nama": "Batik Mega Mendung Indigo",
                "Jenis_Produk": "Kain Batik", "Motif": "Mega Mendung",
                "Asal_Daerah": "Cirebon", "Deskripsi": "Batik tulis mega mendung klasik dengan pewarna indigo alami, motif awan 7 gradasi warna.",
                "Dimensi": "250x110cm", "Berat_Gram": "350", "Halal": "Ya",
                "Eco_Friendly": "Ya", "Tingkat_Kesulitan": "8",
                "Warna_Dominan": "#1B4F72,#2E86C1,#AED6F1",
                "Gambar_URL": "https://images.unsplash.com/photo-1558642084-fd07fae5282e?w=400",
                "Harga_Jual": "850000", "Harga_Diskon": "", "Status": "Aktif", "Stok": "5"
            },
            {
                "ID": "PRD0002", "Nama": "Kemeja Batik Parang Rusak",
                "Jenis_Produk": "Kemeja Batik", "Motif": "Parang Rusak",
                "Asal_Daerah": "Solo", "Deskripsi": "Kemeja batik cap motif parang rusak, kain primisima, cutting modern slim fit.",
                "Dimensi": "L/XL", "Berat_Gram": "250", "Halal": "Ya",
                "Eco_Friendly": "Tidak", "Tingkat_Kesulitan": "5",
                "Warna_Dominan": "#2C1A0E,#C9A84C",
                "Gambar_URL": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=400",
                "Harga_Jual": "275000", "Harga_Diskon": "249000", "Status": "Aktif", "Stok": "12"
            },
            {
                "ID": "PRD0003", "Nama": "Selendang Batik Kawung",
                "Jenis_Produk": "Selendang", "Motif": "Kawung",
                "Asal_Daerah": "Yogyakarta", "Deskripsi": "Selendang batik tulis kawung dengan pewarna sintetis multi-warna. Cocok untuk acara formal.",
                "Dimensi": "200x50cm", "Berat_Gram": "180", "Halal": "Ya",
                "Eco_Friendly": "Tidak", "Tingkat_Kesulitan": "7",
                "Warna_Dominan": "#8B4513,#D4AC0D,#1B4F72",
                "Gambar_URL": "https://images.unsplash.com/photo-1603208781930-04c8892c4c2d?w=400",
                "Harga_Jual": "195000", "Harga_Diskon": "", "Status": "Aktif", "Stok": "8"
            },
            {
                "ID": "PRD0004", "Nama": "Sandal Batik Motif Truntum",
                "Jenis_Produk": "Sandal", "Motif": "Truntum",
                "Asal_Daerah": "Solo", "Deskripsi": "Sandal handmade dengan overlay kain batik tulis motif truntum. Sol EVA premium.",
                "Dimensi": "37-42", "Berat_Gram": "320", "Halal": "Ya",
                "Eco_Friendly": "Tidak", "Tingkat_Kesulitan": "4",
                "Warna_Dominan": "#5D4037,#F57F17",
                "Gambar_URL": "https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=400",
                "Harga_Jual": "145000", "Harga_Diskon": "129000", "Status": "Aktif", "Stok": "20"
            },
            {
                "ID": "PRD0005", "Nama": "Gantungan Kunci Batik Mini",
                "Jenis_Produk": "Aksesoris", "Motif": "Sekar Jagad",
                "Asal_Daerah": "Pekalongan", "Deskripsi": "Gantungan kunci souvenir batik tulis mini dengan berbagai motif pilihan.",
                "Dimensi": "5x8cm", "Berat_Gram": "25", "Halal": "Ya",
                "Eco_Friendly": "Ya", "Tingkat_Kesulitan": "3",
                "Warna_Dominan": "#E91E63,#9C27B0,#FF9800",
                "Gambar_URL": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400",
                "Harga_Jual": "35000", "Harga_Diskon": "", "Status": "Aktif", "Stok": "50"
            },
            {
                "ID": "PRD0006", "Nama": "Batik Tulis Sogan Premium",
                "Jenis_Produk": "Kain Batik", "Motif": "Sogan Klasik",
                "Asal_Daerah": "Solo", "Deskripsi": "Batik tulis asli Solo dengan pewarna soga alami dari kulit kayu. Proses 3-4 bulan pengerjaan.",
                "Dimensi": "250x110cm", "Berat_Gram": "400", "Halal": "Ya",
                "Eco_Friendly": "Ya", "Tingkat_Kesulitan": "10",
                "Warna_Dominan": "#8B4513,#2C1A0E,#C9A84C",
                "Gambar_URL": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400",
                "Harga_Jual": "3500000", "Harga_Diskon": "", "Status": "Aktif", "Stok": "2"
            },
        ]

    def demo_diskon(self) -> List[Dict]:
        return [
            {
                "ID": "DSK0001", "Nama": "Flash Sale Tengah Malam",
                "Tipe": "persen", "Nilai": "30", "Min_Pembelian": "100000",
                "Max_Diskon": "500000", "Berlaku_Mulai": "2024-01-01",
                "Berlaku_Sampai": "2024-12-31", "Jam_Mulai": "00:00",
                "Jam_Selesai": "03:00", "Hari_Berlaku": "Senin,Selasa,Rabu,Kamis,Jumat",
                "Kode_Promo": "MIDNIGHT30", "Deskripsi": "Diskon 30% khusus tengah malam jam 00.00-03.00", "Status": "Aktif"
            },
            {
                "ID": "DSK0002", "Nama": "Promo Akhir Pekan",
                "Tipe": "persen", "Nilai": "15", "Min_Pembelian": "200000",
                "Max_Diskon": "300000", "Berlaku_Mulai": "2024-01-01",
                "Berlaku_Sampai": "2024-12-31", "Jam_Mulai": "00:00",
                "Jam_Selesai": "23:59", "Hari_Berlaku": "Sabtu,Minggu",
                "Kode_Promo": "WEEKEND15", "Deskripsi": "Diskon 15% setiap akhir pekan", "Status": "Aktif"
            },
            {
                "ID": "DSK0003", "Nama": "Voucher Nominal",
                "Tipe": "nominal", "Nilai": "50000", "Min_Pembelian": "300000",
                "Max_Diskon": "50000", "Berlaku_Mulai": "2024-01-01",
                "Berlaku_Sampai": "2024-12-31", "Jam_Mulai": "",
                "Jam_Selesai": "", "Hari_Berlaku": "Semua",
                "Kode_Promo": "HEMAT50K", "Deskripsi": "Potongan Rp 50.000 min. pembelian Rp 300.000", "Status": "Aktif"
            },
            {
                "ID": "DSK0004", "Nama": "Buy 2 Get 1",
                "Tipe": "beli_x_gratis_y", "Nilai": "2:1", "Min_Pembelian": "0",
                "Max_Diskon": "", "Berlaku_Mulai": "2024-06-01",
                "Berlaku_Sampai": "2024-06-30", "Jam_Mulai": "",
                "Jam_Selesai": "", "Hari_Berlaku": "Semua",
                "Kode_Promo": "B2G1", "Deskripsi": "Beli 2 gratis 1 untuk item sejenis", "Status": "Aktif"
            },
            {
                "ID": "DSK0005", "Nama": "Diskon Ongkir",
                "Tipe": "gratis_ongkir", "Nilai": "100", "Min_Pembelian": "500000",
                "Max_Diskon": "50000", "Berlaku_Mulai": "2024-01-01",
                "Berlaku_Sampai": "2024-12-31", "Jam_Mulai": "",
                "Jam_Selesai": "", "Hari_Berlaku": "Semua",
                "Kode_Promo": "FREEONGKIR", "Deskripsi": "Gratis ongkir min. pembelian Rp 500.000", "Status": "Aktif"
            },
            {
                "ID": "DSK0006", "Nama": "Diskon Member",
                "Tipe": "persen", "Nilai": "10", "Min_Pembelian": "0",
                "Max_Diskon": "200000", "Berlaku_Mulai": "2024-01-01",
                "Berlaku_Sampai": "2024-12-31", "Jam_Mulai": "",
                "Jam_Selesai": "", "Hari_Berlaku": "Semua",
                "Kode_Promo": "MEMBER10", "Deskripsi": "Diskon 10% khusus member terdaftar", "Status": "Aktif"
            },
        ]

    def save_setting(self, setting) -> bool:
        """Save ShopSetting to the Setting sheet (Key-Value format)."""
        import dataclasses
        if not self.is_configured():
            return False
        try:
            pairs = [
                ["nama_toko", setting.nama_toko],
                ["deskripsi", setting.deskripsi],
                ["logo_url", setting.logo_url],
                ["alamat", setting.alamat],
                ["no_hp", setting.no_hp],
                ["email", setting.email],
                ["instagram", setting.instagram],
                ["website", setting.website],
                ["footer_text", setting.footer_text],
                ["currency", setting.currency],
            ]
            # Clear sheet and rewrite
            sheet_name = SHEETS["setting"]
            url = (
                f"https://sheets.googleapis.com/v4/spreadsheets/{self._sheets_id}"
                f"/values/{sheet_name}!A:B:clear?key={self._api_key}"
            )
            self._post(url, {})
            # Write header + data
            write_url = (
                f"https://sheets.googleapis.com/v4/spreadsheets/{self._sheets_id}"
                f"/values/{sheet_name}!A1?valueInputOption=RAW&key={self._api_key}"
            )
            values = [["Key", "Value"]] + pairs
            self._put(write_url, {"values": values})
            return True
        except Exception as e:
            print(f"[SheetsDB] save_setting error: {e}")
            return False

    def save_demo_data(self, state) -> bool:
        """Push demo data from state to Google Sheets."""
        if not self.is_configured():
            return False
        try:
            for key, items in [
                ("produk", state.produk),
                ("diskon", state.diskon),
                ("alat", state.alat),
                ("bahan", state.bahan),
                ("pewarna", state.pewarna),
                ("malam", state.malam),
                ("karyawan", state.karyawan),
                ("overhead", state.overhead),
            ]:
                for item in items:
                    self.append_row(key, item)
            return True
        except Exception as e:
            print(f"[SheetsDB] save_demo_data error: {e}")
            return False

    @staticmethod
    def load_demo_to_state(state):
        """Load full demo data into app state (offline mode)."""
        db = SheetsDB()  # unconfigured instance for demo data access

        state.produk = db.demo_produk()
        state.diskon = db.demo_diskon()

        state.alat = [
            {"ID": "ALT001", "Nama": "Smart Canting Electric", "Kategori": "Canting",
             "Deskripsi": "Canting elektrik otomatis dengan pengatur suhu", "Biaya_Sewa_Per_Menit": "500",
             "Biaya_Sewa_Per_Hari": "50000", "Status": "Aktif", "Catatan": ""},
            {"ID": "ALT002", "Nama": "Canting Tradisional", "Kategori": "Canting",
             "Deskripsi": "Canting tembaga tradisional", "Biaya_Sewa_Per_Menit": "100",
             "Biaya_Sewa_Per_Hari": "10000", "Status": "Aktif", "Catatan": ""},
            {"ID": "ALT003", "Nama": "Kompor Batik", "Kategori": "Pemanas",
             "Deskripsi": "Kompor khusus untuk memanaskan malam", "Biaya_Sewa_Per_Menit": "200",
             "Biaya_Sewa_Per_Hari": "20000", "Status": "Aktif", "Catatan": ""},
            {"ID": "ALT004", "Nama": "Wajan Timah", "Kategori": "Pemanas",
             "Deskripsi": "Wajan untuk mencairkan malam batik", "Biaya_Sewa_Per_Menit": "50",
             "Biaya_Sewa_Per_Hari": "5000", "Status": "Aktif", "Catatan": ""},
            {"ID": "ALT005", "Nama": "Meja Batik", "Kategori": "Meja",
             "Deskripsi": "Meja khusus membatik ukuran 2x1m", "Biaya_Sewa_Per_Menit": "100",
             "Biaya_Sewa_Per_Hari": "15000", "Status": "Aktif", "Catatan": ""},
        ]

        state.bahan = [
            {"ID": "BHN001", "Nama": "Kain Primissima", "Jenis": "Kain",
             "Satuan": "meter", "Harga_Per_Satuan": "35000", "Supplier": "Textile Jawa", "Catatan": ""},
            {"ID": "BHN002", "Nama": "Kain Sutra Alam", "Jenis": "Kain",
             "Satuan": "meter", "Harga_Per_Satuan": "120000", "Supplier": "Sutra Nusantara", "Catatan": ""},
            {"ID": "BHN003", "Nama": "Kain Katun Jepang", "Jenis": "Kain",
             "Satuan": "meter", "Harga_Per_Satuan": "55000", "Supplier": "Impor Textile", "Catatan": ""},
            {"ID": "BHN004", "Nama": "Kain Rayon", "Jenis": "Kain",
             "Satuan": "meter", "Harga_Per_Satuan": "28000", "Supplier": "Textile Jawa", "Catatan": ""},
        ]

        state.pewarna = [
            {"ID": "PWN001", "Nama": "Naptol AS", "Jenis": "Sintetis", "Kode_Warna": "#8B4513",
             "Satuan": "gram", "Harga_Per_Satuan": "150", "Halal": "Ya", "Eco_Friendly": "Tidak", "Catatan": ""},
            {"ID": "PWN002", "Nama": "Indigosol Blue", "Jenis": "Sintetis", "Kode_Warna": "#1B4F72",
             "Satuan": "gram", "Harga_Per_Satuan": "200", "Halal": "Ya", "Eco_Friendly": "Tidak", "Catatan": ""},
            {"ID": "PWN003", "Nama": "Indigo Alam", "Jenis": "Alami", "Kode_Warna": "#2E4A7A",
             "Satuan": "gram", "Harga_Per_Satuan": "500", "Halal": "Ya", "Eco_Friendly": "Ya", "Catatan": ""},
            {"ID": "PWN004", "Nama": "Soga Tegeran", "Jenis": "Alami", "Kode_Warna": "#8B6914",
             "Satuan": "gram", "Harga_Per_Satuan": "350", "Halal": "Ya", "Eco_Friendly": "Ya", "Catatan": ""},
            {"ID": "PWN005", "Nama": "Remazol Red", "Jenis": "Sintetis", "Kode_Warna": "#C0392B",
             "Satuan": "gram", "Harga_Per_Satuan": "180", "Halal": "Ya", "Eco_Friendly": "Tidak", "Catatan": ""},
        ]

        state.malam = [
            {"ID": "MLM001", "Nama": "Malam Parafin", "Jenis": "Parafin",
             "Satuan": "kg", "Harga_Per_Satuan": "25000", "Halal": "Ya", "Catatan": ""},
            {"ID": "MLM002", "Nama": "Malam Tawon", "Jenis": "Tawon (Lebah)",
             "Satuan": "kg", "Harga_Per_Satuan": "80000", "Halal": "Ya", "Catatan": "Premium"},
            {"ID": "MLM003", "Nama": "Malam Kelebet", "Jenis": "Kelebet",
             "Satuan": "kg", "Harga_Per_Satuan": "45000", "Halal": "Ya", "Catatan": ""},
            {"ID": "MLM004", "Nama": "Malam Campuran", "Jenis": "Campuran",
             "Satuan": "kg", "Harga_Per_Satuan": "35000", "Halal": "Ya", "Catatan": "Parafin + Tawon"},
        ]

        state.karyawan = [
            {"ID": "KRY001", "Nama": "Ibu Sari Dewi", "Spesialisasi": "Canting Tulis",
             "Upah_Per_Jam": "15000", "Upah_Per_Hari": "80000",
             "Status": "Aktif", "No_HP": "081234567890", "Tanggal_Masuk": "2020-01-15"},
            {"ID": "KRY002", "Nama": "Bapak Joko", "Spesialisasi": "Pewarnaan",
             "Upah_Per_Jam": "12000", "Upah_Per_Hari": "70000",
             "Status": "Aktif", "No_HP": "082345678901", "Tanggal_Masuk": "2019-06-01"},
            {"ID": "KRY003", "Nama": "Mbak Retno", "Spesialisasi": "Finishing & QC",
             "Upah_Per_Jam": "13000", "Upah_Per_Hari": "75000",
             "Status": "Aktif", "No_HP": "083456789012", "Tanggal_Masuk": "2021-03-10"},
        ]

        state.overhead = [
            {"ID": "OVH001", "Nama": "Listrik Bengkel", "Kategori": "Utilitas",
             "Biaya_Per_Unit": "1500", "Satuan": "kWh", "Catatan": ""},
            {"ID": "OVH002", "Nama": "Air PDAM", "Kategori": "Utilitas",
             "Biaya_Per_Unit": "8000", "Satuan": "m3", "Catatan": ""},
            {"ID": "OVH003", "Nama": "Gas LPG 3kg", "Kategori": "Bahan Bakar",
             "Biaya_Per_Unit": "22000", "Satuan": "tabung", "Catatan": ""},
            {"ID": "OVH004", "Nama": "Sewa Bengkel", "Kategori": "Sewa",
             "Biaya_Per_Unit": "500000", "Satuan": "bulan", "Catatan": ""},
        ]
