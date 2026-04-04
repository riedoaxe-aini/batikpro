"""
CrudMasterPage – CRUD semua Data Master
Tab: Produk | Alat | Bahan | Pewarna | Malam | Karyawan | Overhead | Proses | Admin
"""

import flet as ft
import datetime
from core.theme import BatikTheme as T
from components.widgets import (
    batik_appbar, batik_textfield, batik_dropdown, primary_button,
    outline_button, show_snack, show_confirm_dialog, BatikBottomNav, cost_row
)

TABS = ["Produk", "Alat", "Bahan", "Pewarna", "Malam", "Karyawan", "Overhead", "Proses", "Admin"]
JENIS_PRODUK = ["Kain Batik", "Kemeja Batik", "Selendang", "Sandal", "Aksesoris", "Lainnya"]
JENIS_BATIK = ["", "Tulis", "Cap", "Sablon"]
STATUS_OPTIONS = ["Aktif", "Nonaktif", "Habis", "Preorder"]
YES_NO_OPTIONS = ["", "Ya", "Tidak"]

# Dynamic categories with ability to add new
KATEGORI_ALAT = ["Alat Tulis", "Alat Elektronik", "Alat Pemanas", "Alat Cap", "Furnitur", "Lainnya"]
KATEGORI_BAHAN = ["Kain", "Benang", "Aksesoris", "Lainnya"]
KATEGORI_PROSES = ["Pencucian", "Pemakuan", "Pemotongan", "Penjahitan", "Pengeleman", "Finishing", "Lainnya"]
KATEGORI_OVERHEAD = ["Utilitas", "Bahan Bakar", "Sewa", "Transportasi", "Lainnya"]
SPESIALISASI_KARYAWAN = ["Pembatik Tulis", "Pembatik Cap", "Pewarnaan", "Nglorod", "Finishing", "Desain", "Lainnya"]

# Satuan options with detailed units
SATUAN_BERAT = ["gram", "kg", "ons", "pon"]
SATUAN_PANJANG = ["meter", "cm", "yard", "kaki"]
SATUAN_VOLUME = ["liter", "ml", "cc"]
SATUAN_WAKTU = ["menit", "jam", "hari", "minggu"]
SATUAN_ENERGI = ["kWh", "watt", "joule"]
SATUAN_LAIN = ["pcs", "lembar", "gulung", "buah", "set", "paket"]

SATUAN_OPTIONS = SATUAN_BERAT + SATUAN_PANJANG + SATUAN_VOLUME + SATUAN_WAKTU + SATUAN_ENERGI + SATUAN_LAIN
ROLE_OPTIONS = ["Admin", "Staff", "Kasir"]
ADMIN_STATUS = ["Aktif", "Nonaktif"]

class CrudMasterPage:
    def __init__(self, page, state, db, router, tab="Produk", edit_id=None, **kwargs):
        self.page = page
        self.state = state
        self.db = db
        self.router = router
        self._active_tab = tab if tab in TABS else "Produk"
        self._edit_id = edit_id
        self._list_ref = ft.Ref[ft.Column]()
        self._form_visible = edit_id is not None
        self._form_data: dict = {}
        self._editing_id: str = None
        
        # Image references for 10 images
        self._image_refs = [ft.Ref[ft.TextField]() for _ in range(10)]
        
        # References for HPP components
        self._bahan_list_ref = ft.Ref[ft.Column]()
        self._pewarna_list_ref = ft.Ref[ft.Column]()
        self._malam_list_ref = ft.Ref[ft.Column]()
        self._alat_list_ref = ft.Ref[ft.Column]()
        self._karyawan_list_ref = ft.Ref[ft.Column]()
        self._overhead_list_ref = ft.Ref[ft.Column]()
        
        # HPP wizard data for produk
        self._hpp_data = {
            "bahan_list": [],
            "pewarna_list": [],
            "malam_list": [],
            "alat_list": [],
            "karyawan_list": [],
            "overhead_list": [],
            "biaya_desain": 0.0,
            "biaya_pengemasan": 0.0,
            "biaya_pengiriman": 0.0,
            "biaya_pajak": 0.0,
            "biaya_lainnya": 0.0,
            "margin_persen": 30.0,
            "diskon_persen": 0.0,
            "kuantitas": 1,
        }
        
        # Dynamic categories storage
        self._custom_categories = {
            "alat": [],
            "bahan": [],
            "proses": [],
            "overhead": [],
            "karyawan": []
        }

    def build(self):
        def on_nav(index):
            pages = ["gallery", "home", "hpp_wizard", "crud_master", "setting"]
            self.router.navigate(pages[index])

        # Create custom tab bar
        tab_buttons = []
        for i, label in enumerate(TABS):
            is_selected = (label == self._active_tab)
            
            def make_tap_handler(idx, lbl):
                def handler(_):
                    self._active_tab = lbl
                    self._form_visible = False
                    self._form_data = {}
                    self._editing_id = None
                    self._refresh_list()
                    for j, btn in enumerate(tab_buttons):
                        if j == idx:
                            btn.bgcolor = T.PRIMARY
                            btn.content.controls[0].color = T.TEXT_WHITE
                        else:
                            btn.bgcolor = T.BG_CARD
                            btn.content.controls[0].color = T.TEXT_SECONDARY
                    self.page.update()
                return handler
            
            tab_btn = ft.Container(
                content=ft.Column([
                    ft.Text(label, size=T.FONT_SM, weight="w600", 
                           color=T.TEXT_WHITE if is_selected else T.TEXT_SECONDARY),
                    ft.Container(
                        height=2,
                        bgcolor=T.ACCENT if is_selected else ft.Colors.TRANSPARENT,
                        width=40,
                    ),
                ], spacing=4, horizontal_alignment="center"),
                bgcolor=T.PRIMARY if is_selected else T.BG_CARD,
                padding=ft.padding.symmetric(12, 16),
                border_radius=ft.BorderRadius(8, 8, 0, 0),
                on_click=make_tap_handler(i, label),
                expand=True,
            )
            tab_buttons.append(tab_btn)
        
        tab_bar = ft.Container(
            content=ft.Row(tab_buttons, spacing=2),
            bgcolor=T.BG_CARD,
            border=ft.border.only(bottom=ft.BorderSide(1, T.DIVIDER)),
        )

        list_col = ft.Column(ref=self._list_ref, spacing=T.SPACE_SM, scroll="auto")
        self._refresh_list_widget(list_col)

        self._form_container = ft.Container(visible=self._form_visible)
        self._build_form_widget()

        content = ft.ListView(
            [
                batik_appbar("Data Master", on_back=lambda _: self.router.navigate("home"),
                              subtitle="CRUD semua data"),
                ft.Container(content=tab_bar, bgcolor=T.BG_CARD),
                ft.Container(
                    content=ft.Row([
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Row([ft.Icon(ft.Icons.ADD_ROUNDED, size=14, color="white"), ft.Text("+ Tambah Baru", color="white", weight="w600", size=12)], spacing=4, tight=True),
                            bgcolor=T.PRIMARY,
                            padding=ft.padding.symmetric(8, 14),
                            on_click=self._show_add_form, ink=True,
                        ),
                    ]),
                    padding=ft.padding.symmetric(T.SPACE_SM, T.SPACE_LG),
                ),
                self._form_container,
                ft.Container(content=list_col, padding=ft.padding.symmetric(0, T.SPACE_LG)),
                ft.Container(height=80),
            ],
            spacing=0, expand=True,
        )

        bottom_nav = BatikBottomNav(current_index=3, on_change=on_nav)

        return ft.Container(
            content=ft.Stack([
                ft.Column([content], expand=True),
                ft.Container(content=bottom_nav.build(), bottom=0, left=0, right=0),
            ]),
            bgcolor=T.BG_PRIMARY, expand=True,
        )

    def _get_data(self) -> list:
        mapping = {
            "Produk": self.state.produk,
            "Alat": self.state.alat,
            "Bahan": self.state.bahan,
            "Pewarna": self.state.pewarna,
            "Malam": self.state.malam,
            "Karyawan": self.state.karyawan,
            "Overhead": self.state.overhead,
            "Proses": getattr(self.state, 'proses', []),
            "Admin": getattr(self.state, 'admins', []),
        }
        return mapping.get(self._active_tab, [])

    def _get_prefix(self) -> str:
        prefixes = {
            "Produk": "PRD", "Alat": "ALT", "Bahan": "BHN",
            "Pewarna": "PWN", "Malam": "MLM", "Karyawan": "KRY", 
            "Overhead": "OVH", "Proses": "PRS", "Admin": "ADM"
        }
        return prefixes.get(self._active_tab, "ITM")

    def _refresh_list_widget(self, col: ft.Column):
        col.controls.clear()
        data = self._get_data()
        if not data:
            col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX_ROUNDED, size=50, color=T.TEXT_HINT),
                        ft.Text("Belum ada data", size=T.FONT_SM, color=T.TEXT_HINT),
                    ], horizontal_alignment="center", spacing=8),
                    expand=True,
                    padding=40,
                )
            )
            return
        for item in data:
            col.controls.append(self._item_card(item))

    def _refresh_list(self):
        if self._list_ref.current:
            self._refresh_list_widget(self._list_ref.current)
        self.page.update()

    def _item_card(self, item: dict) -> ft.Container:
        nama = item.get("Nama", item.get("username", item.get("Nama_Produk", "-")))
        iid = item.get("ID", "-")

        subtitle = ""
        if self._active_tab == "Produk":
            try: 
                hpp = float(item.get("HPP_Per_Unit", 0))
                harga = float(item.get("Harga_Jual", 0))
                subtitle = f"HPP: {self.state.format_currency(hpp)} | Jual: {self.state.format_currency(harga)}"
                stok = item.get("Stok", 0)
                subtitle += f" | Stok: {stok}"
            except: 
                subtitle = "-"
        elif self._active_tab == "Alat":
            subtitle = f"Sewa: Rp {item.get('Biaya_Sewa_Per_Menit',0)}/menit"
        elif self._active_tab == "Bahan":
            subtitle = f"Rp {item.get('Harga_Per_Satuan',0)}/{item.get('Satuan','-')}"
        elif self._active_tab == "Pewarna":
            subtitle = f"Rp {item.get('Harga_Per_Satuan',0)}/{item.get('Satuan','-')}"
        elif self._active_tab == "Malam":
            subtitle = f"Rp {item.get('Harga_Per_Satuan',0)}/{item.get('Satuan','-')}"
        elif self._active_tab == "Karyawan":
            subtitle = f"Rp {item.get('Upah_Per_Jam',0)}/jam"
        elif self._active_tab == "Overhead":
            subtitle = f"Rp {item.get('Biaya_Per_Satuan',0)}/{item.get('Satuan','-')}"
        elif self._active_tab == "Proses":
            durasi = item.get("Durasi_Menit", 0)
            biaya = item.get("Biaya_Per_Proses", 0)
            subtitle = f"{durasi} menit | Rp {biaya}/proses"
        elif self._active_tab == "Admin":
            role = item.get("role", "Staff")
            status = item.get("status", "Aktif")
            subtitle = f"{role} | {status}"

        def on_edit(_):
            self._editing_id = iid
            self._form_data = dict(item)
            if self._active_tab == "Produk":
                self._hpp_data = {
                    "bahan_list": item.get("bahan_list", []),
                    "pewarna_list": item.get("pewarna_list", []),
                    "malam_list": item.get("malam_list", []),
                    "alat_list": item.get("alat_list", []),
                    "karyawan_list": item.get("karyawan_list", []),
                    "overhead_list": item.get("overhead_list", []),
                    "biaya_desain": item.get("biaya_desain", 0),
                    "biaya_pengemasan": item.get("biaya_pengemasan", 0),
                    "biaya_pengiriman": item.get("biaya_pengiriman", 0),
                    "biaya_pajak": item.get("biaya_pajak", 0),
                    "biaya_lainnya": item.get("biaya_lainnya", 0),
                    "margin_persen": item.get("margin_persen", 30),
                    "diskon_persen": item.get("diskon_persen", 0),
                    "kuantitas": item.get("kuantitas", 1),
                }
            self._show_edit_form()

        def on_delete(_):
            show_confirm_dialog(
                self.page, "Hapus Data", f"Hapus {nama}?",
                on_confirm=lambda: self._delete_item(iid)
            )

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(iid[-3:], size=T.FONT_XS, color=T.TEXT_WHITE, weight="w700"),
                    bgcolor=T.PRIMARY, border_radius=T.RADIUS_SM, padding=ft.padding.symmetric(4, 8),
                    width=40,
                ),
                ft.Column([
                    ft.Text(nama, size=T.FONT_SM, weight="w600", color=T.TEXT_PRIMARY),
                    ft.Text(subtitle, size=T.FONT_XS, color=T.TEXT_HINT),
                ], spacing=2, tight=True, expand=True),
                ft.IconButton(icon=ft.Icons.EDIT_ROUNDED, icon_color=T.SECONDARY, icon_size=18, on_click=on_edit),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE_ROUNDED, icon_color=T.ERROR, icon_size=18, on_click=on_delete),
            ], spacing=10, vertical_alignment="center"),
            bgcolor=T.BG_CARD, border_radius=T.RADIUS_MD, padding=T.SPACE_MD,
            shadow=T.SHADOW_SM, border=ft.border.all(1, T.DIVIDER),
        )

    def _show_add_form(self, _=None):
        self._editing_id = None
        self._form_data = {}
        if self._active_tab == "Admin":
            self._form_data["created_at"] = datetime.datetime.now().isoformat()
        self._hpp_data = {
            "bahan_list": [],
            "pewarna_list": [],
            "malam_list": [],
            "alat_list": [],
            "karyawan_list": [],
            "overhead_list": [],
            "biaya_desain": 0.0,
            "biaya_pengemasan": 0.0,
            "biaya_pengiriman": 0.0,
            "biaya_pajak": 0.0,
            "biaya_lainnya": 0.0,
            "margin_persen": 30.0,
            "diskon_persen": 0.0,
            "kuantitas": 1,
        }
        self._form_visible = True
        self._build_form_widget()
        self._form_container.visible = True
        self.page.update()

    def _show_edit_form(self):
        self._form_visible = True
        self._build_form_widget()
        self._form_container.visible = True
        self.page.update()

    def _calculate_hpp(self):
        """Calculate HPP and selling price from components"""
        h = self._hpp_data
        
        total_bahan = sum(i.get("subtotal", 0) for i in h["bahan_list"])
        total_pewarna = sum(i.get("subtotal", 0) for i in h["pewarna_list"])
        total_malam = sum(i.get("subtotal", 0) for i in h["malam_list"])
        total_alat = sum(i.get("subtotal", 0) for i in h["alat_list"])
        total_upah = sum(i.get("subtotal", 0) for i in h["karyawan_list"])
        total_overhead = sum(i.get("subtotal", 0) for i in h["overhead_list"])
        
        total_tambahan = (
            h.get("biaya_desain", 0) +
            h.get("biaya_pengemasan", 0) +
            h.get("biaya_pengiriman", 0) +
            h.get("biaya_pajak", 0) +
            h.get("biaya_lainnya", 0)
        )
        
        total_produksi = total_bahan + total_pewarna + total_malam + total_alat + total_upah + total_overhead + total_tambahan
        kuantitas = max(h.get("kuantitas", 1), 1)
        hpp_per_unit = total_produksi / kuantitas
        
        margin = h.get("margin_persen", 30) / 100
        harga_jual = hpp_per_unit * (1 + margin)
        
        diskon = h.get("diskon_persen", 0) / 100
        harga_final = harga_jual * (1 - diskon)
        
        return {
            "total_produksi": total_produksi,
            "hpp_per_unit": hpp_per_unit,
            "harga_jual": harga_jual,
            "harga_final": harga_final,
            "margin_persen": h.get("margin_persen", 30),
            "diskon_persen": h.get("diskon_persen", 0),
        }

    def _build_form_widget(self):
        d = self._form_data
        tab = self._active_tab
        is_edit = self._editing_id is not None
        title = f"{'Edit' if is_edit else 'Tambah'} {tab}"

        def save(_):
            self._save_item()

        def cancel(_):
            self._form_container.visible = False
            self._form_data = {}
            self._editing_id = None
            self.page.update()

        fields = self._build_fields(d)

        form_content = ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Row([
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            icon_color=T.ERROR,
                            icon_size=24,
                            on_click=cancel,
                            tooltip="Batal",
                        ),
                    ]),
                    ft.Container(
                        content=ft.Row([
                            ft.Text(title, size=T.FONT_MD, weight="w700", color=T.TEXT_PRIMARY, expand=True),
                        ]),
                        padding=ft.padding.only(bottom=T.SPACE_SM),
                    ),
                    *fields,
                    ft.Container(height=T.SPACE_SM),
                    ft.Row([
                        outline_button("Batal", on_click=cancel),
                        ft.Container(width=T.SPACE_SM),
                        primary_button("Simpan", icon=ft.Icons.SAVE_ROUNDED, on_click=save, expand=True),
                    ]),
                ],
                spacing=T.SPACE_MD,
                padding=ft.padding.all(T.SPACE_LG),
            ),
            bgcolor=T.BG_CARD,
            border=ft.border.all(1.5, T.ACCENT),
            margin=ft.margin.symmetric(0, T.SPACE_LG),
            shadow=T.SHADOW_MD,
            expand=True,
        )

        self._form_container.content = form_content

    def _build_fields(self, d: dict) -> list:
        tab = self._active_tab
        
        if tab == "Produk":
            return self._build_produk_fields(d)
        elif tab == "Proses":
            return self._build_proses_fields(d)
        elif tab == "Admin":
            return self._build_admin_fields(d)
        else:
            return self._build_other_fields(d)

    def _build_produk_fields(self, d: dict) -> list:
        """Build fields for Produk with HPP components"""
        fields = []
        
        def tf(key, label, ktype="text", multiline=False, hint=""):
            return ft.TextField(
                label=label, value=str(d.get(key, "")),
                keyboard_type=ktype, multiline=multiline,
                min_lines=1, max_lines=4 if multiline else 1,
                hint_text=hint,
                label_style=ft.TextStyle(size=T.FONT_SM, color=T.TEXT_SECONDARY),
                on_change=lambda e, k=key: d.update({k: e.control.value}),
                bgcolor=T.BG_CARD,
            )
        
        def dd(key, label, opts):
            ctrl = ft.Dropdown(
                label=label, 
                value=d.get(key, ""),
                options=[ft.dropdown.Option(o) for o in opts],
                label_style=ft.TextStyle(size=T.FONT_SM, color=T.TEXT_SECONDARY),
            )
            ctrl.on_select = lambda e, k=key: d.update({k: e.control.value})
            return ctrl
        
        existing_urls = d.get("Gambar_URLs", [])
        if isinstance(existing_urls, str):
            existing_urls = [u.strip() for u in existing_urls.split(",") if u.strip()]
        
        image_fields = []
        for i in range(10):
            img_url = existing_urls[i] if i < len(existing_urls) else ""
            img_field = ft.TextField(
                ref=self._image_refs[i],
                label=f"Gambar {i+1} (URL)",
                value=img_url,
                hint_text="https://...",
                keyboard_type="url",
                label_style=ft.TextStyle(size=T.FONT_SM, color=T.TEXT_SECONDARY),
                on_change=lambda e, idx=i: self._on_image_change(idx, e.control.value),
                bgcolor=T.BG_CARD,
            )
            image_fields.append(img_field)
        
        fields.extend([
            tf("Nama", "Nama Produk *"),
            dd("Jenis_Produk", "Jenis Produk", JENIS_PRODUK),
            tf("Motif", "Motif", hint="Motif batik"),
            tf("Asal_Daerah", "Asal Daerah", hint="Kota/daerah asal produksi"),
            tf("Deskripsi", "Deskripsi", multiline=True, hint="Deskripsi lengkap produk"),
            tf("Dimensi", "Dimensi", hint="Contoh: 250x110cm"),
            tf("Berat_Gram", "Berat (gram)", "number", hint="Berat produk dalam gram"),
            dd("Halal", "Halal", YES_NO_OPTIONS),
            dd("Eco_Friendly", "Eco Friendly", YES_NO_OPTIONS),
            dd("Preorder", "Preorder", YES_NO_OPTIONS),
            dd("Special", "Special", YES_NO_OPTIONS),
            dd("Premium", "Premium", YES_NO_OPTIONS),
            dd("Jenis_Batik", "Jenis Batik", JENIS_BATIK),
            tf("Tingkat_Kesulitan", "Tingkat Kesulitan (1-10)", "number"),
            tf("Warna_Dominan", "Warna Dominan", hint="Contoh: Merah, Biru, Emas"),
        ])
        
        fields.extend([
            ft.Text("📸 Gambar Produk (Max 10)", size=T.FONT_MD, weight="w700", color=T.PRIMARY),
            ft.Divider(color=T.DIVIDER),
            ft.Text("Masukkan URL gambar produk (dari Google Drive, Imgur, dll)", 
                   size=T.FONT_XS, color=T.TEXT_HINT),
            ft.Container(height=4),
            *image_fields,
            ft.Text("💡 Tips: Kosongkan jika tidak ada gambar", size=T.FONT_XS, color=T.TEXT_HINT, italic=True),
            ft.Container(height=8),
        ])
        
        fields.extend([
            ft.Text("💰 Komponen Biaya Produksi", size=T.FONT_MD, weight="w700", color=T.PRIMARY),
            ft.Divider(color=T.DIVIDER),
            self._build_biaya_desain_section(),
            self._build_bahan_section(),
            self._build_pewarna_section(),
            self._build_malam_section(),
            self._build_alat_section(),
            self._build_karyawan_section(),
            self._build_overhead_section(),
            self._build_tambahan_section(),
            self._build_margin_diskon_section(),
            self._build_hpp_preview(),
        ])
        
        fields.extend([
            ft.Divider(color=T.DIVIDER),
            dd("Status", "Status", STATUS_OPTIONS),
            tf("Stok", "Stok", "number", hint="Jumlah stok tersedia"),
        ])
        
        return fields

    def _build_biaya_desain_section(self):
        def update_biaya_desain(e):
            try:
                self._hpp_data["biaya_desain"] = float(e.control.value)
            except:
                self._hpp_data["biaya_desain"] = 0
            self._update_hpp_preview()
        
        return ft.Column([
            ft.Text("🎨 Biaya Desain:", size=T.FONT_MD, weight="w600"),
            ft.TextField(label="Biaya Desain (Rp)", value=str(self._hpp_data.get("biaya_desain", 0)),
                        keyboard_type="number", on_change=update_biaya_desain,
                        prefix="Rp", bgcolor=T.BG_CARD,
                        hint_text="Biaya untuk desain motif batik"),
        ], spacing=T.SPACE_SM)

    def _build_bahan_section(self):
        bahan_list = []
        for b in self.state.bahan:
            bahan_list.append(ft.Row([
                ft.Text(b.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(self.state.format_currency(float(b.get("Harga_Per_Satuan", 0))), size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=b: self._add_to_list("bahan_list", item, {"satuan": item.get("Satuan", "pcs"), "harga": float(item.get("Harga_Per_Satuan", 0))})),
            ], spacing=8, vertical_alignment="center"))
        
        return ft.Column([
            ft.Text("🧵 Bahan Baku:", size=T.FONT_MD, weight="w600"),
            ft.TextField(label="Cari Bahan", hint_text="Ketik nama bahan...", bgcolor=T.BG_CARD),
            ft.Column(bahan_list, spacing=T.SPACE_SM, height=150, scroll="auto"),
            ft.Divider(),
            ft.Text("Bahan Terpilih:", size=T.FONT_SM, weight="w600"),
            ft.Column(ref=self._bahan_list_ref, spacing=T.SPACE_SM),
        ], spacing=T.SPACE_SM)

    def _build_pewarna_section(self):
        pewarna_list = []
        for p in self.state.pewarna:
            pewarna_list.append(ft.Row([
                ft.Text(p.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(self.state.format_currency(float(p.get("Harga_Per_Satuan", 0))), size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=p: self._add_to_list("pewarna_list", item, {"harga": float(item.get("Harga_Per_Satuan", 0))})),
            ], spacing=8))
        
        return ft.Column([
            ft.Text("🎨 Pewarna:", size=T.FONT_MD, weight="w600"),
            ft.Column(pewarna_list, spacing=T.SPACE_SM, height=120, scroll="auto"),
            ft.Divider(),
            ft.Text("Pewarna Terpilih:", size=T.FONT_SM, weight="w600"),
            ft.Column(ref=self._pewarna_list_ref, spacing=T.SPACE_SM),
        ], spacing=T.SPACE_SM)

    def _build_malam_section(self):
        malam_list = []
        for m in self.state.malam:
            malam_list.append(ft.Row([
                ft.Text(m.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(self.state.format_currency(float(m.get("Harga_Per_Satuan", 0))), size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=m: self._add_to_list("malam_list", item, {"harga": float(item.get("Harga_Per_Satuan", 0))})),
            ], spacing=8))
        
        return ft.Column([
            ft.Text("🕯️ Malam:", size=T.FONT_MD, weight="w600"),
            ft.Column(malam_list, spacing=T.SPACE_SM, height=120, scroll="auto"),
            ft.Divider(),
            ft.Text("Malam Terpilih:", size=T.FONT_SM, weight="w600"),
            ft.Column(ref=self._malam_list_ref, spacing=T.SPACE_SM),
        ], spacing=T.SPACE_SM)

    def _build_alat_section(self):
        alat_list = []
        for a in self.state.alat:
            alat_list.append(ft.Row([
                ft.Text(a.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(f"Rp {a.get('Biaya_Sewa_Per_Menit', 0)}/menit", size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=a: self._add_to_list("alat_list", item, {"biaya_sewa": float(item.get("Biaya_Sewa_Per_Menit", 0))})),
            ], spacing=8))
        
        return ft.Column([
            ft.Text("🔧 Alat:", size=T.FONT_MD, weight="w600"),
            ft.Column(alat_list, spacing=T.SPACE_SM, height=150, scroll="auto"),
            ft.Divider(),
            ft.Text("Alat Terpilih:", size=T.FONT_SM, weight="w600"),
            ft.Column(ref=self._alat_list_ref, spacing=T.SPACE_SM),
        ], spacing=T.SPACE_SM)

    def _build_karyawan_section(self):
        karyawan_list = []
        for k in self.state.karyawan:
            karyawan_list.append(ft.Row([
                ft.Text(k.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(f"Rp {k.get('Upah_Per_Jam', 0)}/jam", size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=k: self._add_to_list("karyawan_list", item, {"upah": float(item.get("Upah_Per_Jam", 0))})),
            ], spacing=8))
        
        return ft.Column([
            ft.Text("👥 Karyawan:", size=T.FONT_MD, weight="w600"),
            ft.Column(karyawan_list, spacing=T.SPACE_SM, height=150, scroll="auto"),
            ft.Divider(),
            ft.Text("Karyawan Terpilih:", size=T.FONT_SM, weight="w600"),
            ft.Column(ref=self._karyawan_list_ref, spacing=T.SPACE_SM),
        ], spacing=T.SPACE_SM)

    def _build_overhead_section(self):
        overhead_list = []
        for o in self.state.overhead:
            overhead_list.append(ft.Row([
                ft.Text(o.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(f"Rp {o.get('Biaya_Per_Satuan', 0)}/{o.get('Satuan', 'unit')}", size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=o: self._add_to_list("overhead_list", item, {"biaya": float(item.get("Biaya_Per_Satuan", 0))})),
            ], spacing=8))
        
        return ft.Column([
            ft.Text("💡 Overhead:", size=T.FONT_MD, weight="w600"),
            ft.Column(overhead_list, spacing=T.SPACE_SM, height=120, scroll="auto"),
            ft.Divider(),
            ft.Text("Overhead Terpilih:", size=T.FONT_SM, weight="w600"),
            ft.Column(ref=self._overhead_list_ref, spacing=T.SPACE_SM),
        ], spacing=T.SPACE_SM)

    def _build_tambahan_section(self):
        def update_biaya(key, e):
            try:
                self._hpp_data[key] = float(e.control.value)
            except:
                self._hpp_data[key] = 0
            self._update_hpp_preview()
        
        return ft.Column([
            ft.Text("📦 Biaya Tambahan:", size=T.FONT_MD, weight="w600"),
            ft.TextField(label="Biaya Pengemasan", value=str(self._hpp_data.get("biaya_pengemasan", 0)),
                        keyboard_type="number", on_change=lambda e: update_biaya("biaya_pengemasan", e),
                        prefix="Rp", bgcolor=T.BG_CARD),
            ft.TextField(label="Biaya Pengiriman", value=str(self._hpp_data.get("biaya_pengiriman", 0)),
                        keyboard_type="number", on_change=lambda e: update_biaya("biaya_pengiriman", e),
                        prefix="Rp", bgcolor=T.BG_CARD),
            ft.TextField(label="Pajak", value=str(self._hpp_data.get("biaya_pajak", 0)),
                        keyboard_type="number", on_change=lambda e: update_biaya("biaya_pajak", e),
                        prefix="Rp", bgcolor=T.BG_CARD),
            ft.TextField(label="Biaya Lainnya", value=str(self._hpp_data.get("biaya_lainnya", 0)),
                        keyboard_type="number", on_change=lambda e: update_biaya("biaya_lainnya", e),
                        prefix="Rp", bgcolor=T.BG_CARD),
            ft.TextField(label="Kuantitas Produksi", value=str(self._hpp_data.get("kuantitas", 1)),
                        keyboard_type="number", on_change=lambda e: self._update_kuantitas(e), bgcolor=T.BG_CARD),
        ], spacing=T.SPACE_SM)

    def _build_margin_diskon_section(self):
        def update_margin(e):
            try:
                self._hpp_data["margin_persen"] = float(e.control.value)
            except:
                self._hpp_data["margin_persen"] = 30
            self._update_hpp_preview()
        
        def update_diskon(e):
            try:
                self._hpp_data["diskon_persen"] = float(e.control.value)
            except:
                self._hpp_data["diskon_persen"] = 0
            self._update_hpp_preview()
        
        return ft.Column([
            ft.Text("📈 Margin & Diskon:", size=T.FONT_MD, weight="w600"),
            ft.TextField(label="Margin Keuntungan (%)", value=str(self._hpp_data.get("margin_persen", 30)),
                        keyboard_type="number", on_change=update_margin, bgcolor=T.BG_CARD),
            ft.TextField(label="Diskon (%)", value=str(self._hpp_data.get("diskon_persen", 0)),
                        keyboard_type="number", on_change=update_diskon, bgcolor=T.BG_CARD),
        ], spacing=T.SPACE_SM)

    def _build_hpp_preview(self):
        self._hpp_preview_ref = ft.Ref[ft.Column]()
        return ft.Column([
            ft.Text("📊 Preview Kalkulasi HPP:", size=T.FONT_MD, weight="w700", color=T.PRIMARY),
            ft.Container(ref=self._hpp_preview_ref, content=ft.Column([]), padding=T.SPACE_SM),
        ], spacing=T.SPACE_SM)

    def _update_hpp_preview(self):
        if not hasattr(self, '_hpp_preview_ref') or not self._hpp_preview_ref.current:
            return
        
        calc = self._calculate_hpp()
        self._hpp_preview_ref.current.content = ft.Column([
            cost_row("Total Biaya Produksi", self.state.format_currency(calc["total_produksi"])),
            cost_row("HPP per Unit", self.state.format_currency(calc["hpp_per_unit"]), T.PRIMARY, True),
            cost_row("Margin", f"{calc['margin_persen']:.0f}%"),
            cost_row("Harga Jual", self.state.format_currency(calc["harga_jual"])),
            cost_row("Diskon", f"{calc['diskon_persen']:.0f}%"),
            cost_row("Harga Final", self.state.format_currency(calc["harga_final"]), T.SUCCESS, True),
        ], spacing=T.SPACE_XS)
        self.page.update()

    def _update_kuantitas(self, e):
        try:
            self._hpp_data["kuantitas"] = int(e.control.value)
        except:
            self._hpp_data["kuantitas"] = 1
        self._update_hpp_preview()

    def _add_to_list(self, list_key, item, extra_data):
        """Add item to selected list with support for decimal quantities"""
        new_item = {
            "id": item.get("ID"),
            "nama": item.get("Nama"),
            "jumlah": 1.0,  # Use float for decimal support
            **extra_data,
            "subtotal": 0.0
        }
        
        # Calculate initial subtotal with float support
        if "harga" in new_item:
            new_item["subtotal"] = new_item["jumlah"] * new_item["harga"]
        elif "biaya" in new_item:
            new_item["subtotal"] = new_item["jumlah"] * new_item["biaya"]
        elif "biaya_sewa" in new_item:
            new_item["subtotal"] = new_item["jumlah"] * new_item["biaya_sewa"]
        elif "upah" in new_item:
            new_item["subtotal"] = new_item["jumlah"] * new_item["upah"]
        
        self._hpp_data[list_key].append(new_item)
        self._update_list_display(list_key)
        self._update_hpp_preview()

    def _update_list_display(self, list_key):
        """Update display of selected items with decimal support"""
        ref_map = {
            "bahan_list": self._bahan_list_ref,
            "pewarna_list": self._pewarna_list_ref,
            "malam_list": self._malam_list_ref,
            "alat_list": self._alat_list_ref,
            "karyawan_list": self._karyawan_list_ref,
            "overhead_list": self._overhead_list_ref,
        }
        
        ref = ref_map.get(list_key)
        if not ref or not ref.current:
            return
        
        def update_subtotal(idx, e):
            try:
                val = float(e.control.value)  # Allow decimal
                item = self._hpp_data[list_key][idx]
                item["jumlah"] = val
                if "harga" in item:
                    item["subtotal"] = val * item["harga"]
                elif "biaya" in item:
                    item["subtotal"] = val * item["biaya"]
                elif "biaya_sewa" in item:
                    item["subtotal"] = val * item["biaya_sewa"]
                elif "upah" in item:
                    item["subtotal"] = val * item["upah"]
                self._update_list_display(list_key)
                self._update_hpp_preview()
            except:
                pass
        
        def delete_item(idx):
            self._hpp_data[list_key].pop(idx)
            self._update_list_display(list_key)
            self._update_hpp_preview()
        
        items = []
        for idx, item in enumerate(self._hpp_data[list_key]):
            unit_text = ""
            if list_key == "bahan_list":
                unit_text = item.get("satuan", "pcs")
            elif list_key in ["pewarna_list", "malam_list"]:
                unit_text = "gram" if list_key == "pewarna_list" else "kg"
            elif list_key == "alat_list":
                unit_text = "menit"
            elif list_key == "karyawan_list":
                unit_text = "jam"
            else:
                unit_text = "unit"
            
            items.append(ft.Row([
                ft.Text(item["nama"], size=T.FONT_SM, expand=True),
                ft.TextField(value=str(item["jumlah"]), width=80, keyboard_type="number",
                            on_change=lambda e, i=idx: update_subtotal(i, e), text_align="center"),
                ft.Text(unit_text, size=T.FONT_XS),
                ft.Text(self.state.format_currency(item["subtotal"]), size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, icon_color=T.ERROR,
                            on_click=lambda _, i=idx: delete_item(i)),
            ], spacing=8, vertical_alignment="center"))
        
        ref.current.controls = items
        self.page.update()

    def _on_image_change(self, index: int, value: str):
        urls = self._form_data.get("Gambar_URLs", [])
        if isinstance(urls, str):
            urls = [u.strip() for u in urls.split(",") if u.strip()]
        while len(urls) <= index:
            urls.append("")
        urls[index] = value
        urls = [u for u in urls if u.strip()]
        self._form_data["Gambar_URLs"] = urls

    def _build_proses_fields(self, d: dict) -> list:
        """Build fields for Proses tab with custom category and duration unit selection"""
        fields = []
        
        def tf(key, label, ktype="text", multiline=False):
            return ft.TextField(
                label=label, value=str(d.get(key, "")),
                keyboard_type=ktype, multiline=multiline,
                min_lines=1, max_lines=4 if multiline else 1,
                label_style=ft.TextStyle(size=T.FONT_SM, color=T.TEXT_SECONDARY),
                on_change=lambda e, k=key: d.update({k: e.control.value}),
                bgcolor=T.BG_CARD,
            )
        
        def dd(key, label, opts, on_custom_add=None):
            ctrl = ft.Dropdown(
                label=label, 
                value=d.get(key, opts[0] if opts else ""),
                options=[ft.dropdown.Option(o) for o in opts],
                label_style=ft.TextStyle(size=T.FONT_SM, color=T.TEXT_SECONDARY),
            )
            ctrl.on_select = lambda e, k=key: d.update({k: e.control.value})
            return ctrl
        
        # Custom category handling
        proses_lain_ref = ft.Ref[ft.TextField]()
        durasi_satuan_ref = ft.Ref[ft.Dropdown]()
        kategori_opts = list(KATEGORI_PROSES) + self._custom_categories["proses"]
        
        def update_biaya_per_satuan(e):
            satuan = durasi_satuan_ref.current.value if durasi_satuan_ref.current else "Menit"
            durasi = d.get("Durasi", 0)
            biaya = d.get("Biaya_Per_Satuan", 0)
            try:
                durasi = float(durasi)
                biaya = float(biaya)
            except:
                durasi = 0
                biaya = 0
            if satuan == "Jam":
                d["Durasi_Menit"] = durasi * 60
                d["Biaya_Per_Menit"] = biaya / 60
            else:
                d["Durasi_Menit"] = durasi
                d["Biaya_Per_Menit"] = biaya
        
        def on_kategori_change(e):
            kategori = e.control.value
            if proses_lain_ref.current:
                proses_lain_ref.current.visible = (kategori == "Lainnya")
            self.page.update()
        
        def add_custom_kategori(e):
            new_kategori = proses_lain_ref.current.value.strip()
            if new_kategori and new_kategori not in KATEGORI_PROSES and new_kategori not in self._custom_categories["proses"]:
                self._custom_categories["proses"].append(new_kategori)
                # Update dropdown options
                kategori_dd.options.append(ft.dropdown.Option(new_kategori))
                d["Kategori"] = new_kategori
                d["Nama"] = new_kategori
                proses_lain_ref.current.visible = False
                self.page.update()
        
        kategori_dd = dd("Kategori", "Kategori", kategori_opts)
        kategori_dd.on_select = on_kategori_change
        
        proses_lain_field = ft.Column([
            ft.TextField(
                ref=proses_lain_ref,
                label="Nama Proses Lainnya",
                hint_text="Masukkan nama proses baru",
                visible=d.get("Kategori") == "Lainnya",
                on_change=lambda e: None,
                bgcolor=T.BG_CARD,
            ),
            ft.Container(
                content=ft.Text("+ Tambah sebagai kategori baru", size=T.FONT_XS, color=T.PRIMARY),
                on_click=add_custom_kategori,
                visible=d.get("Kategori") == "Lainnya",
                padding=ft.padding.symmetric(4, 8),
                ink=True,
            ),
        ], spacing=4)
        
        durasi_satuan_dd = dd("Durasi_Satuan", "Satuan Waktu", ["Menit", "Jam"])
        durasi_satuan_dd.on_select = lambda e: update_biaya_per_satuan(e)
        
        fields = [
            tf("Nama", "Nama Proses *"),
            kategori_dd,
            proses_lain_field,
            tf("Deskripsi", "Deskripsi", multiline=True),
            ft.Row([
                ft.TextField(
                    label="Durasi", value=str(d.get("Durasi", 0)), 
                    keyboard_type="number", width=120,
                    on_change=lambda e: update_biaya_per_satuan(e),
                    bgcolor=T.BG_CARD,
                ),
                durasi_satuan_dd,
            ]),
            ft.TextField(
                label="Biaya per Satuan (Rp)", value=str(d.get("Biaya_Per_Satuan", 0)),
                keyboard_type="number", on_change=lambda e: update_biaya_per_satuan(e),
                prefix="Rp", bgcolor=T.BG_CARD,
            ),
            dd("Status", "Status", ["Aktif", "Nonaktif"]),
        ]
        
        return fields

    def _build_admin_fields(self, d: dict) -> list:
        """Build fields for Admin tab"""
        fields = []
        
        def tf(key, label, ktype="text", multiline=False, read_only=False, password=False, can_reveal_password=False):
            return ft.TextField(
                label=label, value=str(d.get(key, "")),
                keyboard_type=ktype, multiline=multiline,
                min_lines=1, max_lines=4 if multiline else 1,
                read_only=read_only,
                password=password,
                can_reveal_password=can_reveal_password,
                label_style=ft.TextStyle(size=T.FONT_SM, color=T.TEXT_SECONDARY),
                on_change=lambda e, k=key: d.update({k: e.control.value}),
                bgcolor=T.BG_CARD,
            )
        
        def dd(key, label, opts):
            ctrl = ft.Dropdown(
                label=label, 
                value=d.get(key, opts[0] if opts else ""),
                options=[ft.dropdown.Option(o) for o in opts],
                label_style=ft.TextStyle(size=T.FONT_SM, color=T.TEXT_SECONDARY),
            )
            ctrl.on_select = lambda e, k=key: d.update({k: e.control.value})
            return ctrl
        
        fields = [
            tf("username", "Username *"),
            tf("password", "Password *", password=True, can_reveal_password=True),
            tf("nama", "Nama Lengkap *"),
            tf("email", "Email", "email"),
            tf("no_hp", "No HP", "phone"),
            dd("role", "Role", ROLE_OPTIONS),
            dd("status", "Status", ADMIN_STATUS),
            tf("created_at", "Tanggal Dibuat", read_only=True),
        ]
        
        return fields

    def _build_other_fields(self, d: dict) -> list:
        """Build fields for non-produk, non-proses, non-admin tabs with custom categories and satuan"""
        fields = []
        
        def tf(key, label, ktype="text", multiline=False):
            return ft.TextField(
                label=label, value=str(d.get(key, "")),
                keyboard_type=ktype, multiline=multiline,
                min_lines=1, max_lines=4 if multiline else 1,
                label_style=ft.TextStyle(size=T.FONT_SM, color=T.TEXT_SECONDARY),
                on_change=lambda e, k=key: d.update({k: e.control.value}),
                bgcolor=T.BG_CARD,
            )
        
        def dd(key, label, opts, on_custom_add=None):
            ctrl = ft.Dropdown(
                label=label, 
                value=d.get(key, opts[0] if opts else ""),
                options=[ft.dropdown.Option(o) for o in opts],
                label_style=ft.TextStyle(size=T.FONT_SM, color=T.TEXT_SECONDARY),
            )
            ctrl.on_select = lambda e, k=key: d.update({k: e.control.value})
            return ctrl
        
        tab = self._active_tab
        
        # Custom category handling for each tab
        if tab == "Alat":
            kategori_opts = list(KATEGORI_ALAT) + self._custom_categories["alat"]
            kategori_lain_ref = ft.Ref[ft.TextField]()
            
            def on_alat_kategori_change(e):
                if e.control.value == "Lainnya":
                    kategori_lain_ref.current.visible = True
                else:
                    kategori_lain_ref.current.visible = False
                self.page.update()
            
            def add_alat_kategori(e):
                new_kategori = kategori_lain_ref.current.value.strip()
                if new_kategori and new_kategori not in KATEGORI_ALAT and new_kategori not in self._custom_categories["alat"]:
                    self._custom_categories["alat"].append(new_kategori)
                    kategori_dd.options.append(ft.dropdown.Option(new_kategori))
                    d["Kategori"] = new_kategori
                    kategori_lain_ref.current.visible = False
                    kategori_lain_ref.current.value = ""
                    self.page.update()
            
            kategori_dd = dd("Kategori", "Kategori", kategori_opts)
            kategori_dd.on_select = on_alat_kategori_change
            
            fields = [
                tf("Nama", "Nama Alat *"),
                kategori_dd,
                ft.TextField(
                    ref=kategori_lain_ref,
                    label="Kategori Lainnya",
                    hint_text="Masukkan kategori baru",
                    visible=False,
                    bgcolor=T.BG_CARD,
                ),
                ft.Container(
                    content=ft.Text("+ Tambah sebagai kategori baru", size=T.FONT_XS, color=T.PRIMARY),
                    on_click=add_alat_kategori,
                    visible=False,
                    padding=ft.padding.symmetric(4, 8),
                    ink=True,
                ),
                tf("Deskripsi", "Deskripsi", multiline=True),
                tf("Biaya_Sewa_Per_Menit", "Biaya Sewa/menit (Rp)", "number"),
                tf("Biaya_Sewa_Per_Hari", "Biaya Sewa/hari (Rp)", "number"),
                dd("Status", "Status", ["Aktif", "Nonaktif", "Rusak"]),
            ]
        elif tab == "Bahan":
            jenis_opts = list(KATEGORI_BAHAN) + self._custom_categories["bahan"]
            jenis_lain_ref = ft.Ref[ft.TextField]()
            
            def on_bahan_jenis_change(e):
                if e.control.value == "Lainnya":
                    jenis_lain_ref.current.visible = True
                else:
                    jenis_lain_ref.current.visible = False
                self.page.update()
            
            def add_bahan_jenis(e):
                new_jenis = jenis_lain_ref.current.value.strip()
                if new_jenis and new_jenis not in KATEGORI_BAHAN and new_jenis not in self._custom_categories["bahan"]:
                    self._custom_categories["bahan"].append(new_jenis)
                    jenis_dd.options.append(ft.dropdown.Option(new_jenis))
                    d["Jenis"] = new_jenis
                    jenis_lain_ref.current.visible = False
                    jenis_lain_ref.current.value = ""
                    self.page.update()
            
            jenis_dd = dd("Jenis", "Jenis", jenis_opts)
            jenis_dd.on_select = on_bahan_jenis_change
            
            fields = [
                tf("Nama", "Nama Bahan *"),
                jenis_dd,
                ft.TextField(
                    ref=jenis_lain_ref,
                    label="Jenis Lainnya",
                    hint_text="Masukkan jenis baru",
                    visible=False,
                    bgcolor=T.BG_CARD,
                ),
                ft.Container(
                    content=ft.Text("+ Tambah sebagai jenis baru", size=T.FONT_XS, color=T.PRIMARY),
                    on_click=add_bahan_jenis,
                    visible=False,
                    padding=ft.padding.symmetric(4, 8),
                    ink=True,
                ),
                dd("Satuan", "Satuan", SATUAN_OPTIONS),
                tf("Harga_Per_Satuan", "Harga/Satuan (Rp)", "number"),
                tf("Supplier", "Supplier"),
            ]
        elif tab == "Pewarna":
            fields = [
                tf("Nama", "Nama Pewarna *"),
                dd("Jenis", "Jenis", ["Sintetis", "Alami"]),
                tf("Kode_Warna", "Kode Warna"),
                dd("Satuan", "Satuan", SATUAN_OPTIONS),
                tf("Harga_Per_Satuan", "Harga/Satuan (Rp)", "number"),
                dd("Halal", "Halal", YES_NO_OPTIONS),
                dd("Eco_Friendly", "Eco Friendly", YES_NO_OPTIONS),
            ]
        elif tab == "Malam":
            fields = [
                tf("Nama", "Nama Malam *"),
                dd("Jenis", "Jenis", ["Parafin", "Alami", "Campuran"]),
                dd("Satuan", "Satuan", SATUAN_OPTIONS),
                tf("Harga_Per_Satuan", "Harga/Satuan (Rp)", "number"),
                dd("Halal", "Halal", YES_NO_OPTIONS),
            ]
        elif tab == "Karyawan":
            spesialisasi_opts = list(SPESIALISASI_KARYAWAN) + self._custom_categories["karyawan"]
            spesialisasi_lain_ref = ft.Ref[ft.TextField]()
            
            def on_karyawan_spesialisasi_change(e):
                if e.control.value == "Lainnya":
                    spesialisasi_lain_ref.current.visible = True
                else:
                    spesialisasi_lain_ref.current.visible = False
                self.page.update()
            
            def add_karyawan_spesialisasi(e):
                new_spesialisasi = spesialisasi_lain_ref.current.value.strip()
                if new_spesialisasi and new_spesialisasi not in SPESIALISASI_KARYAWAN and new_spesialisasi not in self._custom_categories["karyawan"]:
                    self._custom_categories["karyawan"].append(new_spesialisasi)
                    spesialisasi_dd.options.append(ft.dropdown.Option(new_spesialisasi))
                    d["Spesialisasi"] = new_spesialisasi
                    spesialisasi_lain_ref.current.visible = False
                    spesialisasi_lain_ref.current.value = ""
                    self.page.update()
            
            spesialisasi_dd = dd("Spesialisasi", "Spesialisasi", spesialisasi_opts)
            spesialisasi_dd.on_select = on_karyawan_spesialisasi_change
            
            fields = [
                tf("Nama", "Nama Karyawan *"),
                spesialisasi_dd,
                ft.TextField(
                    ref=spesialisasi_lain_ref,
                    label="Spesialisasi Lainnya",
                    hint_text="Masukkan spesialisasi baru",
                    visible=False,
                    bgcolor=T.BG_CARD,
                ),
                ft.Container(
                    content=ft.Text("+ Tambah sebagai spesialisasi baru", size=T.FONT_XS, color=T.PRIMARY),
                    on_click=add_karyawan_spesialisasi,
                    visible=False,
                    padding=ft.padding.symmetric(4, 8),
                    ink=True,
                ),
                tf("Upah_Per_Jam", "Upah/Jam (Rp)", "number"),
                tf("Upah_Per_Hari", "Upah/Hari (Rp)", "number"),
                dd("Status", "Status", ["Aktif", "Cuti", "Tidak Aktif"]),
                tf("No_HP", "No HP"),
            ]
        elif tab == "Overhead":
            kategori_opts = list(KATEGORI_OVERHEAD) + self._custom_categories["overhead"]
            kategori_lain_ref = ft.Ref[ft.TextField]()
            
            def on_overhead_kategori_change(e):
                if e.control.value == "Lainnya":
                    kategori_lain_ref.current.visible = True
                else:
                    kategori_lain_ref.current.visible = False
                self.page.update()
            
            def add_overhead_kategori(e):
                new_kategori = kategori_lain_ref.current.value.strip()
                if new_kategori and new_kategori not in KATEGORI_OVERHEAD and new_kategori not in self._custom_categories["overhead"]:
                    self._custom_categories["overhead"].append(new_kategori)
                    kategori_dd.options.append(ft.dropdown.Option(new_kategori))
                    d["Kategori"] = new_kategori
                    kategori_lain_ref.current.visible = False
                    kategori_lain_ref.current.value = ""
                    self.page.update()
            
            kategori_dd = dd("Kategori", "Kategori", kategori_opts)
            kategori_dd.on_select = on_overhead_kategori_change
            
            fields = [
                tf("Nama", "Nama Overhead *"),
                kategori_dd,
                ft.TextField(
                    ref=kategori_lain_ref,
                    label="Kategori Lainnya",
                    hint_text="Masukkan kategori baru",
                    visible=False,
                    bgcolor=T.BG_CARD,
                ),
                ft.Container(
                    content=ft.Text("+ Tambah sebagai kategori baru", size=T.FONT_XS, color=T.PRIMARY),
                    on_click=add_overhead_kategori,
                    visible=False,
                    padding=ft.padding.symmetric(4, 8),
                    ink=True,
                ),
                dd("Satuan", "Satuan", SATUAN_OPTIONS),
                tf("Biaya_Per_Satuan", "Biaya/Satuan (Rp)", "number"),
            ]
        
        return fields

    def _save_item(self):
        d = self._form_data
        data = self._get_data()
        
        if self._active_tab == "Produk":
            urls = []
            for i, ref in enumerate(self._image_refs):
                if ref.current and ref.current.value:
                    urls.append(ref.current.value.strip())
            d["Gambar_URLs"] = urls
            d["Gambar_URL"] = urls[0] if urls else ""
            
            calc = self._calculate_hpp()
            d.update({
                "bahan_list": self._hpp_data["bahan_list"],
                "pewarna_list": self._hpp_data["pewarna_list"],
                "malam_list": self._hpp_data["malam_list"],
                "alat_list": self._hpp_data["alat_list"],
                "karyawan_list": self._hpp_data["karyawan_list"],
                "overhead_list": self._hpp_data["overhead_list"],
                "biaya_desain": self._hpp_data["biaya_desain"],
                "biaya_pengemasan": self._hpp_data["biaya_pengemasan"],
                "biaya_pengiriman": self._hpp_data["biaya_pengiriman"],
                "biaya_pajak": self._hpp_data["biaya_pajak"],
                "biaya_lainnya": self._hpp_data["biaya_lainnya"],
                "margin_persen": self._hpp_data["margin_persen"],
                "diskon_persen": self._hpp_data["diskon_persen"],
                "kuantitas": self._hpp_data["kuantitas"],
                "total_biaya_produksi": calc["total_produksi"],
                "HPP_Per_Unit": calc["hpp_per_unit"],
                "Harga_Jual": calc["harga_jual"],
                "Harga_Final": calc["harga_final"],
            })
        elif self._active_tab == "Proses":
            durasi_satuan = d.get("Durasi_Satuan", "Menit")
            durasi = d.get("Durasi", 0)
            biaya = d.get("Biaya_Per_Satuan", 0)
            try:
                durasi = float(durasi)
                biaya = float(biaya)
            except:
                durasi = 0
                biaya = 0
            if durasi_satuan == "Jam":
                d["Durasi_Menit"] = durasi * 60
                d["Biaya_Per_Menit"] = biaya / 60
                d["Biaya_Per_Proses"] = biaya
            else:
                d["Durasi_Menit"] = durasi
                d["Biaya_Per_Menit"] = biaya
                d["Biaya_Per_Proses"] = biaya * durasi
            
            if d.get("Kategori") == "Lainnya" and d.get("Nama"):
                if d["Nama"] not in KATEGORI_PROSES and d["Nama"] not in self._custom_categories["proses"]:
                    self._custom_categories["proses"].append(d["Nama"])
                d["Kategori"] = d["Nama"]
        elif self._active_tab == "Admin":
            if not d.get("password") and self._editing_id:
                for existing in data:
                    if existing.get("ID") == self._editing_id:
                        d["password"] = existing.get("password", "")
                        break

        if self._editing_id:
            idx = next((i for i, x in enumerate(data) if x.get("ID") == self._editing_id), None)
            if idx is not None:
                d["ID"] = self._editing_id
                data[idx] = dict(d)
                if self.state.local_db:
                    self.state.local_db.upsert(self._active_tab.lower(), d)
            show_snack(self.page, "✅ Data berhasil diperbarui!")
        else:
            new_id = self.db.generate_id(self._get_prefix(), data)
            d["ID"] = new_id
            data.append(dict(d))
            if self.state.local_db:
                self.state.local_db.upsert(self._active_tab.lower(), d)
            show_snack(self.page, f"✅ Data {new_id} berhasil ditambahkan!")

        self._form_container.visible = False
        self._form_data = {}
        self._editing_id = None
        self._refresh_list()

    def _delete_item(self, iid: str):
        data = self._get_data()
        idx = next((i for i, x in enumerate(data) if x.get("ID") == iid), None)
        if idx is not None:
            data.pop(idx)
            if self.state.local_db:
                self.state.local_db.delete(self._active_tab.lower(), iid)
        show_snack(self.page, "🗑️ Data berhasil dihapus!", T.WARNING)
        self._refresh_list()