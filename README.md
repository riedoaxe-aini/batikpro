# 🎨 BatikPro ERP v2.0

> Aplikasi manajemen & kalkulasi HPP produk batik berbasis Android/Tablet/SmartTV
> Dibangun dengan **Flet (Python)** + **Google Sheets** sebagai database online

---

## ✨ Fitur Lengkap

| Fitur | Keterangan |
|---|---|
| 🏪 **Galeri Toko** | Tampilan produk seperti toko online (header, grid, footer) |
| 🧮 **Wizard HPP 8 Langkah** | Kalkulasi harga pokok produksi secara detail |
| 📊 **Laporan PDF** | Cetak tabel produk & HPP dengan ReportLab |
| 🏷️ **8 Tipe Diskon** | Flash sale, bundling, member, voucher, dll |
| ☁️ **Google Sheets DB** | Database online real-time via API v4 |
| 📱 **Multi Platform** | Android smartphone, tablet, SmartTV |
| 🎨 **Tema Batik** | Warna soga, indigo, emas – khas batik nusantara |

---

## 📁 Struktur Proyek

```
batikpro/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── core/
│   ├── theme.py               # BatikTheme (warna, shadow, font)
│   ├── app_state.py           # AppState & ShopSetting dataclass
│   ├── sheets_db.py           # Google Sheets API connector
│   └── router.py              # Page router
├── components/
│   └── widgets.py             # Reusable UI components
├── pages/
│   ├── splash_page.py         # Loading screen + init data
│   ├── home_page.py           # Halaman utama (header+galeri+footer)
│   ├── gallery_page.py        # Galeri penuh dengan filter & sort
│   ├── product_detail_page.py # Detail produk
│   ├── hpp_wizard_page.py     # Wizard kalkulasi HPP 8 langkah
│   ├── crud_master_page.py    # CRUD semua master data (7 tab)
│   ├── diskon_page.py         # Manajemen diskon
│   ├── laporan_page.py        # Laporan & export PDF
│   ├── setting_page.py        # Pengaturan toko & database
│   └── admin_page.py          # Admin panel & tools
├── utils/
│   └── helpers.py             # Helper functions
└── assets/                    # Logo, gambar statis
```

---

## 🚀 Cara Menjalankan

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan di Desktop (Development)

```bash
cd batikpro
python main.py
```

### 3. Build APK Android

```bash
# Install flet CLI
pip install flet

# Build APK
flet build apk

# Atau untuk bundle AAB (Google Play)
flet build aab
```

---

## ☁️ Setup Google Sheets Database

### Langkah-langkah:

1. **Buat Google Spreadsheet** baru di [sheets.google.com](https://sheets.google.com)

2. **Salin Spreadsheet ID** dari URL:
   ```
   https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
   ```

3. **Aktifkan Google Sheets API:**
   - Buka [console.cloud.google.com](https://console.cloud.google.com)
   - Buat project baru atau pilih existing
   - Enable **Google Sheets API**
   - Buat **API Key** (untuk read-only)

4. **Untuk operasi write (CRUD):**
   - Buat **Service Account** di Google Cloud
   - Download JSON key
   - Share Spreadsheet ke email service account

5. **Konfigurasi di aplikasi:**
   - Buka menu **Pengaturan → Tab Database**
   - Isi Spreadsheet ID dan API Key
   - Klik **Uji Koneksi**
   - Klik **Init Sheet Headers**

### Struktur Sheet (12 sheet otomatis):

| Sheet | Fungsi |
|---|---|
| Setting | Pengaturan toko |
| Master_Produk | Data produk batik |
| Master_Alat | Alat produksi |
| Master_Bahan | Bahan / kain |
| Master_Pewarna | Pewarna sintetis & alami |
| Master_Malam | Malam batik |
| Master_Karyawan | Data karyawan |
| Master_Overhead | Biaya overhead |
| Master_Proses | Proses produksi |
| Kalkulasi_HPP | Hasil kalkulasi HPP |
| Master_Diskon | Data diskon & promo |
| Transaksi | Riwayat transaksi |

---

## 🧮 Komponen HPP

Wizard HPP menghitung:

```
HPP = Bahan Kain + Pewarna + Malam + Sewa Alat + Upah Karyawan + Overhead
Harga Jual = HPP × (1 + Margin%)
Harga Final = Harga Jual - Diskon
```

### 8 Langkah Wizard HPP:

1. **Info Produk** – nama, jenis, kuantitas
2. **Alat** – pilih alat + durasi menit
3. **Bahan Kain** – pilih bahan + jumlah meter
4. **Pewarna** – pilih pewarna + gram
5. **Malam** – pilih malam + kg
6. **Upah Karyawan** – pilih karyawan + jam kerja
7. **Overhead** – pilih overhead + jumlah
8. **Ringkasan** – breakdown + slider margin + diskon

---

## 🏷️ Tipe Diskon

| Tipe | Keterangan |
|---|---|
| Persen (%) | Potongan persentase dengan max cap |
| Nominal (Rp) | Potongan nominal tetap |
| Flash Sale | Diskon % dengan batasan waktu |
| Beli X Gratis Y | Beli sekian unit gratis |
| Gratis Ongkir | Subsidi ongkos kirim |
| Cashback | Kembalian % dalam bentuk kredit |
| Bundling | Paket produk dengan harga spesial |
| Member | Diskon eksklusif anggota |

---

## 🎨 Tema Warna Batik

| Warna | Hex | Makna |
|---|---|---|
| Soga Coklat | `#7B3F00` | Warna batik tradisional |
| Indigo Batik | `#1B4F72` | Warna nila alami |
| Emas | `#C9A84C` | Kemewahan batik premium |
| Krem Kain | `#FDF8F2` | Warna kain mori |

---

## 📱 Platform Support

- ✅ Android Smartphone (Portrait 480×900)
- ✅ Android Tablet (Landscape adaptif)
- ✅ SmartTV (Landscape fullscreen)
- ✅ Desktop Windows/Mac/Linux (Development)
- ✅ Web Browser (via `flet run --web`)

---

## 🛠️ Teknologi

- **[Flet](https://flet.dev)** – Flutter-based Python UI
- **Google Sheets API v4** – Database online
- **ReportLab** – Generate PDF laporan
- **Python 3.11+** – Backend logic

---

## 📄 Lisensi

Dibuat untuk pengrajin batik Indonesia 🇮🇩

**Bangga Produk Batik Nusantara!**
