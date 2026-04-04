"""
HomePage – Halaman Utama Toko (seperti website toko online)
Header: nama toko, logo, deskripsi
Tengah: galeri produk unggulan + kategori
Footer: info toko
"""

import flet as ft
from core.theme import BatikTheme as T
from components.widgets import (
    BatikBottomNav, product_card, stat_card, section_header, show_snack
)

class HomePage:
    def __init__(self, page, state, db, router, **kwargs):
        self.page = page
        self.state = state
        self.db = db
        self.router = router
        self.search_ref = ft.Ref[ft.TextField]()

    def build(self) -> ft.Control:
        s = self.state.setting

        def on_nav(index):
            # Order: Gallery(0), Toko(1), HPP(2), Master(3), Setelan(4)
            pages = ["gallery", "home", "hpp_wizard", "crud_master", "setting"]
            self.router.navigate(pages[index])

        def on_search(e):
            query = e.control.value.strip()
            self.state.search_query = query
            self.router.navigate("gallery")

        def on_product_tap(pid):
            def handler(_):
                self.state.current_produk_id = pid
                self.router.navigate("product_detail")
            return handler

        # ── Header Toko ──
        header = self._build_header(s)

        # ── Search Bar ──
        search_bar = ft.Container(
            content=ft.Row([
                ft.TextField(
                    ref=self.search_ref,
                    hint_text="Cari produk batik...",
                    prefix_icon=ft.Icons.SEARCH_ROUNDED,
                    bgcolor=T.BG_CARD,
                    expand=True,
                    on_submit=on_search,
                    hint_style=ft.TextStyle(color=T.TEXT_HINT, size=T.FONT_SM),
                    height=48,
                    content_padding=ft.padding.symmetric(0, 16),
                ),
            ]),
            padding=ft.padding.symmetric(T.SPACE_SM, T.SPACE_LG),
        )

        # ── Kategori Chips ──
        jenis_list = ["Semua", "Kain Batik", "Kemeja Batik", "Selendang", "Sandal", "Aksesoris"]

        def make_chip(jenis):
            selected = self.state.filter_jenis == jenis

            def tap(_):
                self.state.filter_jenis = jenis
                self.router.navigate("gallery")

            return ft.GestureDetector(
                content=ft.Container(
                    content=ft.Text(jenis, size=T.FONT_XS, color=T.TEXT_WHITE if selected else T.PRIMARY,
                                    weight="w600"),
                    bgcolor=T.PRIMARY if selected else ft.Colors.with_opacity(0.08, T.PRIMARY),
                    padding=ft.padding.symmetric(8, 14),
                    border=ft.border.all(1, T.PRIMARY) if not selected else None,
                ),
                on_tap=tap,
            )

        kategori_row = ft.Container(
            content=ft.Row(
                [make_chip(j) for j in jenis_list],
                scroll="auto",
                spacing=8,
            ),
            padding=ft.padding.symmetric(0, T.SPACE_LG),
        )

        # ── Produk Unggulan (Responsive Grid) ──
        produk_all = self.state.produk
        cols = self._get_grid_columns()
        produk_unggulan = produk_all[:cols * 2]  # 2 rows
        
        screen_width = self.state.screen_width
        card_width = (screen_width - (T.SPACE_LG * 2) - (T.SPACE_MD * (cols - 1))) / cols
        
        produk_grid_rows = []
        for i in range(0, len(produk_unggulan), cols):
            row_items = []
            for j in range(cols):
                if i + j < len(produk_unggulan):
                    p = produk_unggulan[i + j]
                    card = product_card(p, self.state.format_currency, on_tap=on_product_tap(p.get("ID")))
                    row_items.append(
                        ft.Container(
                            content=card,
                            width=max(card_width, 140),
                            expand=True,
                        )
                    )
                else:
                    row_items.append(ft.Container(expand=True))
            produk_grid_rows.append(ft.Row(row_items, spacing=T.SPACE_MD))

        # ── HPP Summary Banner ──
        hpp_count = len(self.state.hpp_list)
        hpp_banner = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.CALCULATE_ROUNDED, color=T.TEXT_WHITE, size=28),
                    bgcolor=ft.Colors.with_opacity(0.2, T.TEXT_WHITE),
                    border_radius=T.RADIUS_SM, padding=10,
                ),
                ft.Column([
                    ft.Text("Kalkulator HPP Batik", size=T.FONT_MD, weight="w700", color=T.TEXT_WHITE),
                    ft.Text(f"{hpp_count} kalkulasi tersimpan", size=T.FONT_XS, color=ft.Colors.with_opacity(0.85, T.TEXT_WHITE)),
                ], spacing=2, tight=True, expand=True),
                ft.Container(
                        content=ft.Row([ft.Text("Hitung HPP", color="white", weight="w600", size=12)], spacing=4, tight=True),
                        bgcolor=T.PRIMARY,
                        padding=ft.padding.symmetric(8, 14),
                        on_click=lambda _: self.router.navigate("hpp_wizard"),
                        ink=True,
                    ),
            ], spacing=12, vertical_alignment="center"),
            gradient=T.GRADIENT_INDIGO,
            padding=T.SPACE_LG,
            margin=ft.margin.symmetric(0, T.SPACE_LG),
            shadow=T.SHADOW_MD,
        )

        # ── Stats Row ──
        total_produk = len(produk_all)
        total_aktif = sum(1 for p in produk_all if p.get("Status", "") == "Aktif")
        
        stats_row = ft.Container(
            content=ft.Row([
                stat_card("Total Produk", str(total_produk), ft.Icons.INVENTORY_2_ROUNDED, T.PRIMARY),
                ft.Container(width=T.SPACE_SM),
                stat_card("Produk Aktif", str(total_aktif), ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, T.SUCCESS),
            ], spacing=0),
            padding=ft.padding.symmetric(0, T.SPACE_LG),
        )

        # ── Footer ──
        footer = self._build_footer(s)

        # ── Scroll Content ──
        content = ft.ListView(
            [
                header,
                search_bar,
                kategori_row,
                stats_row,
                hpp_banner,
                ft.Container(
                    content=ft.Column([
                        section_header(
                            "Produk Unggulan", f"{total_produk} produk tersedia",
                            "Lihat Semua", on_action=lambda _: self.router.navigate("gallery")
                        ),
                        ft.Container(height=T.SPACE_SM),
                        *produk_grid_rows,
                    ], spacing=T.SPACE_MD),
                    padding=ft.padding.symmetric(0, T.SPACE_LG),
                ),
                ft.Container(height=T.SPACE_MD),
                footer,
                ft.Container(height=80),
            ],
            spacing=0,
            expand=True,
        )

        bottom_nav = BatikBottomNav(current_index=1, on_change=on_nav)

        return ft.Container(
            content=ft.Stack([
                ft.Column([content], expand=True),
                ft.Container(
                    content=bottom_nav.build(),
                    bottom=0, left=0, right=0,
                ),
            ]),
            bgcolor=T.BG_PRIMARY,
            expand=True,
        )

    def _get_grid_columns(self):
        """Get number of grid columns based on screen size and orientation"""
        w = self.state.screen_width
        h = self.state.screen_height
        is_landscape = w > h
        
        if self.state.is_tv:
            return 7
        elif is_landscape and self.state.is_tablet:
            return 5
        elif self.state.is_tablet:
            return 4
        elif is_landscape:
            return 4
        else:
            return 2

    def _build_header(self, s) -> ft.Container:
        shop_name = s.nama_toko
        shop_desc = s.deskripsi

        logo_widget: ft.Control
        if s.logo_url:
            logo_widget = ft.Image(
                src=s.logo_url,
                width=56, height=56, 
                fit="cover", 
                border_radius=T.RADIUS_SM
            )
        else:
            logo_widget = ft.Container(
                content=ft.Text("🎨", size=28),
                width=56, height=56,
                bgcolor=ft.Colors.with_opacity(0.2, T.TEXT_WHITE),
            )

        return ft.Container(
            content=ft.Column([
                ft.Container(height=48),
                ft.Row([
                    logo_widget,
                    ft.Column([
                        ft.Text(shop_name, size=T.FONT_XL, weight="w700",
                                color=T.TEXT_WHITE),
                        ft.Text(shop_desc, size=T.FONT_XS,
                                color=ft.Colors.with_opacity(0.85, T.TEXT_WHITE),
                                max_lines=2, overflow="ellipsis"),
                    ], spacing=2, tight=True, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                        icon_color=ft.Colors.with_opacity(0.9, T.TEXT_WHITE),
                        icon_size=22,
                    ),
                ], spacing=12, vertical_alignment="center"),
                ft.Container(height=T.SPACE_MD),
            ], spacing=0, tight=True),
            gradient=T.GRADIENT_PRIMARY,
            padding=ft.padding.only(left=T.SPACE_LG, right=T.SPACE_LG, bottom=T.SPACE_XL),
            shadow=T.SHADOW_MD,
        )

    def _build_footer(self, s) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Divider(color=T.DIVIDER, height=1),
                ft.Container(
                    content=ft.Column([
                        ft.Text(s.nama_toko, size=T.FONT_MD, weight="w700",
                                color=T.PRIMARY),
                        ft.Text(s.deskripsi, size=T.FONT_XS, color=T.TEXT_SECONDARY,
                                text_align="center"),
                        ft.Container(height=T.SPACE_SM),
                        ft.Row([
                            _footer_link(ft.Icons.PHONE_ROUNDED, s.no_hp or "-"),
                            ft.Container(width=T.SPACE_LG),
                            _footer_link(ft.Icons.EMAIL_ROUNDED, s.email or "-"),
                        ], alignment="center"),
                        ft.Row([
                            _footer_link(ft.Icons.CAMERA_ALT_ROUNDED, s.instagram or "-"),
                            ft.Container(width=T.SPACE_LG),
                            _footer_link(ft.Icons.LANGUAGE_ROUNDED, s.website or "-"),
                        ], alignment="center"),
                        ft.Container(height=T.SPACE_SM),
                        ft.Text(s.footer_text, size=T.FONT_XS, color=T.TEXT_HINT,
                                text_align="center"),
                    ], horizontal_alignment="center", spacing=6, tight=True),
                    padding=T.SPACE_LG,
                ),
            ], spacing=0, tight=True),
            bgcolor=T.BG_SECONDARY,
        )

def _footer_link(icon, text) -> ft.Row:
    return ft.Row([
        ft.Icon(icon, size=13, color=T.TEXT_HINT),
        ft.Text(text, size=T.FONT_XS, color=T.TEXT_SECONDARY),
    ], spacing=4, tight=True)