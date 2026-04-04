import flet as ft
from core.theme import BatikTheme
from components.widgets import (
    batik_appbar, primary_button, outline_button,
    show_snack, show_confirm_dialog, section_header
)

class AdminPage:
    def __init__(self, page: ft.Page, app_state, router, sheets_db):
        self.page = page
        self.state = app_state
        self.router = router
        self.db = sheets_db

    def build(self):
        return ft.Column(
            controls=[
                batik_appbar("🛡️ Admin Panel",
                             on_back=lambda _: self.router.go_back(),
                             subtitle="Manajemen sistem & data"),
                ft.Container(
                    content=ft.ListView(
                        controls=self._build_content(),
                        spacing=12,
                        padding=ft.padding.all(16),
                    ),
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        )

    def _build_content(self):
        s = self.state

        def reset_all(_):
            def do_reset():
                s.produk.clear()
                s.alat.clear()
                s.bahan.clear()
                s.pewarna.clear()
                s.malam.clear()
                s.karyawan.clear()
                s.overhead.clear()
                s.proses.clear()
                s.hpp_list.clear()
                s.diskon.clear()
                show_snack(self.page, "✅ Semua data berhasil di-reset!")
                self.page.update()
            show_confirm_dialog(
                self.page,
                "Reset Semua Data",
                "⚠️ Ini akan menghapus SEMUA data di memori. Data di Sheets tidak berubah. Lanjutkan?",
                do_reset,
            )

        def load_demo(_):
            from core.sheets_db import SheetsDB
            SheetsDB.load_demo_to_state(s)
            show_snack(self.page, "✅ Data demo berhasil dimuat!")

        def sync_from_sheets(_):
            if not self.db.is_configured():
                show_snack(self.page, "⚠️ Google Sheets belum dikonfigurasi!", BatikTheme.WARNING)
                return
            keys = ["produk", "alat", "bahan", "pewarna", "malam", "karyawan", "overhead", "diskon", "hpp"]
            count = 0
            for key in keys:
                rows = self.db.read_sheet(key)
                if rows:
                    getattr(s, key if key != "hpp" else "hpp_list", []).clear()
                    target = s.hpp_list if key == "hpp" else getattr(s, key, [])
                    target.extend(rows)
                    count += len(rows)
            show_snack(self.page, f"✅ {count} baris berhasil disinkronisasi dari Sheets!")

        def export_json(_):
            import json, os
            data = {
                "produk": s.produk,
                "alat": s.alat,
                "bahan": s.bahan,
                "pewarna": s.pewarna,
                "malam": s.malam,
                "karyawan": s.karyawan,
                "overhead": s.overhead,
                "hpp_list": s.hpp_list,
                "diskon": s.diskon,
            }
            path = os.path.expanduser("~/batikpro_export.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            show_snack(self.page, f"✅ Data diekspor ke {path}")

        # Summary stats
        stats = [
            ("📦 Produk", len(s.produk), BatikTheme.PRIMARY),
            ("🔧 Alat", len(s.alat), BatikTheme.SECONDARY),
            ("🧵 Bahan", len(s.bahan), "#8E44AD"),
            ("🎨 Pewarna", len(s.pewarna), "#E67E22"),
            ("🕯️ Malam", len(s.malam), "#795548"),
            ("👷 Karyawan", len(s.karyawan), BatikTheme.SUCCESS),
            ("💡 Overhead", len(s.overhead), "#E74C3C"),
            ("🧮 HPP", len(s.hpp_list), BatikTheme.ACCENT),
            ("🏷️ Diskon", len(s.diskon), "#16A085"),
        ]

        return [
            # Data summary
            ft.Container(
                content=ft.Column([
                    ft.Text("📊 Ringkasan Data", size=15, weight="w700",
                            color=BatikTheme.PRIMARY),
                    ft.Divider(color=BatikTheme.DIVIDER),
                    ft.GridView(
                        controls=[
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(icon_label, size=18, text_align="center"),
                                    ft.Text(str(count), size=20, weight="w700",
                                            color=color, text_align="center"),
                                    ft.Text(icon_label.split(" ", 1)[-1], size=10,
                                            color=BatikTheme.TEXT_SECONDARY,
                                            text_align="center"),
                                ], horizontal_alignment="center",
                                   spacing=2),
                                bgcolor=BatikTheme.BG_PRIMARY,
                                padding=ft.padding.all(10),
                                border=ft.border.all(1, BatikTheme.DIVIDER),
                            )
                            for icon_label, count, color in stats
                        ],
                        runs_count=3,
                        max_extent=120,
                        spacing=8,
                        run_spacing=8,
                        height=220,
                    ),
                ], spacing=10),
                bgcolor=BatikTheme.BG_CARD,
                padding=ft.padding.all(16),
                border=ft.border.all(1, BatikTheme.DIVIDER),
            ),

            # Data actions
            ft.Container(
                content=ft.Column([
                    ft.Text("🗄️ Manajemen Data", size=15, weight="w700",
                            color=BatikTheme.PRIMARY),
                    ft.Divider(color=BatikTheme.DIVIDER),
                    _action_row("☁️ Sync dari Google Sheets", "Ambil data terbaru dari Sheets",
                                sync_from_sheets, BatikTheme.SECONDARY),
                    _action_row("🎭 Muat Data Demo", "Reset dengan data demo lengkap",
                                load_demo, BatikTheme.SUCCESS),
                    _action_row("📤 Export JSON", "Simpan semua data ke file JSON",
                                export_json, "#8E44AD"),
                    _action_row("🗑️ Reset Memori", "Hapus semua data dari memori",
                                reset_all, BatikTheme.ERROR),
                ], spacing=10),
                bgcolor=BatikTheme.BG_CARD,
                padding=ft.padding.all(16),
                border=ft.border.all(1, BatikTheme.DIVIDER),
            ),

            # Connection status
            ft.Container(
                content=ft.Column([
                    ft.Text("🔗 Status Koneksi", size=15, weight="w700",
                            color=BatikTheme.PRIMARY),
                    ft.Divider(color=BatikTheme.DIVIDER),
                    ft.Row([
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if self.db.is_configured() else ft.Icons.CANCEL,
                            color=BatikTheme.SUCCESS if self.db.is_configured() else BatikTheme.ERROR,
                            size=20,
                        ),
                        ft.Text(
                            "Google Sheets API: " + ("Terhubung" if self.db.is_configured() else "Belum dikonfigurasi"),
                            size=13,
                            color=BatikTheme.SUCCESS if self.db.is_configured() else BatikTheme.ERROR,
                            weight="w600",
                        ),
                    ], spacing=8),
                    ft.Text(
                        f"Sheets ID: {self.state.setting.sheets_id or '-'}",
                        size=11, color=BatikTheme.TEXT_SECONDARY,
                        font_family="monospace",
                    ),
                    ft.Container(height=4),
                    outline_button("⚙️ Ke Pengaturan Database",
                                   lambda _: self.router.navigate("setting")),
                ], spacing=8),
                bgcolor=BatikTheme.BG_CARD,
                padding=ft.padding.all(16),
                border=ft.border.all(1, BatikTheme.DIVIDER),
            ),

            # Quick nav
            ft.Container(
                content=ft.Column([
                    ft.Text("🚀 Navigasi Cepat", size=15, weight="w700",
                            color=BatikTheme.PRIMARY),
                    ft.Divider(color=BatikTheme.DIVIDER),
                    ft.Wrap(
                        spacing=8, run_spacing=8,
                        controls=[
                            _nav_chip(label, dest, self.router)
                            for label, dest in [
                                ("🏪 Toko", "home"),
                                ("🖼️ Galeri", "gallery"),
                                ("🧮 HPP", "hpp_wizard"),
                                ("📋 Master Data", "crud_master"),
                                ("🏷️ Diskon", "diskon"),
                                ("📊 Laporan", "laporan"),
                                ("⚙️ Setting", "setting"),
                            ]
                        ],
                    ),
                ], spacing=10),
                bgcolor=BatikTheme.BG_CARD,
                padding=ft.padding.all(16),
                border=ft.border.all(1, BatikTheme.DIVIDER),
            ),

            ft.Container(height=16),
        ]

def _action_row(title: str, desc: str, on_click, color: str):
    return ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text(title, size=13, weight="w600", color=BatikTheme.TEXT_PRIMARY),
                ft.Text(desc, size=11, color=BatikTheme.TEXT_SECONDARY),
            ], expand=True, spacing=2),
            ft.Container(
                        content=ft.Row([ft.Text("Jalankan", color="white", weight="w600", size=12)], spacing=4, tight=True),
                        bgcolor=T.PRIMARY,
                        padding=ft.padding.symmetric(8, 14),
                        on_click=on_click, ink=True,
                    ),
        ], vertical_alignment="center"),
        bgcolor=BatikTheme.BG_PRIMARY,
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border=ft.border.all(1, BatikTheme.DIVIDER),
    )

def _nav_chip(label: str, dest: str, router):
    return ft.Container(
        content=ft.Text(label, size=12, weight="w500", color=BatikTheme.PRIMARY),
        bgcolor=BatikTheme.BG_PRIMARY,
        padding=ft.padding.symmetric(horizontal=14, vertical=8),
        border=ft.border.all(1.5, BatikTheme.PRIMARY),
        on_click=lambda _: router.navigate(dest),
        ink=True,
    )
