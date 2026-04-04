"""
ProductDetailPage – Halaman Detail Produk dengan semua informasi
"""

import flet as ft
from core.theme import BatikTheme as T
from components.widgets import batik_appbar, cost_row

class ProductDetailPage:
    def __init__(self, page, state, db, router, **kwargs):
        self.page = page
        self.state = state
        self.db = db
        self.router = router
        self.produk_id = state.current_produk_id
        self.produk = state.get_produk_by_id(self.produk_id) if self.produk_id else None
        self.current_image_index = 0

    def build(self):
        if not self.produk:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=T.ERROR),
                    ft.Text("Produk tidak ditemukan", size=T.FONT_MD, color=T.TEXT_SECONDARY),
                    ft.ElevatedButton("Kembali", on_click=lambda _: self.router.go_back())
                ], horizontal_alignment="center", spacing=20),
                expand=True,
            )
        
        p = self.produk
        nama = p.get("Nama", "Produk")
        jenis = p.get("Jenis_Produk", "")
        deskripsi = p.get("Deskripsi", "")
        motif = p.get("Motif", "")
        asal_daerah = p.get("Asal_Daerah", "")
        dimensi = p.get("Dimensi", "")
        berat = p.get("Berat_Gram", 0)
        warna_dominan = p.get("Warna_Dominan", "")
        tingkat_kesulitan = p.get("Tingkat_Kesulitan", "")
        jenis_batik = p.get("Jenis_Batik", "")
        
        # Status
        halal = p.get("Halal", "")
        eco = p.get("Eco_Friendly", "")
        preorder = p.get("Preorder", "")
        special = p.get("Special", "")
        premium = p.get("Premium", "")
        status = p.get("Status", "")
        stok = p.get("Stok", 0)
        try:
            stok = float(stok) if stok else 0
        except:
            stok = 0

        # Kemudian gunakan stok untuk perbandingan
        stok_color = T.SUCCESS if stok > 0 else T.ERROR
        
        # HPP Calculation
        hpp_per_unit = p.get("HPP_Per_Unit", 0)
        harga_jual = p.get("Harga_Jual", 0)
        harga_final = p.get("Harga_Final", 0)
        margin = p.get("margin_persen", 30)
        diskon = p.get("diskon_persen", 0)
        
        # Biaya komponen
        bahan_list = p.get("bahan_list", [])
        pewarna_list = p.get("pewarna_list", [])
        malam_list = p.get("malam_list", [])
        alat_list = p.get("alat_list", [])
        karyawan_list = p.get("karyawan_list", [])
        overhead_list = p.get("overhead_list", [])
        biaya_desain = p.get("biaya_desain", 0)
        biaya_pengemasan = p.get("biaya_pengemasan", 0)
        biaya_pengiriman = p.get("biaya_pengiriman", 0)
        biaya_pajak = p.get("biaya_pajak", 0)
        biaya_lainnya = p.get("biaya_lainnya", 0)
        
        fc = self.state.format_currency
        
        # Get multiple images
        gambar_urls = p.get("Gambar_URLs", [])
        if not gambar_urls and p.get("Gambar_URL"):
            gambar_urls = [p.get("Gambar_URL")]
        elif isinstance(gambar_urls, str):
            gambar_urls = [u.strip() for u in gambar_urls.split(",") if u.strip()]
        
        def prev_image(_):
            if gambar_urls:
                self.current_image_index = (self.current_image_index - 1) % len(gambar_urls)
                self._update_image(gambar_urls)
        
        def next_image(_):
            if gambar_urls:
                self.current_image_index = (self.current_image_index + 1) % len(gambar_urls)
                self._update_image(gambar_urls)
        
        self._image_ref = ft.Ref[ft.Image]()
        
        # Build image slider
        if gambar_urls:
            image_slider = ft.Column([
                ft.Stack([
                    ft.Image(
                        ref=self._image_ref,
                        src=gambar_urls[0],
                        width=self.page.width or 400,
                        height=300,
                        fit="contain",
                        border_radius=ft.BorderRadius(T.RADIUS_MD, T.RADIUS_MD, T.RADIUS_MD, T.RADIUS_MD),
                    ),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_IOS,
                            icon_color=T.TEXT_WHITE,
                            bgcolor=ft.Colors.with_opacity(0.5, "#000000"),
                            on_click=prev_image,
                        ),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.ARROW_FORWARD_IOS,
                            icon_color=T.TEXT_WHITE,
                            bgcolor=ft.Colors.with_opacity(0.5, "#000000"),
                            on_click=next_image,
                        ),
                    ], alignment="spaceBetween"),
                ]),
                ft.Container(
                    content=ft.Row(
                        [ft.Container(
                            width=8, height=8,
                            bgcolor=T.PRIMARY if i == self.current_image_index else T.TEXT_HINT,
                            border_radius=4,
                        ) for i in range(len(gambar_urls))],
                        spacing=4, alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(top=8),
                ),
            ], spacing=0)
        else:
            image_slider = ft.Container(
                content=ft.Icon(ft.Icons.IMAGE_OUTLINED, size=100, color=T.TEXT_HINT),
                width=self.page.width or 400,
                height=300,
                bgcolor=T.BG_SECONDARY,
                border_radius=T.RADIUS_MD,
            )
        
        # Status badges
        badges = []
        if halal == "Ya":
            badges.append(_badge("Halal", T.BADGE_HALAL))
        if eco == "Ya":
            badges.append(_badge("Eco", T.BADGE_ECO))
        if preorder == "Ya":
            badges.append(_badge("Preorder", T.BADGE_PREORDER))
        if special == "Ya":
            badges.append(_badge("Special", T.BADGE_SPECIAL))
        if premium == "Ya":
            badges.append(_badge("Premium", T.BADGE_PREMIUM))
        
        # Status produk
        status_color = T.SUCCESS if status == "Aktif" else (T.WARNING if status == "Preorder" else T.ERROR)
        
        # Harga display
        if diskon > 0:
            harga_display = ft.Column([
                ft.Row([
                    ft.Text(fc(harga_final), size=T.FONT_XL, weight="w700", color=T.PRIMARY),
                    ft.Container(
                        content=ft.Text(f"-{diskon:.0f}%", size=T.FONT_SM, color=T.TEXT_WHITE, weight="w700"),
                        bgcolor=T.ERROR, border_radius=4, padding=ft.padding.symmetric(4, 8),
                    ),
                ], spacing=8),
                ft.Row([
                    ft.Text(fc(harga_jual), size=T.FONT_SM, color=T.TEXT_HINT),
                    ft.Text("(sebelum diskon)", size=T.FONT_XS, color=T.TEXT_HINT),
                ], spacing=4),
            ], spacing=2)
        else:
            harga_display = ft.Text(fc(harga_jual), size=T.FONT_XL, weight="w700", color=T.PRIMARY)
        
        content = ft.ListView(
            [
                batik_appbar(nama, on_back=lambda _: self.router.go_back()),
                ft.Container(
                    content=ft.Column([
                        image_slider,
                        ft.Container(height=T.SPACE_MD),
                        ft.Row(badges, spacing=4, wrap=True) if badges else ft.Container(),
                        ft.Text(f"Jenis: {jenis}", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                        ft.Text(f"Jenis Batik: {jenis_batik or '-'}", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                        ft.Text(f"Motif: {motif or '-'}", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                        ft.Text(f"Asal Daerah: {asal_daerah or '-'}", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                        ft.Text(f"Dimensi: {dimensi or '-'}", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                        ft.Text(f"Berat: {berat} gram" if berat else "-", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                        ft.Text(f"Warna Dominan: {warna_dominan or '-'}", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                        ft.Text(f"Tingkat Kesulitan: {tingkat_kesulitan or '-'}/10", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                        ft.Divider(color=T.DIVIDER),
                        ft.Text("Deskripsi:", size=T.FONT_MD, weight="w600"),
                        ft.Text(deskripsi or "-", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                        ft.Divider(color=T.DIVIDER),
                        ft.Text("💰 Harga & Stok:", size=T.FONT_MD, weight="w600"),
                        ft.Row([
                            ft.Text("Harga:", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                            ft.Container(expand=True),
                            harga_display,
                        ], alignment="spaceBetween"),
                        ft.Row([
                            ft.Text("Stok:", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                            ft.Container(expand=True),
                            ft.Text(str(stok), size=T.FONT_MD, weight="w700",
                                   color=T.SUCCESS if stok > 0 else T.ERROR),
                        ], alignment="spaceBetween"),
                        ft.Row([
                            ft.Text("Status:", size=T.FONT_SM, color=T.TEXT_SECONDARY),
                            ft.Container(expand=True),
                            ft.Text(status, size=T.FONT_SM, weight="w600", color=status_color),
                        ], alignment="spaceBetween"),
                        ft.Divider(color=T.DIVIDER),
                        ft.Text("📊 Kalkulasi HPP:", size=T.FONT_MD, weight="w600"),
                        cost_row("HPP per Unit", fc(hpp_per_unit), T.PRIMARY, True),
                        cost_row("Margin", f"{margin:.0f}%"),
                        cost_row("Diskon", f"{diskon:.0f}%"),
                        ft.Divider(color=T.DIVIDER),
                        ft.Text("🧾 Komponen Biaya:", size=T.FONT_MD, weight="w600"),
                        cost_row("Biaya Desain", fc(biaya_desain)),
                        cost_row("Biaya Pengemasan", fc(biaya_pengemasan)),
                        cost_row("Biaya Pengiriman", fc(biaya_pengiriman)),
                        cost_row("Pajak", fc(biaya_pajak)),
                        cost_row("Biaya Lainnya", fc(biaya_lainnya)),
                        ft.Text("Bahan:", size=T.FONT_SM, weight="w600"),
                        *[ft.Text(f"• {b.get('nama')} x{b.get('jumlah', 1)} = {fc(b.get('subtotal', 0))}", 
                                 size=T.FONT_XS) for b in bahan_list[:3]],
                        ft.Text("Pewarna:", size=T.FONT_SM, weight="w600"),
                        *[ft.Text(f"• {p.get('nama')} x{p.get('jumlah', 1)} = {fc(p.get('subtotal', 0))}", 
                                 size=T.FONT_XS) for p in pewarna_list[:3]],
                        ft.Text("Alat:", size=T.FONT_SM, weight="w600"),
                        *[ft.Text(f"• {a.get('nama')} {a.get('durasi_menit', 0)} menit = {fc(a.get('subtotal', 0))}", 
                                 size=T.FONT_XS) for a in alat_list[:3]],
                        ft.Text("Karyawan:", size=T.FONT_SM, weight="w600"),
                        *[ft.Text(f"• {k.get('nama')} {k.get('durasi_menit', 0)} menit = {fc(k.get('subtotal', 0))}", 
                                 size=T.FONT_XS) for k in karyawan_list[:3]],
                        ft.Container(height=80),
                    ], spacing=T.SPACE_SM),
                    padding=ft.padding.all(T.SPACE_LG),
                ),
            ],
            spacing=0,
            expand=True,
        )
        
        return ft.Container(
            content=content,
            bgcolor=T.BG_PRIMARY,
            expand=True,
        )
    
    def _update_image(self, gambar_urls):
        if self._image_ref.current and gambar_urls:
            self._image_ref.current.src = gambar_urls[self.current_image_index]
            self.page.update()

def _badge(label: str, color: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(label, size=T.FONT_XS - 1, color=T.TEXT_WHITE, weight="w600"),
        bgcolor=color,
        padding=ft.padding.symmetric(4, 8),
        border_radius=4,
    )