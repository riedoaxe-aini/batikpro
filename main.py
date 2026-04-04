"""
BatikPro ERP v3.2 - Fast startup, minimal blocking
"""
import flet as ft
import datetime
from core.app_state import AppState
from core.theme import BatikTheme
from pages.login_page import LoginPage
from core.router import Router

# Global state untuk login
current_user = None
login_attempts = []

def main(page: ft.Page):
    print("[main] start")
    page.title = "BatikPro ERP"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = BatikTheme.get_theme()
    page.bgcolor = BatikTheme.BG_PRIMARY
    page.padding = 0

    # Fullscreen and responsive settings
    try:
        page.window.maximized = True
        page.window.resizable = True
        page.window.full_screen = False
    except Exception:
        pass

    state = AppState()
    print("[main] state created")

    # Responsive
    def _resize(e=None):
        w = page.width or 480
        h = page.height or 900
        state.screen_width = w
        state.screen_height = h
        state.is_landscape = w > h
        state.is_tablet = w >= 600
        state.is_tv = w >= 1200
        state.grid_cols = 5 if state.is_tv else (4 if state.is_tablet and state.is_landscape else (3 if state.is_tablet else 2))

    page.on_resized = _resize
    _resize()

    # Buat router sementara
    temp_router = Router(page, state, None)
    
    # Tampilkan login page
    print("[main] Showing login page...")
    login_page = LoginPage(page, state, None, temp_router)
    page.controls.append(login_page.build())
    page.update()
    
    import threading
    
    def _init_db_and_nav():
        global current_user, login_attempts
        print("[init] starting DB init")
        try:
            from core.local_db import LocalDB
            ldb = LocalDB()
            print(f"[init] LocalDB ready at {ldb.db_path()}")
        except Exception as e:
            print(f"[init] LocalDB error: {e}")
            ldb = None

        try:
            from core.sheets_db import SheetsDB
            sdb = SheetsDB()
            print("[init] SheetsDB ready")
        except Exception as e:
            print(f"[init] SheetsDB error: {e}")
            sdb = _FallbackDB()

        state.local_db = ldb
        state.sheets_db = sdb

        # Load setting from local DB
        if ldb:
            try:
                ldb.load_shop_setting(state.setting)
                print("[init] setting loaded")
                
                # Load admin data
                admins = ldb.get_all("admin") or []
                print(f"[init] Found {len(admins)} admin(s)")
                
                if not admins:
                    # Create default admin
                    default_admin = {
                        "ID": "ADM0001",
                        "username": "admin",
                        "password": "admin123",
                        "nama": "Administrator",
                        "role": "Admin",
                        "status": "Aktif",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    ldb.upsert("admin", default_admin)
                    admins = [default_admin]
                    print("[init] Default admin created: admin / admin123")
                else:
                    for admin in admins:
                        print(f"[init] Admin exists: {admin.get('username')}")
                
                state.admins = admins
                
                # Load login history
                login_attempts = ldb.get_all("login_history") or []
                
            except Exception as e:
                print(f"[init] setting load error: {e}")

        # Configure Sheets if credentials exist
        if state.setting.sheets_id and state.setting.sheets_api_key:
            try:
                sdb.configure(state.setting.sheets_id, state.setting.sheets_api_key)
            except Exception as e:
                print(f"[init] sheets configure error: {e}")

        # Load data
        print("[init] loading data")
        _load_data(state, ldb, sdb)
        print(f"[init] loaded {len(state.produk)} produk")

        # Start sync if enabled
        if state.setting.sync_enabled and sdb.is_configured():
            try:
                from core.sync_service import SyncService
                sync_svc = SyncService(ldb, sdb, state)
                sync_svc.start(state.setting.sync_interval_min)
                state.sync_service = sync_svc
            except Exception as e:
                print(f"[init] sync service error: {e}")

        # Update router dengan db
        temp_router.db = sdb
        
        def refresh_login():
            page.controls.clear()
            updated_login = LoginPage(page, state, sdb, temp_router)
            page.controls.append(updated_login.build())
            page.update()
            print("[init] Login page refreshed")
        
        page.run_thread(refresh_login)

    threading.Thread(target=_init_db_and_nav, daemon=True).start()
    print("[main] init thread started")

def _load_data(state, ldb, sdb):
    """Load data from local DB or demo"""
    try:
        if ldb:
            # Load all data from database
            state.produk = ldb.get_all("produk") or []
            state.alat = ldb.get_all("alat") or []
            state.bahan = ldb.get_all("bahan") or []
            state.pewarna = ldb.get_all("pewarna") or []
            state.malam = ldb.get_all("malam") or []
            state.karyawan = ldb.get_all("karyawan") or []
            state.overhead = ldb.get_all("overhead") or []
            state.hpp_list = ldb.get_all("hpp") or []
            state.diskon = ldb.get_all("diskon") or []
            state.proses = ldb.get_all("proses") or []
            state.admins = ldb.get_all("admin") or []
            
            # If no produk data, load demo
            if not state.produk:
                print("[load_data] No data found, loading demo...")
                _load_demo(state, sdb)
                # Save demo to database
                for produk in state.produk:
                    ldb.upsert("produk", produk)
                for proses in state.proses:
                    ldb.upsert("proses", proses)
                if state.admins:
                    for admin in state.admins:
                        ldb.upsert("admin", admin)
            else:
                print(f"[load_data] Loaded {len(state.produk)} produk from database")
        else:
            _load_demo(state, sdb)
    except Exception as e:
        print(f"[load_data] error: {e}, falling back to demo")
        _load_demo(state, sdb)

def _load_demo(state, sdb):
    """Load demo data"""
    try:
        state.produk = sdb.demo_produk()
        state.diskon = sdb.demo_diskon()
    except Exception:
        state.produk = []
        state.diskon = []
    
    # Demo products
    state.produk = [
        {"ID":"PRD0001","Nama":"Batik Tulis Mega Mendung","Jenis_Produk":"Kain Batik",
         "Harga_Jual":"450000","Status":"Aktif","Halal":"Ya","Eco_Friendly":"Ya",
         "Preorder":"Tidak","Special":"Ya","Premium":"Ya","Gambar_URL":"",
         "Deskripsi":"Batik tulis halus dengan motif mega mendung","Stok":10},
        {"ID":"PRD0002","Nama":"Batik Cap Kawung","Jenis_Produk":"Kain Batik",
         "Harga_Jual":"250000","Status":"Aktif","Halal":"Ya","Eco_Friendly":"Ya",
         "Preorder":"Tidak","Special":"Tidak","Premium":"Tidak","Gambar_URL":"","Stok":15},
        {"ID":"PRD0003","Nama":"Kemeja Batik Pria","Jenis_Produk":"Kemeja Batik",
         "Harga_Jual":"350000","Status":"Aktif","Halal":"Ya","Eco_Friendly":"Tidak",
         "Preorder":"Ya","Special":"Tidak","Premium":"Tidak","Gambar_URL":"","Stok":5},
        {"ID":"PRD0004","Nama":"Selendang Batik","Jenis_Produk":"Selendang",
         "Harga_Jual":"150000","Status":"Aktif","Halal":"Ya","Eco_Friendly":"Ya","Stok":8},
        {"ID":"PRD0005","Nama":"Sandal Batik","Jenis_Produk":"Sandal",
         "Harga_Jual":"120000","Status":"Aktif","Halal":"Ya","Eco_Friendly":"Ya","Stok":20},
        {"ID":"PRD0006","Nama":"Aksesoris Batik","Jenis_Produk":"Aksesoris",
         "Harga_Jual":"50000","Status":"Aktif","Halal":"Ya","Eco_Friendly":"Ya","Stok":30},
    ]
    
    state.alat = [
        {"ID":"ALT0001","Nama":"Canting Tradisional","Biaya_Sewa_Per_Menit":"50","Status":"Aktif"},
        {"ID":"ALT0002","Nama":"Smart Canting IoT","Biaya_Sewa_Per_Menit":"150","Status":"Aktif"},
        {"ID":"ALT0003","Nama":"Kompor Batik","Biaya_Sewa_Per_Menit":"80","Status":"Aktif"},
    ]
    state.bahan = [
        {"ID":"BHN0001","Nama":"Kain Primisima","Jenis":"Kain","Satuan":"meter","Harga_Per_Satuan":"45000"},
        {"ID":"BHN0002","Nama":"Kain Sutra","Jenis":"Kain","Satuan":"meter","Harga_Per_Satuan":"150000"},
    ]
    state.pewarna = [
        {"ID":"PWN0001","Nama":"Napthol AS","Jenis":"Sintetis","Satuan":"gram","Harga_Per_Satuan":"120","Kode_Warna":"#C0392B"},
        {"ID":"PWN0002","Nama":"Indigosol","Jenis":"Sintetis","Satuan":"gram","Harga_Per_Satuan":"150","Kode_Warna":"#1B4F72"},
    ]
    state.malam = [
        {"ID":"MLM0001","Nama":"Malam Parafin","Jenis":"Parafin","Satuan":"kg","Harga_Per_Satuan":"35000"},
    ]
    state.karyawan = [
        {"ID":"KRY0001","Nama":"Siti Rahayu","Spesialisasi":"Pembatik Tulis","Upah_Per_Jam":"25000","Status":"Aktif"},
        {"ID":"KRY0002","Nama":"Budi Santoso","Spesialisasi":"Pewarnaan","Upah_Per_Jam":"20000","Status":"Aktif"},
    ]
    state.overhead = [
        {"ID":"OVH0001","Nama":"Listrik","Kategori":"Utilitas","Satuan":"kWh","Biaya_Per_Satuan":"1500"},
    ]
    state.proses = [
        {"ID":"PRS0001","Nama":"Pencucian","Kategori":"Pencucian","Durasi_Menit":30,"Biaya_Per_Proses":5000,"Status":"Aktif"},
        {"ID":"PRS0002","Nama":"Pemotongan","Kategori":"Pemotongan","Durasi_Menit":15,"Biaya_Per_Proses":3000,"Status":"Aktif"},
    ]
    state.hpp_list = []

class _FallbackDB:
    """Minimal DB fallback jika SheetsDB gagal import"""
    def is_configured(self): return False
    def configure(self, *a, **kw): pass
    def read_sheet(self, *a, **kw): return []
    def append_row(self, *a, **kw): pass
    def demo_produk(self): return []
    def demo_diskon(self): return []

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")