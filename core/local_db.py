"""
LocalDB - SQLite lokal untuk BatikPro
Path disesuaikan untuk Android dan desktop
"""
import sqlite3
import json
import os
import threading
import base64
import datetime
from typing import List, Dict
import platform

def get_db_path():
    """Get appropriate database path based on platform"""
    if platform.system() == 'Android':
        # Untuk Android, gunakan context.getFilesDir()
        # Flet di Android menyediakan get_app_storage_dir()
        try:
            from flet import get_app_storage_dir
            return os.path.join(get_app_storage_dir(), "batikpro.db")
        except:
            # Fallback untuk Android
            return os.path.join(os.path.expanduser("~"), "batikpro.db")
    else:
        # Untuk desktop, gunakan Documents folder
        return os.path.join(os.path.expanduser("~"), "Documents", "batikpro.db")

DB_PATH = get_db_path()
print(f"[LocalDB] Using database path: {DB_PATH}")

# Pastikan direktori ada
db_dir = os.path.dirname(DB_PATH)
if db_dir:
    try:
        os.makedirs(db_dir, exist_ok=True)
        print(f"[LocalDB] Created directory: {db_dir}")
    except Exception as e:
        print(f"[LocalDB] Error creating directory: {e}")

TABLES = ["produk","alat","bahan","pewarna","malam",
          "karyawan","overhead","proses","hpp","diskon","transaksi",
          "admin","login_history"]

class LocalDB:
    def __init__(self):
        self._lock = threading.Lock()
        self._init_db()
        print(f"[LocalDB] Database path: {DB_PATH}")

    def _conn(self):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._lock:
            conn = self._conn()
            try:
                for t in TABLES:
                    conn.execute(f"""CREATE TABLE IF NOT EXISTS {t} (
                        id TEXT PRIMARY KEY,
                        data TEXT NOT NULL,
                        updated_at TEXT,
                        synced INTEGER DEFAULT 0
                    )""")
                conn.execute("""CREATE TABLE IF NOT EXISTS app_setting (
                    key TEXT PRIMARY KEY, value TEXT
                )""")
                conn.commit()
                print(f"[LocalDB] Tables created: {TABLES}")
            except Exception as e:
                print(f"[LocalDB] Init error: {e}")
            finally:
                conn.close()

    def get_all(self, table: str) -> List[Dict]:
        if table not in TABLES: 
            return []
        with self._lock:
            conn = self._conn()
            try:
                rows = conn.execute(f"SELECT data FROM {table}").fetchall()
                return [json.loads(r["data"]) for r in rows]
            except Exception as e:
                print(f"[LocalDB.get_all] {table}: {e}")
                return []
            finally:
                conn.close()

    def upsert(self, table: str, record: Dict) -> bool:
        if table not in TABLES: 
            return False
        rid = record.get("ID") or record.get("id") or record.get("Key","")
        if not rid:
            rid = f"{table.upper()}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{abs(hash(str(record))) % 1000000}"
            record["ID"] = rid
        with self._lock:
            conn = self._conn()
            try:
                conn.execute(
                    f"INSERT OR REPLACE INTO {table} (id,data,updated_at,synced) VALUES(?,?,?,0)",
                    (rid, json.dumps(record, ensure_ascii=False), datetime.datetime.now().isoformat())
                )
                conn.commit()
                print(f"[LocalDB.upsert] {table}: {rid} saved")
                return True
            except Exception as e:
                print(f"[LocalDB.upsert] {table}: {e}")
                return False
            finally:
                conn.close()

    def delete(self, table: str, rid: str) -> bool:
        if table not in TABLES: 
            return False
        with self._lock:
            conn = self._conn()
            try:
                conn.execute(f"DELETE FROM {table} WHERE id=?", (rid,))
                conn.commit()
                return True
            except Exception as e:
                print(f"[LocalDB.delete] {table}: {e}")
                return False
            finally:
                conn.close()

    def replace_all(self, table: str, records: List[Dict]) -> bool:
        if table not in TABLES: 
            return False
        with self._lock:
            conn = self._conn()
            try:
                conn.execute(f"DELETE FROM {table}")
                for r in records:
                    rid = r.get("ID") or r.get("id","")
                    if not rid:
                        rid = f"{table.upper()}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{abs(hash(str(r))) % 1000000}"
                        r["ID"] = rid
                    conn.execute(
                        f"INSERT INTO {table} (id,data,updated_at,synced) VALUES(?,?,?,1)",
                        (rid, json.dumps(r, ensure_ascii=False), datetime.datetime.now().isoformat())
                    )
                conn.commit()
                print(f"[LocalDB.replace_all] {table}: {len(records)} records saved")
                return True
            except Exception as e:
                print(f"[LocalDB.replace_all] {table}: {e}")
                return False
            finally:
                conn.close()

    def count(self, table: str) -> int:
        with self._lock:
            conn = self._conn()
            try:
                return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            except:
                return 0
            finally:
                conn.close()

    def is_empty(self) -> bool:
        return self.count("produk") == 0

    def get_unsynced(self, table: str) -> List[Dict]:
        with self._lock:
            conn = self._conn()
            try:
                rows = conn.execute(f"SELECT data FROM {table} WHERE synced=0").fetchall()
                return [json.loads(r["data"]) for r in rows]
            except:
                return []
            finally:
                conn.close()

    def mark_synced(self, table: str):
        with self._lock:
            conn = self._conn()
            try:
                conn.execute(f"UPDATE {table} SET synced=1")
                conn.commit()
            except:
                pass
            finally:
                conn.close()

    def save_kv(self, key: str, value: str):
        with self._lock:
            conn = self._conn()
            try:
                conn.execute("INSERT OR REPLACE INTO app_setting(key,value) VALUES(?,?)", (key, value))
                conn.commit()
            finally:
                conn.close()

    def get_kv(self, key: str, default: str = "") -> str:
        with self._lock:
            conn = self._conn()
            try:
                row = conn.execute("SELECT value FROM app_setting WHERE key=?", (key,)).fetchone()
                return row["value"] if row else default
            except:
                return default
            finally:
                conn.close()

    def save_shop_setting(self, s):
        fields = ["nama_toko","deskripsi","logo_url","alamat","no_hp",
                  "email","instagram","website","footer_text","currency",
                  "sheets_id","sheets_api_key","sync_enabled","sync_interval_min"]
        for f in fields:
            value = getattr(s, f, "")
            self.save_kv(f, str(value))

    def load_shop_setting(self, s):
        s.nama_toko        = self.get_kv("nama_toko", "BatikPro Store")
        s.deskripsi        = self.get_kv("deskripsi", "Toko Batik Berkualitas")
        s.logo_url         = self.get_kv("logo_url", "")
        s.alamat           = self.get_kv("alamat", "")
        s.no_hp            = self.get_kv("no_hp", "")
        s.email            = self.get_kv("email", "")
        s.instagram        = self.get_kv("instagram", "")
        s.website          = self.get_kv("website", "")
        s.footer_text      = self.get_kv("footer_text", "© 2024 BatikPro")
        s.currency         = self.get_kv("currency", "Rp")
        s.sheets_id        = self.get_kv("sheets_id", "")
        s.sheets_api_key   = self.get_kv("sheets_api_key", "")
        s.sync_enabled     = self.get_kv("sync_enabled", "False") == "True"
        
        try:
            s.sync_interval_min = int(self.get_kv("sync_interval_min", "30"))
        except:
            s.sync_interval_min = 30
        return s

    def db_path(self) -> str:
        return DB_PATH