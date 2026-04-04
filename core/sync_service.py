"""
SyncService – Background sync antara SQLite lokal dan Google Sheets
- Read dari lokal: instant
- Sync ke Sheets: background thread, tidak blokir UI
"""

import threading
import time
from datetime import datetime
from typing import Callable, Optional

class SyncService:
    """Background sync SQLite ↔ Google Sheets"""

    TABLES = ["produk", "alat", "bahan", "pewarna", "malam",
              "karyawan", "overhead", "diskon", "hpp"]

    def __init__(self, local_db, sheets_db, state, on_status: Optional[Callable] = None):
        self.local_db = local_db
        self.sheets_db = sheets_db
        self.state = state
        self.on_status = on_status  # callback(msg, is_error)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_sync: Optional[datetime] = None
        self._lock = threading.Lock()

    def start(self, interval_minutes: int = 30):
        """Start background sync thread"""
        if self._running:
            return
        self._running = True
        self._interval = interval_minutes * 60
        self._thread = threading.Thread(target=self._loop, daemon=True, name="SyncThread")
        self._thread.start()
        self._notify(f"🔄 Auto-sync aktif setiap {interval_minutes} menit")

    def stop(self):
        """Stop background sync"""
        self._running = False
        self._notify("⏹️ Auto-sync dihentikan")

    def sync_now(self, direction: str = "push"):
        """Trigger immediate sync (non-blocking)"""
        t = threading.Thread(
            target=self._do_sync,
            args=(direction,),
            daemon=True,
            name="SyncNow"
        )
        t.start()

    def _loop(self):
        """Background loop"""
        # Initial sync after 5 sec
        time.sleep(5)
        while self._running:
            self._do_sync("push")
            # Sleep in small chunks to allow fast stop
            for _ in range(int(self._interval)):
                if not self._running:
                    break
                time.sleep(1)

    def _do_sync(self, direction: str = "push"):
        """Actual sync logic"""
        if not self.sheets_db.is_configured():
            return

        with self._lock:
            try:
                self._notify("☁️ Menyinkronkan data...")
                count = 0

                if direction in ("push", "both"):
                    # Push unsynced local records to Sheets
                    for table in self.TABLES:
                        unsynced = self.local_db.get_unsynced(table)
                        for record in unsynced:
                            self.sheets_db.append_row(table, record)
                            count += 1
                        if unsynced:
                            self.local_db.mark_synced(table)

                if direction in ("pull", "both"):
                    # Pull from Sheets → overwrite local
                    for table in self.TABLES:
                        rows = self.sheets_db.read_sheet(table)
                        if rows:
                            self.local_db.replace_all(table, rows)
                            # Update state in memory too
                            target = "hpp_list" if table == "hpp" else table
                            if hasattr(self.state, target):
                                setattr(self.state, target, rows)
                            count += len(rows)

                self._last_sync = datetime.now()
                ts = self._last_sync.strftime("%H:%M:%S")
                self._notify(f"✅ Sync selesai {ts} ({count} data)")

            except Exception as e:
                self._notify(f"❌ Sync gagal: {e}", is_error=True)

    def _notify(self, msg: str, is_error: bool = False):
        """Send status to UI callback"""
        print(f"[Sync] {msg}")
        if self.on_status:
            try:
                self.on_status(msg, is_error)
            except Exception:
                pass

    @property
    def last_sync_str(self) -> str:
        if self._last_sync:
            return self._last_sync.strftime("%d/%m/%Y %H:%M")
        return "Belum pernah"

    @property
    def is_running(self) -> bool:
        return self._running
