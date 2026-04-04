"""
DiskonPage – Manajemen Diskon Lengkap
Tipe: persen, nominal, beli_x_gratis_y, gratis_ongkir, flash_sale, member, cashback, bundling
"""

import flet as ft
from core.theme import BatikTheme as T
from components.widgets import (
    batik_appbar, BatikBottomNav, diskon_card, primary_button, outline_button,
    show_snack, show_confirm_dialog, DISKON_COLORS
)

TIPE_DISKON = [
    "persen", "nominal", "beli_x_gratis_y", "gratis_ongkir",
    "flash_sale", "cashback", "bundling", "member"
]
TIPE_LABELS = {
    "persen": "Diskon % (Persen)",
    "nominal": "Diskon Nominal (Rp)",
    "beli_x_gratis_y": "Beli X Gratis Y",
    "gratis_ongkir": "Gratis Ongkir",
    "flash_sale": "Flash Sale",
    "cashback": "Cashback",
    "bundling": "Bundling / Paket",
    "member": "Diskon Member",
}
HARI_LIST = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]

class DiskonPage:
    def __init__(self, page, state, db, router, **kwargs):
        self.page = page
        self.state = state
        self.db = db
        self.router = router
        self._form_visible = False
        self._form_data: dict = {}
        self._editing_id: str = None
        self._list_ref = ft.Ref[ft.Column]()
        self._form_container = ft.Container(visible=False)

    def build(self):
        def on_nav(index):
            pages = ["home", "gallery", "hpp_wizard", "crud_master", "setting"]
            self.router.navigate(pages[index])

        list_col = ft.Column(ref=self._list_ref, spacing=T.SPACE_SM)
        self._refresh_list_widget(list_col)

        content = ft.ListView([
            batik_appbar("Manajemen Diskon", on_back=lambda _: self.router.navigate("home"),
                          subtitle="Setting promo & potongan harga"),
            ft.Container(
                content=ft.Row([
                    ft.Text("Tipe Diskon Tersedia", size=T.FONT_MD, weight="w700", color=T.TEXT_PRIMARY, expand=True),
                    ft.Container(
                        content=ft.Row([ft.Icon(ft.Icons.ADD_ROUNDED, size=14, color="white"), ft.Text("+ Buat Diskon", color="white", weight="w600", size=12)], spacing=4, tight=True),
                        bgcolor=T.PRIMARY,
                        padding=ft.padding.symmetric(8, 14),
                        on_click=self._show_add_form, ink=True,
                    ),
                ]),
                padding=ft.padding.symmetric(T.SPACE_SM, T.SPACE_LG),
            ),
            # Tipe chips informasi
            ft.Container(
                content=ft.Row(
                    [self._tipe_chip(t) for t in TIPE_DISKON],
                    scroll="auto", spacing=6,
                ),
                padding=ft.padding.symmetric(0, T.SPACE_LG),
            ),
            ft.Divider(color=T.DIVIDER),
            self._form_container,
            ft.Container(content=list_col, padding=ft.padding.symmetric(0, T.SPACE_LG)),
            ft.Container(height=80),
        ], spacing=0, expand=True)

        bottom_nav = BatikBottomNav(current_index=3, on_change=on_nav)

        return ft.Container(
            content=ft.Stack([
                ft.Column([content], expand=True),
                ft.Container(content=bottom_nav.build(), bottom=0, left=0, right=0),
            ]),
            bgcolor=T.BG_PRIMARY, expand=True,
        )

    def _tipe_chip(self, tipe: str) -> ft.Container:
        color = DISKON_COLORS.get(tipe, T.PRIMARY)
        return ft.Container(
            content=ft.Text(TIPE_LABELS.get(tipe, tipe), size=T.FONT_XS, color=color, weight="w600"),
            bgcolor=ft.Colors.with_opacity(0.1, color),
            padding=ft.padding.symmetric(6, 12),
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, color)),
        )

    def _refresh_list_widget(self, col: ft.Column):
        col.controls.clear()
        diskon_list = self.state.diskon
        if not diskon_list:
            col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.DISCOUNT_OUTLINED, size=50, color=T.TEXT_HINT),
                        ft.Text("Belum ada diskon", size=T.FONT_SM, color=T.TEXT_HINT),
                    ], horizontal_alignment="center", spacing=8),
                    alignment=ft.Alignment(0, 0), padding=40,
                )
            )
            return

        for d in diskon_list:
            did = d.get("ID")
            col.controls.append(ft.Column([
                diskon_card(d),
                ft.Row([
                    ft.TextButton(
                        "Edit", icon=ft.Icons.EDIT_ROUNDED,
                        on_click=lambda _, dd=d: self._on_edit(dd),
                    ),
                    ft.TextButton(
                        "Hapus", icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                        on_click=lambda _, dd=d: self._on_delete(dd),
                    ),
                    ft.Container(
                        content=ft.Text(
                            "Aktif" if d.get("Status","") == "Aktif" else "Nonaktif",
                            size=T.FONT_XS, weight="w600",
                            color=T.SUCCESS if d.get("Status","") == "Aktif" else T.TEXT_HINT,
                        ),
                        expand=True,
                    ),
                ], spacing=0),
            ], spacing=2, tight=True))

    def _refresh_list(self):
        if self._list_ref.current:
            self._refresh_list_widget(self._list_ref.current)
        self.page.update()

    def _show_add_form(self, _=None):
        self._editing_id = None
        self._form_data = {}
        self._form_visible = True
        self._build_form()
        self._form_container.visible = True
        self.page.update()

    def _on_edit(self, d: dict):
        self._editing_id = d.get("ID")
        self._form_data = dict(d)
        self._form_visible = True
        self._build_form()
        self._form_container.visible = True
        self.page.update()

    def _on_delete(self, d: dict):
        def confirm():
            self.state.diskon = [x for x in self.state.diskon if x.get("ID") != d.get("ID")]
            if self.db.is_configured():
                idx = next((i for i, x in enumerate(self.state.diskon) if x.get("ID") == d.get("ID")), None)
                if idx is not None:
                    self.db.delete_row("diskon", idx)
            show_snack(self.page, "🗑️ Diskon berhasil dihapus!", T.WARNING)
            self._refresh_list()

        show_confirm_dialog(self.page, "Hapus Diskon", f"Hapus {d.get('Nama','')}?", on_confirm=confirm)

    def _build_form(self):
        d = self._form_data
        is_edit = self._editing_id is not None

        def tf(key, label, ktype="text"):
            return ft.TextField(
                label=label, value=d.get(key, ""),
                keyboard_type=ktype,
                label_style=ft.TextStyle(size=T.FONT_SM, color=T.TEXT_SECONDARY),
                on_change=lambda e, k=key: d.update({k: e.control.value}),
            )

        def dd(key, label, opts):
            return ft.Dropdown(
                label=label, value=d.get(key, opts[0] if opts else ""),
                options=[ft.dropdown.Option(o) for o in opts],
                label_style=ft.TextStyle(size=T.FONT_SM, color=T.TEXT_SECONDARY),
                on_change=lambda e, k=key: d.update({k: e.control.value}),
            )

        form = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"{'Edit' if is_edit else 'Buat'} Diskon", size=T.FONT_MD,
                             weight="w700", color=T.TEXT_PRIMARY, expand=True),
                    ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, icon_color=T.TEXT_HINT, icon_size=18,
                                   on_click=lambda _: self._hide_form()),
                ]),
                tf("Nama", "Nama Diskon *"),
                dd("Tipe", "Tipe Diskon", [TIPE_LABELS[t] for t in TIPE_DISKON]),
                tf("Nilai", "Nilai (% atau Rp atau X:Y)", "text"),
                tf("Min_Pembelian", "Min. Pembelian (Rp)", "number"),
                tf("Max_Diskon", "Maks. Diskon (Rp, opsional)", "number"),
                ft.Row([
                    ft.Container(content=tf("Berlaku_Mulai", "Berlaku Mulai (YYYY-MM-DD)"), expand=True),
                    ft.Container(width=8),
                    ft.Container(content=tf("Berlaku_Sampai", "Berlaku Sampai (YYYY-MM-DD)"), expand=True),
                ]),
                ft.Row([
                    ft.Container(content=tf("Jam_Mulai", "Jam Mulai (HH:MM)"), expand=True),
                    ft.Container(width=8),
                    ft.Container(content=tf("Jam_Selesai", "Jam Selesai (HH:MM)"), expand=True),
                ]),
                tf("Hari_Berlaku", "Hari Berlaku (cth: Senin,Sabtu)"),
                tf("Kode_Promo", "Kode Promo"),
                tf("Deskripsi", "Deskripsi"),
                dd("Status", "Status", ["Aktif", "Nonaktif"]),
                ft.Container(height=T.SPACE_SM),
                ft.Row([
                    outline_button("Batal", on_click=lambda _: self._hide_form()),
                    ft.Container(width=8),
                    primary_button("Simpan Diskon", icon=ft.Icons.SAVE_ROUNDED,
                                   on_click=lambda _: self._save_diskon(), expand=True),
                ]),
            ], spacing=T.SPACE_SM, tight=True),
            bgcolor=T.BG_CARD, border_radius=T.RADIUS_LG, padding=T.SPACE_LG,
            border=ft.border.all(1.5, T.ACCENT),
            margin=ft.margin.symmetric(0, T.SPACE_LG),
            shadow=T.SHADOW_MD,
        )
        self._form_container.content = form

    def _hide_form(self):
        self._form_container.visible = False
        self._form_data = {}
        self._editing_id = None
        self.page.update()

    def _save_diskon(self):
        d = self._form_data
        # Convert tipe label back to key
        for k, v in TIPE_LABELS.items():
            if d.get("Tipe") == v:
                d["Tipe"] = k
                break

        if self._editing_id:
            idx = next((i for i, x in enumerate(self.state.diskon) if x.get("ID") == self._editing_id), None)
            if idx is not None:
                d["ID"] = self._editing_id
                self.state.diskon[idx] = dict(d)
                if self.db.is_configured():
                    self.db.update_row("diskon", idx, d)
            show_snack(self.page, "✅ Diskon berhasil diperbarui!")
        else:
            new_id = self.db.generate_id("DSK", self.state.diskon)
            d["ID"] = new_id
            self.state.diskon.append(dict(d))
            if self.db.is_configured():
                self.db.append_row("diskon", d)
            show_snack(self.page, f"✅ Diskon {new_id} berhasil disimpan!")

        self._hide_form()
        self._refresh_list()
