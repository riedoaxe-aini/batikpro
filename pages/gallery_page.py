"""
GalleryPage – Halaman Galeri Produk Lengkap
Filter: Jenis, Halal, Eco, Range Harga
Sort: Harga, Nama, Terbaru
"""

import flet as ft
from core.theme import BatikTheme as T
from components.widgets import batik_appbar, BatikBottomNav, product_card, section_header

JENIS_OPTIONS = ["Semua", "Kain Batik", "Kemeja Batik", "Selendang", "Sandal", "Aksesoris", "Lainnya"]
SORT_OPTIONS  = ["Terbaru", "Harga: Rendah ke Tinggi", "Harga: Tinggi ke Rendah", "Nama A-Z"]

class GalleryPage:
    def __init__(self, page, state, db, router, **kwargs):
        self.page = page
        self.state = state
        self.db = db
        self.router = router

        self._search = state.search_query
        self._filter_jenis = state.filter_jenis
        self._filter_halal = "Semua"
        self._filter_eco = "Semua"
        self._filter_harga_min = 0
        self._filter_harga_max = 10000000
        self._sort = "Terbaru"
        self._grid_ref = ft.Ref[ft.Column]()
        self._count_ref = ft.Ref[ft.Text]()
        
        # Store dropdown references
        self._sort_dd_ref = ft.Ref[ft.Dropdown]()
        self._halal_dd_ref = ft.Ref[ft.Dropdown]()

    def build(self):
        def on_nav(index):
            # Order: Gallery(0), Toko(1), HPP(2), Master(3), Setelan(4)
            pages = ["gallery", "home", "hpp_wizard", "crud_master", "setting"]
            self.router.navigate(pages[index])

        def on_search_change(e):
            self._search = e.control.value
            self._refresh_grid()

        def on_product_tap(pid):
            def handler(_):
                self.state.current_produk_id = pid
                self.router.navigate("product_detail")
            return handler

        # ── AppBar ──
        appbar = batik_appbar(
            "Galeri Produk",
            on_back=lambda _: self.router.navigate("home"),
            subtitle=f"{len(self.state.produk)} produk",
        )

        # ── Search ──
        search_bar = ft.Container(
            content=ft.TextField(
                value=self._search,
                hint_text="Cari nama, motif, deskripsi...",
                prefix_icon=ft.Icons.SEARCH_ROUNDED,
                bgcolor=T.BG_CARD,
                on_change=on_search_change,
                hint_style=ft.TextStyle(color=T.TEXT_HINT, size=T.FONT_SM),
                height=48,
                content_padding=ft.padding.symmetric(0, 16),
            ),
            padding=ft.padding.symmetric(T.SPACE_SM, T.SPACE_LG),
        )

        # ── Filter Bar (Jenis) ──
        def make_jenis_chip(j):
            selected = self._filter_jenis == j
            def tap(_):
                self._filter_jenis = j
                self.state.filter_jenis = j
                self._refresh_grid()
            return ft.GestureDetector(
                content=ft.Container(
                    content=ft.Text(j, size=T.FONT_XS, color=T.TEXT_WHITE if selected else T.PRIMARY, weight="w600"),
                    bgcolor=T.PRIMARY if selected else ft.Colors.with_opacity(0.08, T.PRIMARY),
                    padding=ft.padding.symmetric(7, 12),
                    border=ft.border.all(1, T.PRIMARY) if not selected else None,
                ),
                on_tap=tap,
            )

        filter_row = ft.Container(
            content=ft.Row(
                [make_jenis_chip(j) for j in JENIS_OPTIONS],
                scroll="auto", spacing=6,
            ),
            padding=ft.padding.symmetric(T.SPACE_SM, T.SPACE_LG),
        )

        # ── Sort & Filter Row ──
        sort_dd = ft.Dropdown(
            ref=self._sort_dd_ref,
            value=self._sort,
            options=[ft.dropdown.Option(s) for s in SORT_OPTIONS],
            width=200,
        )
        sort_dd.on_select = lambda e: self._on_sort(e.control.value)

        halal_dd = ft.Dropdown(
            ref=self._halal_dd_ref,
            label="Halal",
            value=self._filter_halal,
            options=[ft.dropdown.Option(o) for o in ["Semua", "Halal", "Non-Halal"]],
            width=110,
        )
        halal_dd.on_select = lambda e: self._on_filter("halal", e.control.value)

        sort_filter_row = ft.Container(
            content=ft.Row([
                ft.Text("Urut:", size=T.FONT_SM, color=T.TEXT_HINT),
                sort_dd,
                ft.Container(expand=True),
                halal_dd,
            ], spacing=8, vertical_alignment="center"),
            padding=ft.padding.symmetric(T.SPACE_SM, T.SPACE_LG),
        )

        # ── Result Count ──
        count_bar = ft.Container(
            content=ft.Text(ref=self._count_ref, value="", size=T.FONT_SM, color=T.TEXT_HINT),
            padding=ft.padding.only(left=T.SPACE_LG, right=T.SPACE_LG, bottom=T.SPACE_SM),
        )

        # ── Grid ──
        grid_col = ft.Column(ref=self._grid_ref, spacing=T.SPACE_MD)
        self._on_product_tap = on_product_tap
        self._update_grid(grid_col)

        content = ft.ListView(
            [
                appbar,
                search_bar,
                filter_row,
                sort_filter_row,
                count_bar,
                ft.Container(
                    content=grid_col,
                    padding=ft.padding.symmetric(0, T.SPACE_LG),
                ),
                ft.Container(height=80),
            ],
            spacing=0, expand=True,
        )

        bottom_nav = BatikBottomNav(current_index=0, on_change=on_nav)

        return ft.Container(
            content=ft.Stack([
                ft.Column([content], expand=True),
                ft.Container(content=bottom_nav.build(), bottom=0, left=0, right=0),
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

    def _get_filtered_sorted(self):
        produk = self.state.produk

        # Filter by search query
        if self._search:
            q = self._search.lower()
            produk = [p for p in produk if q in p.get("Nama","").lower()
                      or q in p.get("Motif","").lower()
                      or q in p.get("Deskripsi","").lower()
                      or q in p.get("Jenis_Produk","").lower()]

        # Filter by jenis produk
        if self._filter_jenis != "Semua":
            produk = [p for p in produk if p.get("Jenis_Produk","") == self._filter_jenis]

        # Filter by halal
        if self._filter_halal == "Halal":
            produk = [p for p in produk if p.get("Halal","") == "Ya"]
        elif self._filter_halal == "Non-Halal":
            produk = [p for p in produk if p.get("Halal","") != "Ya"]

        # Sort
        def get_harga(p):
            try: 
                return float(p.get("Harga_Jual", 0))
            except: 
                return 0

        if self._sort == "Harga: Rendah ke Tinggi":
            produk = sorted(produk, key=get_harga)
        elif self._sort == "Harga: Tinggi ke Rendah":
            produk = sorted(produk, key=get_harga, reverse=True)
        elif self._sort == "Nama A-Z":
            produk = sorted(produk, key=lambda p: p.get("Nama",""))

        return produk

    def _update_grid(self, grid_col: ft.Column):
        produk = self._get_filtered_sorted()
        grid_col.controls.clear()
        cols = self._get_grid_columns()
        
        # Responsive grid menggunakan Row dengan wrap
        screen_width = self.state.screen_width
        card_width = (screen_width - (T.SPACE_LG * 2) - (T.SPACE_MD * (cols - 1))) / cols
        
        # Buat rows untuk grid
        rows = []
        for i in range(0, len(produk), cols):
            row_items = []
            for j in range(cols):
                if i + j < len(produk):
                    p = produk[i + j]
                    card = product_card(
                        p, 
                        self.state.format_currency, 
                        on_tap=self._on_product_tap(p.get("ID"))
                    )
                    row_items.append(
                        ft.Container(
                            content=card,
                            width=max(card_width, 140),
                            expand=True,
                        )
                    )
                else:
                    row_items.append(ft.Container(expand=True))
            rows.append(ft.Row(row_items, spacing=T.SPACE_MD))
        
        if rows:
            grid_col.controls.extend(rows)
        
        if not produk:
            grid_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=60, color=T.TEXT_HINT),
                        ft.Text("Produk tidak ditemukan", size=T.FONT_MD, color=T.TEXT_HINT),
                    ], horizontal_alignment="center", spacing=8),
                    expand=True,
                    padding=60,
                )
            )
        
        if self._count_ref.current:
            self._count_ref.current.value = f"Menampilkan {len(produk)} produk"

    def _refresh_grid(self):
        if self._grid_ref.current:
            self._update_grid(self._grid_ref.current)
            if self._count_ref.current:
                produk = self._get_filtered_sorted()
                self._count_ref.current.value = f"Menampilkan {len(produk)} produk"
            self.page.update()

    def _on_sort(self, val):
        self._sort = val
        self._refresh_grid()

    def _on_filter(self, key, val):
        if key == "halal":
            self._filter_halal = val
        self._refresh_grid()