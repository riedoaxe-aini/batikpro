"""
SettingPage - Pengaturan aplikasi dengan Backup & Load Database
"""

import flet as ft
import os
import shutil
import datetime
import json
from core.theme import BatikTheme
from components.widgets import (
    batik_appbar, BatikBottomNav, batik_textfield,
    primary_button, outline_button, show_snack, show_confirm_dialog
)

class SettingPage:
    def __init__(self, page: ft.Page, app_state, sheets_db, router, **kwargs):
        self.page = page
        self.state = app_state
        self.db = sheets_db
        self.router = router
        self.tab_index = 0

        # Refs for Toko fields
        self.r_nama = ft.Ref[ft.TextField]()
        self.r_deskripsi = ft.Ref[ft.TextField]()
        self.r_logo_url = ft.Ref[ft.TextField]()
        self.r_alamat = ft.Ref[ft.TextField]()
        self.r_hp = ft.Ref[ft.TextField]()
        self.r_email = ft.Ref[ft.TextField]()
        self.r_ig = ft.Ref[ft.TextField]()
        self.r_web = ft.Ref[ft.TextField]()
        self.r_footer = ft.Ref[ft.TextField]()
        self.r_currency = ft.Ref[ft.TextField]()

        # Refs for Sheets API fields
        self.r_sheets_id = ft.Ref[ft.TextField]()
        self.r_api_key = ft.Ref[ft.TextField]()

        # Refs for Theme
        self.r_theme_url = ft.Ref[ft.TextField]()
        
        # Color picker refs
        self.color_primary = ft.Ref[ft.TextField]()
        self.color_secondary = ft.Ref[ft.TextField]()
        self.color_accent = ft.Ref[ft.TextField]()

        # Connection status ref
        self.r_status_icon = ft.Ref[ft.Icon]()
        self.r_status_text = ft.Ref[ft.Text]()
        self.r_status_container = ft.Ref[ft.Container]()

        self.s = self.state.setting
        self._tab_content = ft.Ref[ft.Column]()
        
        # Logo preview
        self.logo_preview_ref = ft.Ref[ft.Image]()
        # Theme preview
        self.theme_preview_ref = ft.Ref[ft.Container]()
        
        # Database path
        self.db_path = self.state.local_db.db_path() if self.state.local_db else ""
        
        # Load saved theme colors from database
        self._load_theme_colors()

    def _load_theme_colors(self):
        """Load saved theme colors from database"""
        if self.state.local_db:
            primary = self.state.local_db.get_kv("theme_primary", "")
            secondary = self.state.local_db.get_kv("theme_secondary", "")
            accent = self.state.local_db.get_kv("theme_accent", "")
            
            if primary and primary.startswith('#'):
                BatikTheme.PRIMARY = primary
            if secondary and secondary.startswith('#'):
                BatikTheme.SECONDARY = secondary
            if accent and accent.startswith('#'):
                BatikTheme.ACCENT = accent
            
            # Update gradient
            BatikTheme.GRADIENT_PRIMARY = ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[BatikTheme.PRIMARY, BatikTheme._darken_color_rgb(BatikTheme._hex_to_rgb(BatikTheme.PRIMARY), 0.2)]
            )

    def _save_theme_colors(self):
        """Save theme colors to database"""
        if self.state.local_db:
            self.state.local_db.save_kv("theme_primary", BatikTheme.PRIMARY)
            self.state.local_db.save_kv("theme_secondary", BatikTheme.SECONDARY)
            self.state.local_db.save_kv("theme_accent", BatikTheme.ACCENT)
            print(f"[Theme] Saved: PRIMARY={BatikTheme.PRIMARY}, SECONDARY={BatikTheme.SECONDARY}, ACCENT={BatikTheme.ACCENT}")

    def build(self):
        def on_nav(index):
            pages = ["gallery", "home", "hpp_wizard", "crud_master", "setting"]
            if index != 4:
                self.router.navigate(pages[index])

        TAB_LABELS = ["🏪 Toko", "🔗 Database", "🎨 Tema", "💾 Backup/Load", "📜 History", "ℹ️ Tentang"]
        tab_buttons = []
        
        for i, label in enumerate(TAB_LABELS):
            is_selected = (i == self.tab_index)
            
            def make_tap_handler(idx):
                def handler(_):
                    self.tab_index = idx
                    self._update_tab_content()
                    for j, btn in enumerate(tab_buttons):
                        if j == idx:
                            btn.bgcolor = BatikTheme.PRIMARY
                            btn.content.controls[0].color = BatikTheme.TEXT_WHITE
                        else:
                            btn.bgcolor = BatikTheme.BG_CARD
                            btn.content.controls[0].color = BatikTheme.TEXT_SECONDARY
                    self.page.update()
                return handler
            
            tab_btn = ft.Container(
                content=ft.Column([
                    ft.Text(label, size=BatikTheme.FONT_SM, weight="w600", 
                           color=BatikTheme.TEXT_WHITE if is_selected else BatikTheme.TEXT_SECONDARY),
                    ft.Container(
                        height=2,
                        bgcolor=BatikTheme.ACCENT if is_selected else ft.Colors.TRANSPARENT,
                        width=40,
                    ),
                ], spacing=4, horizontal_alignment="center"),
                bgcolor=BatikTheme.PRIMARY if is_selected else BatikTheme.BG_CARD,
                padding=ft.padding.symmetric(12, 16),
                border_radius=ft.BorderRadius(8, 8, 0, 0),
                on_click=make_tap_handler(i),
                expand=True,
            )
            tab_buttons.append(tab_btn)
        
        tab_bar = ft.Container(
            content=ft.Row(tab_buttons, spacing=2),
            bgcolor=BatikTheme.BG_CARD,
            border=ft.border.only(bottom=ft.BorderSide(1, BatikTheme.DIVIDER)),
        )

        tab_content = ft.Column(ref=self._tab_content, expand=True)
        self._update_tab_content()

        return ft.Container(
            content=ft.Column(
                controls=[
                    batik_appbar("⚙️ Pengaturan", subtitle="Konfigurasi aplikasi BatikPro"),
                    tab_bar,
                    tab_content,
                    BatikBottomNav(current_index=4, on_change=on_nav).build(),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )

    def _update_tab_content(self):
        if not self._tab_content.current:
            return
        
        self._tab_content.current.controls.clear()
        
        if self.tab_index == 0:
            self._tab_content.current.controls.append(self._tab_toko())
        elif self.tab_index == 1:
            self._tab_content.current.controls.append(self._tab_database())
        elif self.tab_index == 2:
            self._tab_content.current.controls.append(self._tab_theme())
        elif self.tab_index == 3:
            self._tab_content.current.controls.append(self._tab_backup_load())
        elif self.tab_index == 4:
            self._tab_content.current.controls.append(self._tab_history())
        elif self.tab_index == 5:
            self._tab_content.current.controls.append(self._tab_tentang())

    def _tab_toko(self):
        s = self.s

        def save_toko(_):
            s.nama_toko = self.r_nama.current.value or s.nama_toko
            s.deskripsi = self.r_deskripsi.current.value or s.deskripsi
            s.logo_url = self.r_logo_url.current.value or ""
            s.alamat = self.r_alamat.current.value or ""
            s.no_hp = self.r_hp.current.value or ""
            s.email = self.r_email.current.value or ""
            s.instagram = self.r_ig.current.value or ""
            s.website = self.r_web.current.value or ""
            s.footer_text = self.r_footer.current.value or ""
            s.currency = self.r_currency.current.value or "Rp"
            
            if self.state.local_db:
                self.state.local_db.save_shop_setting(s)
                self._save_all_data()
            show_snack(self.page, "✅ Pengaturan toko berhasil disimpan!")

        def preview_logo(_):
            url = self.r_logo_url.current.value
            if url and url.startswith("http"):
                self.logo_preview_ref.current.src = url
                self.logo_preview_ref.current.visible = True
            else:
                self.logo_preview_ref.current.visible = False
            self.page.update()

        logo_preview = ft.Container(
            content=ft.Column([
                ft.Image(
                    ref=self.logo_preview_ref,
                    src="",
                    width=80, height=80,
                    border_radius=12,
                    fit="contain",
                    visible=False,
                ),
                ft.Text("Belum ada logo", size=11, color=BatikTheme.TEXT_HINT, 
                        visible=not bool(s.logo_url)),
            ], horizontal_alignment="center"),
            width=100, height=100,
            bgcolor=BatikTheme.BG_SECONDARY,
            border=ft.border.all(1, BatikTheme.DIVIDER),
        )

        if s.logo_url:
            self.logo_preview_ref.current.src = s.logo_url
            self.logo_preview_ref.current.visible = True

        return ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Container(height=16),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Logo Toko", size=13, weight="w600",
                                    color=BatikTheme.TEXT_SECONDARY),
                            ft.Row([
                                logo_preview,
                                ft.Column([
                                    batik_textfield("URL Logo", ref=self.r_logo_url,
                                                    value=s.logo_url,
                                                    hint="https://...",
                                                    on_blur=preview_logo),
                                    ft.Text("Masukkan URL gambar logo toko (Google Drive, Imgur, dll)",
                                            size=10, color=BatikTheme.TEXT_HINT),
                                ], expand=True, spacing=4),
                            ], spacing=12, vertical_alignment="start"),
                        ], spacing=8),
                        bgcolor=BatikTheme.BG_CARD,
                        padding=ft.padding.all(16),
                        border=ft.border.all(1, BatikTheme.DIVIDER),
                    ),

                    ft.Container(height=12),

                    _section_card("🏪 Identitas Toko", [
                        batik_textfield("Nama Toko *", ref=self.r_nama, value=s.nama_toko),
                        batik_textfield("Deskripsi / Tagline", ref=self.r_deskripsi,
                                        value=s.deskripsi, multiline=True, min_lines=2),
                        batik_textfield("Simbol Mata Uang", ref=self.r_currency,
                                        value=s.currency, hint="Rp"),
                    ]),

                    ft.Container(height=12),

                    _section_card("📞 Informasi Kontak", [
                        batik_textfield("Alamat Toko", ref=self.r_alamat,
                                        value=s.alamat, multiline=True, min_lines=2),
                        batik_textfield("Nomor HP / WhatsApp", ref=self.r_hp,
                                        value=s.no_hp, keyboard_type="phone"),
                        batik_textfield("Email", ref=self.r_email,
                                        value=s.email, keyboard_type="email"),
                    ]),

                    ft.Container(height=12),

                    _section_card("📱 Media Sosial", [
                        batik_textfield("Instagram (@username)", ref=self.r_ig, value=s.instagram),
                        batik_textfield("Website / Tokopedia / Shopee", ref=self.r_web, value=s.website),
                        batik_textfield("Teks Footer", ref=self.r_footer,
                                        value=s.footer_text, multiline=True, min_lines=2),
                    ]),

                    ft.Container(height=16),

                    primary_button("💾 Simpan Pengaturan Toko", save_toko),
                    ft.Container(height=32),
                ],
                spacing=0,
                padding=ft.padding.symmetric(horizontal=16),
            ),
            expand=True,
        )

    def _save_all_data(self):
        """Save all data to database"""
        if not self.state.local_db:
            return
        
        self.state.local_db.replace_all("produk", self.state.produk)
        self.state.local_db.replace_all("alat", self.state.alat)
        self.state.local_db.replace_all("bahan", self.state.bahan)
        self.state.local_db.replace_all("pewarna", self.state.pewarna)
        self.state.local_db.replace_all("malam", self.state.malam)
        self.state.local_db.replace_all("karyawan", self.state.karyawan)
        self.state.local_db.replace_all("overhead", self.state.overhead)
        self.state.local_db.replace_all("proses", getattr(self.state, 'proses', []))
        self.state.local_db.replace_all("hpp", self.state.hpp_list)
        self.state.local_db.replace_all("diskon", self.state.diskon)
        self.state.local_db.replace_all("admin", self.state.admins)

    def _load_all_data_from_db(self):
        """Load all data from database"""
        if not self.state.local_db:
            return
        
        self.state.produk = self.state.local_db.get_all("produk")
        self.state.alat = self.state.local_db.get_all("alat")
        self.state.bahan = self.state.local_db.get_all("bahan")
        self.state.pewarna = self.state.local_db.get_all("pewarna")
        self.state.malam = self.state.local_db.get_all("malam")
        self.state.karyawan = self.state.local_db.get_all("karyawan")
        self.state.overhead = self.state.local_db.get_all("overhead")
        self.state.proses = self.state.local_db.get_all("proses")
        self.state.hpp_list = self.state.local_db.get_all("hpp")
        self.state.diskon = self.state.local_db.get_all("diskon")
        self.state.admins = self.state.local_db.get_all("admin")

    def _tab_database(self):
        s = self.s
        is_connected = self.db.is_configured()

        status_color = BatikTheme.SUCCESS if is_connected else BatikTheme.TEXT_SECONDARY
        status_icon_name = ft.Icons.CHECK_CIRCLE if is_connected else ft.Icons.RADIO_BUTTON_UNCHECKED
        status_text = "Terhubung ke Google Sheets" if is_connected else "Belum terhubung"

        def save_db(_):
            sid = self.r_sheets_id.current.value.strip()
            key = self.r_api_key.current.value.strip()
            if not sid or not key:
                show_snack(self.page, "⚠️ Spreadsheet ID dan API Key wajib diisi!", BatikTheme.WARNING)
                return
            s.sheets_id = sid
            s.sheets_api_key = key
            self.db.configure(sid, key)
            test = self.db.read_sheet("setting", limit=1)
            if test is not None:
                self.r_status_icon.current.icon = ft.Icons.CHECK_CIRCLE
                self.r_status_icon.current.color = BatikTheme.SUCCESS
                self.r_status_text.current.value = "✅ Terhubung ke Google Sheets"
                self.r_status_container.current.bgcolor = "#E8F5E9"
                show_snack(self.page, "✅ Berhasil terhubung ke Google Sheets!")
            else:
                self.r_status_icon.current.icon = ft.Icons.ERROR
                self.r_status_icon.current.color = BatikTheme.ERROR
                self.r_status_text.current.value = "❌ Gagal terhubung – periksa ID dan API Key"
                self.r_status_container.current.bgcolor = "#FFEBEE"
                show_snack(self.page, "❌ Gagal terhubung!", BatikTheme.ERROR)
            self.page.update()

        def init_sheets(_):
            def do_init():
                result = self.db.init_sheets()
                if result:
                    show_snack(self.page, "✅ Semua sheet berhasil diinisialisasi!")
                else:
                    show_snack(self.page, "❌ Gagal inisialisasi sheet!", BatikTheme.ERROR)
            show_confirm_dialog(
                self.page,
                "Inisialisasi Spreadsheet",
                "Ini akan membuat/reset semua sheet header. Lanjutkan?",
                do_init,
            )

        def sync_demo(_):
            self.db.save_demo_data(self.state)
            show_snack(self.page, "✅ Data demo berhasil disinkronisasi ke Sheets!")

        return ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Container(height=16),

                    ft.Container(
                        ref=self.r_status_container,
                        content=ft.Row([
                            ft.Icon(ref=self.r_status_icon, icon=status_icon_name,
                                    color=status_color, size=20),
                            ft.Text(ref=self.r_status_text, value=status_text,
                                    size=13, weight="w600", color=status_color),
                        ], spacing=8),
                        bgcolor="#E8F5E9" if is_connected else BatikTheme.BG_CARD,
                        padding=ft.padding.all(12),
                        border=ft.border.all(1, BatikTheme.SUCCESS if is_connected else BatikTheme.DIVIDER),
                    ),

                    ft.Container(height=12),

                    _section_card("🔑 Konfigurasi Google Sheets API", [
                        batik_textfield("Spreadsheet ID *", ref=self.r_sheets_id,
                                        value=s.sheets_id,
                                        hint="Salin dari URL: /spreadsheets/d/[ID]/edit"),
                        ft.Text(
                            "💡 Buka Google Sheets → lihat URL → salin bagian ID-nya",
                            size=11, color=BatikTheme.TEXT_SECONDARY, italic=True,
                        ),
                        ft.Container(height=4),
                        batik_textfield("API Key *", ref=self.r_api_key,
                                        value=s.sheets_api_key,
                                        hint="AIza...",
                                        password=True, can_reveal_password=True),
                        ft.Text(
                            "💡 Buat di console.cloud.google.com → APIs → Credentials",
                            size=11, color=BatikTheme.TEXT_SECONDARY, italic=True,
                        ),
                    ]),

                    ft.Container(height=12),
                    primary_button("🔗 Simpan & Uji Koneksi", save_db),
                    ft.Container(height=12),

                    _section_card("📋 Inisialisasi", [
                        ft.Row([
                            outline_button("🗂️ Init Sheet Headers", init_sheets),
                            outline_button("☁️ Sync Demo Data", sync_demo),
                        ], spacing=8, wrap=True),
                    ]),

                    ft.Container(height=32),
                ],
                spacing=0,
                padding=ft.padding.symmetric(horizontal=16),
            ),
            expand=True,
        )

    def _tab_theme(self):
        """Tab untuk mengubah tema dari gambar atau manual dengan color picker sederhana"""
        
        # Color picker text fields
        primary_text = ft.TextField(
            value=BatikTheme.PRIMARY,
            hint_text="#RRGGBB",
            width=150,
            bgcolor=BatikTheme.BG_CARD,
        )
        secondary_text = ft.TextField(
            value=BatikTheme.SECONDARY,
            hint_text="#RRGGBB",
            width=150,
            bgcolor=BatikTheme.BG_CARD,
        )
        accent_text = ft.TextField(
            value=BatikTheme.ACCENT,
            hint_text="#RRGGBB",
            width=150,
            bgcolor=BatikTheme.BG_CARD,
        )
        
        # Store as instance variables for access in other functions
        self.primary_text = primary_text
        self.secondary_text = secondary_text
        self.accent_text = accent_text
        
        # Preview containers
        primary_preview = ft.Container(
            width=40, height=40,
            bgcolor=BatikTheme.PRIMARY,
            border_radius=8,
            border=ft.border.all(1, BatikTheme.DIVIDER),
        )
        secondary_preview = ft.Container(
            width=40, height=40,
            bgcolor=BatikTheme.SECONDARY,
            border_radius=8,
            border=ft.border.all(1, BatikTheme.DIVIDER),
        )
        accent_preview = ft.Container(
            width=40, height=40,
            bgcolor=BatikTheme.ACCENT,
            border_radius=8,
            border=ft.border.all(1, BatikTheme.DIVIDER),
        )
        
        # Store preview references for updates
        self.primary_preview_ref = ft.Ref[ft.Container]()
        self.secondary_preview_ref = ft.Ref[ft.Container]()
        self.accent_preview_ref = ft.Ref[ft.Container]()
        primary_preview.ref = self.primary_preview_ref
        secondary_preview.ref = self.secondary_preview_ref
        accent_preview.ref = self.accent_preview_ref
        
        def update_primary_color(e):
            color = primary_text.value.strip()
            if color.startswith('#') and len(color) == 7:
                if self.primary_preview_ref.current:
                    self.primary_preview_ref.current.bgcolor = color
            self.page.update()
        
        def update_secondary_color(e):
            color = secondary_text.value.strip()
            if color.startswith('#') and len(color) == 7:
                if self.secondary_preview_ref.current:
                    self.secondary_preview_ref.current.bgcolor = color
            self.page.update()
        
        def update_accent_color(e):
            color = accent_text.value.strip()
            if color.startswith('#') and len(color) == 7:
                if self.accent_preview_ref.current:
                    self.accent_preview_ref.current.bgcolor = color
            self.page.update()
        
        def save_theme_manual(_):
            """Apply manual theme colors and save to database"""
            primary = primary_text.value.strip()
            secondary = secondary_text.value.strip()
            accent = accent_text.value.strip()
            
            def is_valid_hex(color):
                if not color or not color.startswith('#') or len(color) != 7:
                    return False
                try:
                    int(color[1:], 16)
                    return True
                except:
                    return False
            
            if not is_valid_hex(primary):
                primary = BatikTheme.PRIMARY
            if not is_valid_hex(secondary):
                secondary = BatikTheme.SECONDARY
            if not is_valid_hex(accent):
                accent = BatikTheme.ACCENT
            
            BatikTheme.PRIMARY = primary
            BatikTheme.SECONDARY = secondary
            BatikTheme.ACCENT = accent
            
            # Save to database
            self._save_theme_colors()
            
            # Update gradient
            BatikTheme.GRADIENT_PRIMARY = ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[BatikTheme.PRIMARY, BatikTheme._darken_color_rgb(BatikTheme._hex_to_rgb(primary), 0.2)]
            )
            
            self.page.theme = BatikTheme.get_theme()
            self.page.bgcolor = BatikTheme.BG_PRIMARY
            self.page.update()
            
            if self.theme_preview_ref.current:
                self.theme_preview_ref.current.bgcolor = BatikTheme.PRIMARY
            
            show_snack(self.page, "✅ Tema berhasil diperbarui secara manual dan tersimpan!", BatikTheme.SUCCESS)
        
        def reset_theme(_):
            """Reset to default theme and save to database"""
            BatikTheme.PRIMARY = "#7B3F00"
            BatikTheme.SECONDARY = "#B87333"
            BatikTheme.ACCENT = "#D4AF37"
            BatikTheme.BG_PRIMARY = "#FDF8F0"
            BatikTheme.BG_CARD = "#FFFFFF"
            BatikTheme.BG_SECONDARY = "#F5EDE3"
            BatikTheme.TEXT_PRIMARY = "#2C1810"
            BatikTheme.TEXT_SECONDARY = "#5C3E2D"
            BatikTheme.TEXT_HINT = "#9B7B5C"
            BatikTheme.DIVIDER = "#E5D5BC"
            
            # Save to database
            self._save_theme_colors()
            
            BatikTheme.GRADIENT_PRIMARY = ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=["#7B3F00", "#5C2D00"]
            )
            
            self.page.theme = BatikTheme.get_theme()
            self.page.bgcolor = BatikTheme.BG_PRIMARY
            self.page.update()
            
            if self.theme_preview_ref.current:
                self.theme_preview_ref.current.bgcolor = BatikTheme.PRIMARY
            
            # Reset text fields
            primary_text.value = BatikTheme.PRIMARY
            secondary_text.value = BatikTheme.SECONDARY
            accent_text.value = BatikTheme.ACCENT
            
            # Reset previews
            if self.primary_preview_ref.current:
                self.primary_preview_ref.current.bgcolor = BatikTheme.PRIMARY
            if self.secondary_preview_ref.current:
                self.secondary_preview_ref.current.bgcolor = BatikTheme.SECONDARY
            if self.accent_preview_ref.current:
                self.accent_preview_ref.current.bgcolor = BatikTheme.ACCENT
            
            self.page.update()
            
            show_snack(self.page, "✅ Tema berhasil direset ke default dan tersimpan!", BatikTheme.SUCCESS)
        
        def apply_theme_from_image(_):
            """Apply theme from image URL - only update PRIMARY, SECONDARY, ACCENT and save"""
            url = self.r_theme_url.current.value.strip()
            if not url:
                show_snack(self.page, "⚠️ Masukkan URL gambar!", BatikTheme.WARNING)
                return
            
            show_snack(self.page, "🔄 Memproses gambar...", BatikTheme.SUCCESS)
            
            # Store current background and text colors that should NOT be changed
            old_bg_primary = BatikTheme.BG_PRIMARY
            old_bg_card = BatikTheme.BG_CARD
            old_bg_secondary = BatikTheme.BG_SECONDARY
            old_text_primary = BatikTheme.TEXT_PRIMARY
            old_text_secondary = BatikTheme.TEXT_SECONDARY
            old_text_hint = BatikTheme.TEXT_HINT
            old_divider = BatikTheme.DIVIDER
            
            # Try to update colors from image
            if BatikTheme.update_from_url(url):
                # Restore background and text colors (only keep PRIMARY, SECONDARY, ACCENT from image)
                BatikTheme.BG_PRIMARY = old_bg_primary
                BatikTheme.BG_CARD = old_bg_card
                BatikTheme.BG_SECONDARY = old_bg_secondary
                BatikTheme.TEXT_PRIMARY = old_text_primary
                BatikTheme.TEXT_SECONDARY = old_text_secondary
                BatikTheme.TEXT_HINT = old_text_hint
                BatikTheme.DIVIDER = old_divider
                
                # Save to database
                self._save_theme_colors()
                
                # Update gradient with new primary color
                BatikTheme.GRADIENT_PRIMARY = ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[BatikTheme.PRIMARY, BatikTheme._darken_color_rgb(BatikTheme._hex_to_rgb(BatikTheme.PRIMARY), 0.2)]
                )
                
                # Update page theme
                self.page.theme = BatikTheme.get_theme()
                self.page.bgcolor = BatikTheme.BG_PRIMARY
                self.page.update()
                
                # Update theme preview
                if self.theme_preview_ref.current:
                    self.theme_preview_ref.current.bgcolor = BatikTheme.PRIMARY
                
                # Update text fields
                primary_text.value = BatikTheme.PRIMARY
                secondary_text.value = BatikTheme.SECONDARY
                accent_text.value = BatikTheme.ACCENT
                
                # Update preview containers
                if self.primary_preview_ref.current:
                    self.primary_preview_ref.current.bgcolor = BatikTheme.PRIMARY
                if self.secondary_preview_ref.current:
                    self.secondary_preview_ref.current.bgcolor = BatikTheme.SECONDARY
                if self.accent_preview_ref.current:
                    self.accent_preview_ref.current.bgcolor = BatikTheme.ACCENT
                
                self.page.update()
                
                show_snack(self.page, "✅ Tema (Primer, Sekunder, Aksen) berhasil diperbarui dari gambar dan tersimpan!\n"
                           "Background dan Text tetap menggunakan warna default.", BatikTheme.SUCCESS)
            else:
                show_snack(self.page, "❌ Gagal memproses gambar! Periksa URL dan coba lagi.", BatikTheme.ERROR)
        
        def preview_theme(_):
            url = self.r_theme_url.current.value.strip()
            if url:
                show_snack(self.page, "🔄 Memuat preview...", BatikTheme.SUCCESS)
        
        # Set on_change handlers
        primary_text.on_change = update_primary_color
        secondary_text.on_change = update_secondary_color
        accent_text.on_change = update_accent_color
        
        return ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Container(height=24),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🎨 Tema Aplikasi", size=18, weight="w700",
                                    color=BatikTheme.PRIMARY),
                            ft.Text("Ubah tema dari gambar batik atau atur warna manual",
                                    size=12, color=BatikTheme.TEXT_SECONDARY),
                        ], spacing=4),
                    ),
                    
                    ft.Container(height=24),
                    
                    # Auto Theme from Image
                    _section_card("🎨 Auto Tema dari Gambar", [
                        ft.Text(
                            "Masukkan URL gambar batik atau motif untuk mengekstrak warna tema.\n"
                            "Aplikasi akan mengambil warna dominan dari gambar dan menerapkannya.",
                            size=12, color=BatikTheme.TEXT_SECONDARY,
                        ),
                        ft.Container(height=12),
                        batik_textfield("URL Gambar Tema", ref=self.r_theme_url,
                                        value=getattr(self.state.setting, 'theme_image_url', ""),
                                        hint="https://...",
                                        on_blur=preview_theme),
                        ft.Container(height=8),
                        primary_button(
                            "🎨 Terapkan Tema dari Gambar",
                            on_click=apply_theme_from_image,
                            expand=True,
                        ),
                        ft.Text(
                            "💡 Tips: Gunakan gambar batik dengan warna yang jelas dan kontras\n"
                            "untuk mendapatkan tema yang optimal",
                            size=10, color=BatikTheme.TEXT_HINT,
                            text_align="center",
                        ),
                    ]),
                    
                    ft.Container(height=12),
                    
                    # Theme preview
                    ft.Container(
                        ref=self.theme_preview_ref,
                        content=ft.Column([
                            ft.Text("Preview Warna Saat Ini", size=14, weight="w600",
                                    color=BatikTheme.TEXT_WHITE),
                            ft.Row([
                                ft.Container(
                                    width=60, height=60,
                                    bgcolor=BatikTheme.PRIMARY,
                                    border_radius=8,
                                    content=ft.Text("Primer", size=10, color="white"),
                                ),
                                ft.Container(
                                    width=60, height=60,
                                    bgcolor=BatikTheme.SECONDARY,
                                    border_radius=8,
                                    content=ft.Text("Sekunder", size=10, color="white"),
                                ),
                                ft.Container(
                                    width=60, height=60,
                                    bgcolor=BatikTheme.ACCENT,
                                    border_radius=8,
                                    content=ft.Text("Aksen", size=10, color="white"),
                                ),
                            ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
                        ], spacing=12, horizontal_alignment="center"),
                        bgcolor=BatikTheme.PRIMARY,
                        padding=ft.padding.all(24),
                        border_radius=16,
                        margin=ft.margin.symmetric(horizontal=16),
                    ),
                    
                    ft.Container(height=24),
                    
                    # Manual Theme Settings
                    _section_card("🎨 Atur Warna Manual", [
                        ft.Text(
                            "Atur warna tema secara manual dengan memasukkan kode hex warna.\n"
                            "Format: #RRGGBB (contoh: #7B3F00 untuk coklat)",
                            size=12, color=BatikTheme.TEXT_SECONDARY,
                        ),
                        ft.Container(height=12),
                        
                        # Primary Color
                        ft.Text("Warna Primer:", size=12, weight="w600"),
                        ft.Row([
                            primary_preview,
                            primary_text,
                        ], spacing=10, vertical_alignment="center"),
                        
                        ft.Container(height=8),
                        
                        # Secondary Color
                        ft.Text("Warna Sekunder:", size=12, weight="w600"),
                        ft.Row([
                            secondary_preview,
                            secondary_text,
                        ], spacing=10, vertical_alignment="center"),
                        
                        ft.Container(height=8),
                        
                        # Accent Color
                        ft.Text("Warna Aksen:", size=12, weight="w600"),
                        ft.Row([
                            accent_preview,
                            accent_text,
                        ], spacing=10, vertical_alignment="center"),
                        
                        ft.Container(height=12),
                        
                        ft.Row([
                            outline_button("Reset Default", on_click=reset_theme, expand=True),
                            ft.Container(width=8),
                            primary_button("Terapkan Warna", on_click=save_theme_manual, expand=True),
                        ]),
                        ft.Text(
                            "💡 Tips: Gunakan situs seperti colorhunt.co untuk inspirasi warna\n"
                            "Atau gunakan fitur Auto Tema dari gambar batik",
                            size=10, color=BatikTheme.TEXT_HINT,
                            text_align="center",
                        ),
                    ]),
                    
                    ft.Container(height=24),
                    
                    _section_card("🎨 Warna Saat Ini", [
                        _color_row("Warna Primer", BatikTheme.PRIMARY),
                        _color_row("Warna Sekunder", BatikTheme.SECONDARY),
                        _color_row("Warna Aksen", BatikTheme.ACCENT),
                        ft.Divider(color=BatikTheme.DIVIDER),
                        _color_row("Background", BatikTheme.BG_PRIMARY),
                        _color_row("Card Background", BatikTheme.BG_CARD),
                        _color_row("Text Primary", BatikTheme.TEXT_PRIMARY),
                    ]),
                    
                    ft.Container(height=32),
                ],
                spacing=0,
                padding=ft.padding.symmetric(horizontal=16),
            ),
            expand=True,
        )

    def _tab_backup_load(self):
        """Tab untuk Backup & Load Database (tanpa FilePicker)"""
        backup_name_ref = ft.Ref[ft.TextField]()
        backup_path_ref = ft.Ref[ft.Text]()
        load_path_ref = ft.Ref[ft.TextField]()
        
        def backup_database(_):
            backup_name = backup_name_ref.current.value.strip()
            if not backup_name:
                show_snack(self.page, "⚠️ Masukkan nama folder backup!", BatikTheme.WARNING)
                return
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = os.path.join(os.path.expanduser("~"), "Documents", "BatikPro_Backups", f"{backup_name}_{timestamp}")
            os.makedirs(backup_folder, exist_ok=True)
            
            if os.path.exists(self.db_path):
                dest = os.path.join(backup_folder, "batikpro.db")
                shutil.copy2(self.db_path, dest)
                show_snack(self.page, f"✅ Database berhasil di backup ke:\n{backup_folder}", BatikTheme.SUCCESS)
                backup_path_ref.current.value = backup_folder
                self.page.update()
            else:
                show_snack(self.page, "❌ File database tidak ditemukan!", BatikTheme.ERROR)
        
        def load_database(_):
            file_path = load_path_ref.current.value
            if not file_path or not os.path.exists(file_path):
                show_snack(self.page, "⚠️ Masukkan path file database yang valid!", BatikTheme.WARNING)
                return
            
            def do_load():
                try:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_folder = os.path.join(os.path.expanduser("~"), "Documents", "BatikPro_Backups", f"auto_backup_before_load_{timestamp}")
                    os.makedirs(backup_folder, exist_ok=True)
                    shutil.copy2(self.db_path, os.path.join(backup_folder, "batikpro.db"))
                    
                    shutil.copy2(file_path, self.db_path)
                    self._load_all_data_from_db()
                    # Also reload theme colors
                    self._load_theme_colors()
                    
                    show_snack(self.page, "✅ Database berhasil dimuat! Aplikasi akan refresh.", BatikTheme.SUCCESS)
                    self.page.update()
                except Exception as e:
                    show_snack(self.page, f"❌ Gagal memuat database: {e}", BatikTheme.ERROR)
            
            show_confirm_dialog(
                self.page,
                "Konfirmasi Load Database",
                "Load database akan menggantikan data saat ini. Data saat ini akan di-backup otomatis. Lanjutkan?",
                do_load,
            )
        
        def export_data(_):
            export_path = os.path.join(os.path.expanduser("~"), "Documents", "BatikPro_Export")
            os.makedirs(export_path, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = os.path.join(export_path, f"batikpro_export_{timestamp}.json")
            
            data = {
                "produk": self.state.produk,
                "alat": self.state.alat,
                "bahan": self.state.bahan,
                "pewarna": self.state.pewarna,
                "malam": self.state.malam,
                "karyawan": self.state.karyawan,
                "overhead": self.state.overhead,
                "proses": getattr(self.state, 'proses', []),
                "hpp_list": self.state.hpp_list,
                "diskon": self.state.diskon,
                "admin": self.state.admins,
                "theme": {
                    "primary": BatikTheme.PRIMARY,
                    "secondary": BatikTheme.SECONDARY,
                    "accent": BatikTheme.ACCENT,
                },
                "setting": {
                    "nama_toko": self.s.nama_toko,
                    "deskripsi": self.s.deskripsi,
                    "logo_url": self.s.logo_url,
                    "alamat": self.s.alamat,
                    "no_hp": self.s.no_hp,
                    "email": self.s.email,
                    "instagram": self.s.instagram,
                    "website": self.s.website,
                    "footer_text": self.s.footer_text,
                    "currency": self.s.currency,
                }
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            show_snack(self.page, f"✅ Data berhasil diekspor ke:\n{export_file}", BatikTheme.SUCCESS)
        
        def delete_database(_):
            """Hapus database lokal"""
            def do_delete():
                try:
                    # Backup dulu sebelum hapus
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_folder = os.path.join(os.path.expanduser("~"), "Documents", "BatikPro_Backups", f"backup_before_delete_{timestamp}")
                    os.makedirs(backup_folder, exist_ok=True)
                    
                    if os.path.exists(self.db_path):
                        shutil.copy2(self.db_path, os.path.join(backup_folder, "batikpro.db"))
                        os.remove(self.db_path)
                        show_snack(self.page, f"✅ Database berhasil dihapus!\nBackup tersimpan di:\n{backup_folder}", BatikTheme.SUCCESS)
                        
                        # Kosongkan state
                        self.state.produk = []
                        self.state.alat = []
                        self.state.bahan = []
                        self.state.pewarna = []
                        self.state.malam = []
                        self.state.karyawan = []
                        self.state.overhead = []
                        self.state.proses = []
                        self.state.hpp_list = []
                        self.state.diskon = []
                        self.state.admins = []
                        
                        # Refresh tampilan
                        self._load_all_data_from_db()
                        self.page.update()
                    else:
                        show_snack(self.page, "❌ File database tidak ditemukan!", BatikTheme.ERROR)
                except Exception as e:
                    show_snack(self.page, f"❌ Gagal menghapus database: {e}", BatikTheme.ERROR)
            
            show_confirm_dialog(
                self.page,
                "Konfirmasi Hapus Database",
                "Anda yakin ingin menghapus database lokal?\n\n"
                "⚠️ PERINGATAN:\n"
                "• Semua data akan hilang!\n"
                "• Database akan di-backup otomatis sebelum dihapus.\n"
                "• Aplikasi akan membuat database baru saat restart.\n\n"
                "Lanjutkan?",
                do_delete,
            )
        
        return ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Container(height=24),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("💾 Backup & Load Database", size=18, weight="w700",
                                    color=BatikTheme.PRIMARY),
                            ft.Text("Cadangkan dan pulihkan data Anda", size=12, color=BatikTheme.TEXT_SECONDARY),
                        ], spacing=4),
                    ),
                    
                    ft.Container(height=24),
                    
                    _section_card("📦 Backup Database", [
                        ft.Text(
                            "Buat backup database ke folder dokumen Anda.",
                            size=12, color=BatikTheme.TEXT_SECONDARY,
                        ),
                        ft.Container(height=8),
                        batik_textfield("Nama Backup", ref=backup_name_ref, 
                                        hint="Contoh: backup_januari_2024"),
                        ft.Container(height=8),
                        primary_button("💾 Backup Sekarang", on_click=backup_database, expand=True),
                        ft.Text(
                            f"📍 Lokasi backup: Documents/BatikPro_Backups/",
                            size=10, color=BatikTheme.TEXT_HINT,
                        ),
                        ft.Text(ref=backup_path_ref, size=10, color=BatikTheme.SUCCESS, selectable=True),
                    ]),
                    
                    ft.Container(height=12),
                    
                    _section_card("📂 Load Database", [
                        ft.Text(
                            "Pulihkan database dari file backup.",
                            size=12, color=BatikTheme.TEXT_SECONDARY,
                        ),
                        ft.Container(height=8),
                        batik_textfield("Path File Database", ref=load_path_ref, 
                                        hint=f"Contoh: {self.db_path}",
                                        on_change=lambda e: None),
                        ft.Container(height=8),
                        primary_button("📂 Load Database", on_click=load_database, expand=True, bgcolor=BatikTheme.ACCENT),
                        ft.Text(
                            "💡 Tips: Masukkan path lengkap file database yang ingin dimuat.",
                            size=10, color=BatikTheme.TEXT_HINT,
                        ),
                        ft.Text(
                            "⚠️ Peringatan: Load akan menimpa data saat ini! Data saat ini akan di-backup otomatis.",
                            size=10, color=BatikTheme.WARNING,
                        ),
                    ]),
                    
                    ft.Container(height=12),
                    
                    _section_card("📤 Ekspor Data (JSON)", [
                        ft.Text(
                            "Ekspor semua data ke format JSON.",
                            size=12, color=BatikTheme.TEXT_SECONDARY,
                        ),
                        ft.Container(height=8),
                        outline_button("📄 Ekspor ke JSON", on_click=export_data, expand=True),
                        ft.Text(
                            f"📍 Lokasi export: Documents/BatikPro_Export/",
                            size=10, color=BatikTheme.TEXT_HINT,
                        ),
                    ]),
                    
                    ft.Container(height=12),
                    
                    _section_card("🗑️ Hapus Database", [
                        ft.Text(
                            "Hapus database lokal. Data akan di-backup otomatis sebelum dihapus.",
                            size=12, color=BatikTheme.TEXT_SECONDARY,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            "⚠️ PERINGATAN: Tindakan ini akan menghapus SEMUA data!\n"
                            "Database akan di-backup otomatis ke folder Documents/BatikPro_Backups/",
                            size=11, color=BatikTheme.WARNING,
                        ),
                        ft.Container(height=8),
                        outline_button(
                            "🗑️ Hapus Database", 
                            on_click=delete_database, 
                            expand=True,
                        ),
                    ]),
                    
                    ft.Container(height=12),
                    
                    _section_card("ℹ️ Info Database", [
                        ft.Row([
                            ft.Text("Lokasi Database:", size=12, color=BatikTheme.TEXT_SECONDARY),
                            ft.Text(self.db_path, size=11, color=BatikTheme.TEXT_HINT, selectable=True),
                        ]),
                        ft.Row([
                            ft.Text("Jumlah Produk:", size=12, color=BatikTheme.TEXT_SECONDARY),
                            ft.Text(str(len(self.state.produk)), size=12, weight="w600"),
                        ]),
                        ft.Row([
                            ft.Text("Jumlah Master:", size=12, color=BatikTheme.TEXT_SECONDARY),
                            ft.Text(f"Alat:{len(self.state.alat)} Bahan:{len(self.state.bahan)}", size=11),
                        ]),
                    ]),
                    
                    ft.Container(height=32),
                ],
                spacing=0,
                padding=ft.padding.symmetric(horizontal=16),
            ),
            expand=True,
        )

    def _tab_history(self):
        """Tab untuk Login History"""
        
        history = []
        if self.state.local_db:
            history = self.state.local_db.get_all("login_history") or []
        
        if self.state.current_user:
            current_username = self.state.current_user.get("username", "")
            current_nama = self.state.current_user.get("nama", current_username)
            current_time = datetime.datetime.now().isoformat()
            
            today = datetime.datetime.now().date()
            already_today = False
            for h in history:
                try:
                    h_date = datetime.datetime.fromisoformat(h.get("timestamp", "")).date()
                    if h_date == today and h.get("username") == current_username:
                        already_today = True
                        break
                except:
                    pass
            
            if not already_today:
                history.append({
                    "username": current_username,
                    "nama": current_nama,
                    "timestamp": current_time,
                    "status": "success"
                })
                if self.state.local_db:
                    self.state.local_db.upsert("login_history", {
                        "username": current_username,
                        "nama": current_nama,
                        "timestamp": current_time,
                        "status": "success"
                    })
        
        history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        history_items = []
        for item in history[:50]:
            timestamp = item.get("timestamp", "")
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%d/%m/%Y %H:%M:%S")
            except:
                pass
            
            status = item.get("status", "success")
            status_color = BatikTheme.SUCCESS if status == "success" else BatikTheme.ERROR
            status_text = "✅ Berhasil" if status == "success" else "❌ Gagal"
            
            history_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(item.get("nama", item.get("username", "-")), 
                                   size=BatikTheme.FONT_SM, weight="w600"),
                            ft.Text(item.get("username", "-"), size=BatikTheme.FONT_XS, color=BatikTheme.TEXT_HINT),
                        ], spacing=2, expand=True),
                        ft.Text(status_text, size=BatikTheme.FONT_SM, color=status_color),
                        ft.Text(timestamp, size=BatikTheme.FONT_XS, color=BatikTheme.TEXT_HINT),
                    ], spacing=8, vertical_alignment="center"),
                    padding=ft.padding.all(10),
                    border=ft.border.all(1, BatikTheme.DIVIDER),
                    border_radius=BatikTheme.RADIUS_SM,
                )
            )
        
        if not history_items:
            history_items.append(
                ft.Container(
                    content=ft.Text("Belum ada riwayat login", size=BatikTheme.FONT_SM, color=BatikTheme.TEXT_HINT),
                    padding=ft.padding.all(20),
                )
            )
        
        return ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Container(height=16),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📜 Riwayat Login", size=18, weight="w700",
                                    color=BatikTheme.PRIMARY),
                            ft.Text("Catatan aktivitas login pengguna", size=12, color=BatikTheme.TEXT_SECONDARY),
                        ], spacing=4),
                    ),
                    
                    ft.Container(height=16),
                    
                    ft.Container(
                        content=ft.Column(history_items, spacing=8),
                        padding=ft.padding.symmetric(horizontal=16),
                    ),
                    
                    ft.Container(height=32),
                ],
                spacing=0,
                padding=ft.padding.symmetric(horizontal=16),
            ),
            expand=True,
        )

    def _tab_tentang(self):
        s = self.s
        current_user = getattr(self.state, 'current_user', None)
        user_name = current_user.get("nama", "Admin") if current_user else "Admin"
        
        # Hapus logo - hanya teks
        return ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Container(height=24),

                    ft.Container(
                        content=ft.Column([
                            ft.Text("BatikPro ERP", size=28, weight="w700",
                                    color=BatikTheme.PRIMARY),
                            ft.Text("Aplikasi Manajemen & Kalkulasi HPP Batik",
                                    size=14, color=BatikTheme.TEXT_SECONDARY,
                                    text_align="center"),
                            ft.Container(height=8),
                            ft.Text(f"Selamat datang, {user_name}", size=14, color=BatikTheme.SUCCESS),
                            ft.Text("v2.0.0", size=13, color=BatikTheme.TEXT_SECONDARY),
                        ], horizontal_alignment="center", spacing=6),
                    ),

                    ft.Container(height=24),

                    _section_card("✨ Fitur Utama", [
                        _feature_row("🏪", "Galeri Toko", "Tampilan produk seperti toko online"),
                        _feature_row("🧮", "Wizard HPP", "Kalkulasi harga pokok lengkap"),
                        _feature_row("📊", "Laporan PDF", "Cetak tabel produk & HPP"),
                        _feature_row("🏷️", "8 Tipe Diskon", "Flash sale, bundling, member, dll"),
                        _feature_row("☁️", "Google Sheets", "Database online real-time"),
                        _feature_row("🎨", "Tema Dinamis", "Ubah tema dari gambar batik"),
                        _feature_row("💾", "Backup & Load", "Cadangkan dan pulihkan data"),
                        _feature_row("📜", "Login History", "Catatan aktivitas login"),
                        _feature_row("🗑️", "Hapus Database", "Reset aplikasi dengan menghapus database"),
                        _feature_row("📱", "Multi Platform", "Android, Tablet, SmartTV"),
                    ]),

                    ft.Container(height=12),

                    _section_card("💰 Istilah Keuangan & Rumus", [
                        _finance_row("HPP (Harga Pokok Produksi)", 
                                    "Biaya total yang dikeluarkan untuk memproduksi satu unit produk.",
                                    "HPP = (Total Bahan + Total Tenaga Kerja + Total Overhead) / Kuantitas"),
                        _finance_row("Margin Keuntungan", 
                                    "Persentase keuntungan dari harga jual setelah dikurangi HPP.",
                                    "Margin (%) = (Harga Jual - HPP) / HPP × 100%"),
                        _finance_row("ROI (Return on Investment)", 
                                    "Persentase pengembalian investasi dari penjualan produk.",
                                    "ROI (%) = (Keuntungan / Total Biaya) × 100%"),
                        _finance_row("Diskon", 
                                    "Potongan harga yang diberikan kepada pelanggan.",
                                    "Harga Setelah Diskon = Harga Jual × (1 - Diskon% / 100)"),
                        _finance_row("BEP (Break Even Point)", 
                                    "Titik impas di mana pendapatan sama dengan biaya total.",
                                    "BEP (unit) = Total Biaya Tetap / (Harga Jual - Biaya Variabel)"),
                        _finance_row("Biaya Variabel", 
                                    "Biaya yang berubah sesuai jumlah produksi (bahan, tenaga kerja langsung).", ""),
                        _finance_row("Biaya Tetap", 
                                    "Biaya yang tidak berubah meskipun produksi berubah (sewa, gaji tetap).", ""),
                    ]),

                    ft.Container(height=12),

                    _section_card("📊 Komponen HPP", [
                        ft.Row(
                            controls=[
                                _chip("🧵 Bahan Baku", BatikTheme.PRIMARY),
                                _chip("🎨 Pewarna", "#8E44AD"),
                                _chip("🕯️ Malam", "#E67E22"),
                                _chip("🔧 Sewa Alat", BatikTheme.SECONDARY),
                                _chip("👷 Upah Karyawan", BatikTheme.SUCCESS),
                                _chip("💡 Overhead", "#E74C3C"),
                                _chip("📦 Biaya Tambahan", "#3498DB"),
                                _chip("🎨 Biaya Desain", "#9B59B6"),
                            ],
                            spacing=8,
                            wrap=True,
                        ),
                    ]),

                    ft.Container(height=12),

                    _section_card("🛠️ Teknologi", [
                        _tech_row("Flet", "Flutter-based Python UI framework"),
                        _tech_row("Google Sheets API v4", "Database online"),
                        _tech_row("ReportLab", "Generate laporan PDF"),
                        _tech_row("Pillow", "Ekstraksi warna dari gambar"),
                        _tech_row("SQLite", "Database lokal"),
                        _tech_row("Python 3.11+", "Backend logic"),
                    ]),

                    ft.Container(height=12),

                    ft.Container(
                        content=ft.Column([
                            ft.Text("Dikembangkan dengan ❤️ untuk",
                                    size=12, color=BatikTheme.TEXT_SECONDARY,
                                    text_align="center"),
                            ft.Text("pengrajin batik Indonesia",
                                    size=14, weight="w600",
                                    color=BatikTheme.PRIMARY,
                                    text_align="center"),
                            ft.Text("🇮🇩 Bangga Produk Batik Nusantara 🇮🇩",
                                    size=13, color=BatikTheme.ACCENT,
                                    text_align="center"),
                        ], horizontal_alignment="center", spacing=4),
                    ),

                    ft.Container(height=32),
                ],
                spacing=0,
                padding=ft.padding.symmetric(horizontal=16),
            ),
            expand=True,
        )

def _section_card(title: str, children: list):
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=14, weight="w700", color=BatikTheme.PRIMARY),
            ft.Divider(color=BatikTheme.DIVIDER, height=1),
            *children,
        ], spacing=10),
        bgcolor=BatikTheme.BG_CARD,
        padding=ft.padding.all(16),
        border=ft.border.all(1, BatikTheme.DIVIDER),
    )

def _color_row(label: str, color: str):
    return ft.Row([
        ft.Text(label, size=12, color=BatikTheme.TEXT_SECONDARY, expand=True),
        ft.Container(
            width=30, height=30,
            bgcolor=color,
            border_radius=6,
            border=ft.border.all(1, BatikTheme.DIVIDER),
        ),
        ft.Text(color, size=11, font_family="monospace", color=BatikTheme.TEXT_HINT),
    ], spacing=8, vertical_alignment="center")

def _feature_row(icon: str, title: str, desc: str):
    return ft.Row([
        ft.Text(icon, size=20),
        ft.Column([
            ft.Text(title, size=13, weight="w600", color=BatikTheme.TEXT_PRIMARY),
            ft.Text(desc, size=11, color=BatikTheme.TEXT_SECONDARY),
        ], spacing=1, expand=True),
    ], spacing=12, vertical_alignment="center")

def _finance_row(title: str, desc: str, formula: str):
    return ft.Column([
        ft.Text(title, size=13, weight="w600", color=BatikTheme.PRIMARY),
        ft.Text(desc, size=11, color=BatikTheme.TEXT_SECONDARY),
        ft.Text(formula, size=10, color=BatikTheme.ACCENT, font_family="monospace") if formula else ft.Container(),
        ft.Divider(height=1, color=BatikTheme.DIVIDER),
    ], spacing=4)

def _tech_row(tech: str, desc: str):
    return ft.Row([
        ft.Container(
            content=ft.Text(tech, size=11, weight="w600", color=BatikTheme.SECONDARY),
            bgcolor="#EAF4FB",
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
        ),
        ft.Text(desc, size=12, color=BatikTheme.TEXT_SECONDARY, expand=True),
    ], spacing=10)

def _chip(label: str, color: str):
    return ft.Container(
        content=ft.Text(label, size=12, weight="w500", color="white"),
        bgcolor=color,
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        border_radius=16,
    )