"""
Components – Library Komponen UI Reusable BatikPro
Semua widget custom yang digunakan lintas halaman
"""

import flet as ft
from core.theme import BatikTheme as T
import base64

# ─────────────────────────────────────────────────────────────
# APPBAR / HEADER
# ─────────────────────────────────────────────────────────────

def batik_appbar(title: str, on_back=None, actions: list = None, subtitle: str = "", 
                 background_image: str = None) -> ft.Container:
    """AppBar dengan tema batik coklat atau gambar background"""
    left_section = []
    if on_back:
        left_section.append(
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                icon_size=20,
                on_click=on_back,
            )
        )

    title_col = ft.Column(
        [
            ft.Text(title, size=T.FONT_LG, weight="w700", color=T.TEXT_WHITE, no_wrap=True),
            *([] if not subtitle else [ft.Text(subtitle, size=T.FONT_XS, color=ft.Colors.with_opacity(0.8, T.TEXT_WHITE))]),
        ],
        spacing=0,
        tight=True,
    )

    right_actions = []
    if actions:
        right_actions = actions

    # If background image is provided, use it
    if background_image:
        return ft.Container(
            content=ft.Row(
                [
                    *left_section,
                    ft.Container(content=title_col, expand=True),
                    *right_actions,
                ],
                alignment="start",
                vertical_alignment="center",
            ),
            image=ft.DecorationImage(
                src=background_image,
                fit=ft.ImageFit.COVER,
            ),
            padding=ft.padding.only(left=8, right=8, top=48, bottom=12),
            shadow=T.SHADOW_MD,
        )
    else:
        return ft.Container(
            content=ft.Row(
                [
                    *left_section,
                    ft.Container(content=title_col, expand=True),
                    *right_actions,
                ],
                alignment="start",
                vertical_alignment="center",
            ),
            gradient=T.GRADIENT_PRIMARY,
            padding=ft.padding.only(left=8, right=8, top=48, bottom=12),
            shadow=T.SHADOW_MD,
        )

# ─────────────────────────────────────────────────────────────
# BOTTOM NAV
# ─────────────────────────────────────────────────────────────

class BatikBottomNav:
    def __init__(self, current_index: int, on_change):
        self.current_index = current_index
        self.on_change = on_change

    def _nav_item(self, icon, label, index):
        selected = self.current_index == index
        color = T.PRIMARY if selected else T.TEXT_HINT

        def tap(_):
            if self.on_change:
                self.on_change(index)

        return ft.GestureDetector(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=22),
                        bgcolor=ft.Colors.with_opacity(0.1, T.PRIMARY) if selected else ft.Colors.TRANSPARENT,
                        padding=6,
                    ),
                    ft.Text(label, size=T.FONT_XS, color=color, weight="w600" if selected else "w400"),
                ],
                horizontal_alignment="center",
                spacing=2,
            ),
            on_tap=tap,
            expand=True,
        )

    def build(self):
        # Order: Gallery, Toko, HPP, Master, Setelan
        return ft.Container(
            content=ft.Row(
                [
                    self._nav_item(ft.Icons.GRID_VIEW_ROUNDED, "Galeri", 0),
                    self._nav_item(ft.Icons.STOREFRONT_ROUNDED, "Toko", 1),
                    self._nav_item(ft.Icons.CALCULATE_ROUNDED, "HPP", 2),
                    self._nav_item(ft.Icons.INVENTORY_2_ROUNDED, "Master", 3),
                    self._nav_item(ft.Icons.SETTINGS_ROUNDED, "Setelan", 4),
                ],
                alignment="spaceAround",
            ),
            bgcolor=T.BG_CARD,
            shadow=T.SHADOW_MD,
            padding=ft.padding.only(top=8, bottom=20, left=4, right=4),
            border=ft.border.only(top=ft.BorderSide(1, T.DIVIDER)),
        )

# ─────────────────────────────────────────────────────────────
# PRODUCT CARD - Dengan informasi lengkap
# ─────────────────────────────────────────────────────────────

def product_card(produk: dict, format_currency, on_tap=None) -> ft.GestureDetector:
    """Kartu produk untuk galeri dengan status badges di bawah gambar"""
    nama = produk.get("Nama", "Produk")
    jenis = produk.get("Jenis_Produk", "")
    harga_str = produk.get("Harga_Jual", "0")
    harga_diskon_str = produk.get("Harga_Diskon", "")
    deskripsi = produk.get("Deskripsi", "")[:60]
    gambar = produk.get("Gambar_URL", "")
    if not gambar and produk.get("Gambar_URLs"):
        gambar = produk.get("Gambar_URLs", [])[0] if produk.get("Gambar_URLs") else ""
    
    # Status badges
    halal = produk.get("Halal", "") == "Ya"
    eco = produk.get("Eco_Friendly", "") == "Ya"
    preorder = produk.get("Preorder", "") == "Ya"
    ready = produk.get("Status", "") == "Aktif"
    special = produk.get("Special", "") == "Ya"
    premium = produk.get("Premium", "") == "Ya"
    
    # Stok
    stok_value = produk.get("Stok", 0)
    try:
        stok = float(stok_value) if stok_value else 0
    except (ValueError, TypeError):
        stok = 0
    
    # Price calculation
    try:
        harga = float(harga_str) if harga_str else 0
    except (ValueError, TypeError):
        harga = 0
    try:
        harga_diskon = float(harga_diskon_str) if harga_diskon_str else None
    except (ValueError, TypeError):
        harga_diskon = None

    # Status badges list - untuk ditampilkan di bawah gambar
    badges = []
    if halal:
        badges.append(_badge("Halal", T.BADGE_HALAL))
    if eco:
        badges.append(_badge("Eco", T.BADGE_ECO))
    if preorder:
        badges.append(_badge("Preorder", T.BADGE_PREORDER))
    if not ready:
        badges.append(_badge("Habis", T.BADGE_HABIS))
    if special:
        badges.append(_badge("Special", T.BADGE_SPECIAL))
    if premium:
        badges.append(_badge("Premium", T.BADGE_PREMIUM))

    # Gambar
    if gambar:
        img_content = ft.Image(
            src=gambar, 
            width=float('inf'), 
            height=150,
            fit="cover", 
            border_radius=ft.BorderRadius(T.RADIUS_MD, T.RADIUS_MD, 0, 0),
        )
    else:
        img_content = ft.Container(
            height=150,
            bgcolor=T.BG_SECONDARY,
            border_radius=ft.BorderRadius(T.RADIUS_MD, T.RADIUS_MD, 0, 0),
            content=ft.Icon(ft.Icons.IMAGE_OUTLINED, color=T.TEXT_HINT, size=40),
        )

    # Harga row
    if harga_diskon and harga > 0:
        diskon_persen = round((1 - harga_diskon / harga) * 100)
        harga_row = ft.Column([
            ft.Row([
                ft.Text(format_currency(harga_diskon), size=T.FONT_MD, weight="w700", color=T.PRIMARY),
                ft.Container(
                    content=ft.Text(f"-{diskon_persen}%", size=T.FONT_XS, color=T.TEXT_WHITE, weight="w700"),
                    bgcolor=T.ERROR, 
                    border_radius=4, 
                    padding=ft.padding.symmetric(2, 4)
                ),
            ], spacing=4),
            ft.Text(format_currency(harga), size=T.FONT_XS, color=T.TEXT_HINT, weight="w400"),
        ], spacing=2)
    else:
        harga_row = ft.Text(format_currency(harga), size=T.FONT_MD, weight="w700", color=T.PRIMARY)

    card = ft.Container(
        content=ft.Column(
            [
                # Gambar
                img_content,
                # Badges di bawah gambar (berjajar)
                ft.Container(
                    content=ft.Row(badges, spacing=4, wrap=True),
                    padding=ft.padding.symmetric(horizontal=8, vertical=6),
                ) if badges else ft.Container(),
                # Info
                ft.Container(
                    content=ft.Column([
                        ft.Text(nama, size=T.FONT_SM, weight="w600", color=T.TEXT_PRIMARY, 
                               max_lines=2, overflow="ellipsis"),
                        ft.Text(deskripsi, size=T.FONT_XS, color=T.TEXT_HINT, 
                               max_lines=2, overflow="ellipsis") if deskripsi else ft.Container(),
                        ft.Row([
                            ft.Text(jenis, size=T.FONT_XS, color=T.TEXT_HINT),
                            ft.Text(f"Stok: {stok:.0f}" if stok.is_integer() else f"Stok: {stok}", 
                                   size=T.FONT_XS, color=T.SUCCESS if stok > 0 else T.ERROR),
                        ], spacing=4, wrap=True),
                        harga_row,
                    ], spacing=4, tight=True),
                    padding=ft.padding.all(10),
                ),
            ],
            spacing=0,
        ),
        bgcolor=T.BG_CARD,
        shadow=T.SHADOW_SM,
        clip_behavior="hardEdge",
        border_radius=T.RADIUS_MD,
    )

    return ft.GestureDetector(content=card, on_tap=on_tap)

def _badge(label: str, color: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(label, size=T.FONT_XS - 1, color=T.TEXT_WHITE, weight="w600"),
        bgcolor=color,
        padding=ft.padding.symmetric(4, 8),
        border_radius=4,
    )

# ─────────────────────────────────────────────────────────────
# STAT CARD
# ─────────────────────────────────────────────────────────────

def stat_card(label: str, value: str, icon: str, color: str, subtitle: str = "") -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(icon, color=color, size=18),
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    border_radius=T.RADIUS_SM, padding=8,
                ),
                ft.Column([
                    ft.Text(value, size=T.FONT_XL, weight="w700", color=T.TEXT_PRIMARY),
                    ft.Text(label, size=T.FONT_XS, color=T.TEXT_HINT),
                    *([] if not subtitle else [ft.Text(subtitle, size=T.FONT_XS, color=color)]),
                ], spacing=0, tight=True, expand=True),
            ], spacing=10, vertical_alignment="center"),
        ], tight=True),
        bgcolor=T.BG_CARD,
        padding=T.SPACE_LG, shadow=T.SHADOW_SM, expand=True,
        border=ft.border.all(1, T.DIVIDER),
    )

# ─────────────────────────────────────────────────────────────
# INPUT FIELDS
# ─────────────────────────────────────────────────────────────

def batik_textfield(label: str, hint: str = "", value: str = "", prefix: str = "",
                     suffix: str = "", keyboard_type="text",
                     on_change=None, on_blur=None, multiline: bool = False,
                     read_only=False, password=False, can_reveal_password=False,
                     min_lines=None, ref=None) -> ft.TextField:
    kwargs = dict(
        ref=ref,
        label=label,
        hint_text=hint,
        value=value,
        keyboard_type=keyboard_type,
        on_change=on_change,
        on_blur=on_blur,
        multiline=multiline,
        read_only=read_only,
        password=password,
        can_reveal_password=can_reveal_password,
        bgcolor=T.BG_CARD,
    )
    if prefix:
        kwargs["prefix"] = prefix
    if suffix:
        kwargs["suffix"] = suffix
    if multiline:
        kwargs["min_lines"] = min_lines or 2
        kwargs["max_lines"] = 8
    return ft.TextField(**kwargs)

def batik_dropdown(label: str, options: list, value: str = "", on_change=None) -> ft.Dropdown:
    dropdown = ft.Dropdown(
        label=label,
        value=value,
        options=[ft.dropdown.Option(o) for o in options],
    )
    if on_change:
        dropdown.on_select = on_change
    return dropdown

# ─────────────────────────────────────────────────────────────
# BUTTONS
# ─────────────────────────────────────────────────────────────

def primary_button(text: str, on_click=None, icon: str = None, expand=False,
                   bgcolor=None, color=None) -> ft.Container:
    btn_content = ft.Row(
        [*([ ft.Icon(icon, size=16, color=color or T.TEXT_WHITE)] if icon else []),
         ft.Text(text, size=T.FONT_MD, weight="w600", color=color or T.TEXT_WHITE)],
        spacing=6, tight=True,
    )
    return ft.Container(
        content=btn_content,
        bgcolor=bgcolor or T.PRIMARY,
        padding=ft.padding.symmetric(14, 20),
        on_click=on_click,
        expand=expand,
        ink=True,
    )

def outline_button(text: str, on_click=None, icon: str = None, expand=False) -> ft.Container:
    btn_content = ft.Row(
        [*([ ft.Icon(icon, size=16, color=T.PRIMARY)] if icon else []),
         ft.Text(text, size=T.FONT_MD, weight="w600", color=T.PRIMARY)],
        spacing=6, tight=True,
    )
    return ft.Container(
        content=btn_content,
        border=ft.border.all(1.5, T.PRIMARY),
        padding=ft.padding.symmetric(14, 20),
        on_click=on_click,
        ink=True,
        expand=expand,
    )

# ─────────────────────────────────────────────────────────────
# SECTION HEADER
# ─────────────────────────────────────────────────────────────

def section_header(title: str, subtitle: str = "", action_label: str = "",
                   on_action=None) -> ft.Container:
    right = []
    if action_label:
        right.append(
            ft.Container(
                content=ft.Text(action_label, size=T.FONT_SM, weight="w600", color=T.PRIMARY),
                on_click=on_action, ink=True,
                padding=ft.padding.symmetric(4, 8),
            )
        )
    return ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text(title, size=T.FONT_LG, weight="w700", color=T.TEXT_PRIMARY),
                *([] if not subtitle else [ft.Text(subtitle, size=T.FONT_XS, color=T.TEXT_HINT)]),
            ], spacing=2, tight=True, expand=True),
            *right,
        ], alignment="spaceBetween"),
        padding=ft.padding.symmetric(0, 2),
    )

# ─────────────────────────────────────────────────────────────
# SNACKBAR / DIALOG
# ─────────────────────────────────────────────────────────────

def show_snack(page: ft.Page, message: str, color: str = None):
    """Show a snackbar message"""
    try:
        sb = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=color or T.SUCCESS,
        )
        page.open(sb)
    except Exception:
        try:
            sb = ft.SnackBar(
                content=ft.Text(message, color="white"),
                bgcolor=color or T.SUCCESS,
                open=True,
            )
            page.overlay.append(sb)
            page.update()
        except Exception as e:
            print(f"[snack] {message} ({e})")

def show_confirm_dialog(page: ft.Page, title: str, content: str,
                        on_confirm=None, on_cancel=None):
    def close_yes(_):
        dlg.open = False
        page.update()
        if on_confirm:
            on_confirm()

    def close_no(_):
        dlg.open = False
        page.update()
        if on_cancel:
            on_cancel()

    dlg = ft.AlertDialog(
        title=ft.Text(title, size=T.FONT_LG, weight="w700", color=T.TEXT_PRIMARY),
        content=ft.Text(content, color=T.TEXT_SECONDARY),
        actions=[
            ft.TextButton("Batal", on_click=close_no),
            ft.TextButton("Ya, Hapus", on_click=close_yes),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    dlg.open = True
    page.overlay.append(dlg)
    page.update()

# ─────────────────────────────────────────────────────────────
# LOADING OVERLAY
# ─────────────────────────────────────────────────────────────

def loading_overlay(message: str = "Memuat...") -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.ProgressRing(color=T.PRIMARY, stroke_width=3),
            ft.Text(message, size=T.FONT_SM, color=T.TEXT_SECONDARY),
        ], horizontal_alignment="center", spacing=12, tight=True),
        bgcolor=ft.Colors.with_opacity(0.7, T.BG_PRIMARY),
        expand=True,
    )

# ─────────────────────────────────────────────────────────────
# COST ROW (untuk HPP breakdown)
# ─────────────────────────────────────────────────────────────

def cost_row(label: str, value: str, color: str = None, bold: bool = False) -> ft.Row:
    return ft.Row([
        ft.Text(label, size=T.FONT_SM, color=T.TEXT_SECONDARY, expand=True),
        ft.Text(value, size=T.FONT_SM,
                color=color or T.TEXT_PRIMARY,
                weight="w700" if bold else "w500"),
    ], alignment="spaceBetween")

# ─────────────────────────────────────────────────────────────
# HPP SUMMARY CARD
# ─────────────────────────────────────────────────────────────

def hpp_summary_card(hpp: dict, format_currency) -> ft.Container:
    nama = hpp.get("Nama_Produk", "-")
    hpp_val = float(hpp.get("HPP_Per_Unit", 0))
    harga_jual = float(hpp.get("Harga_Jual", 0))
    harga_final = float(hpp.get("Harga_Final", 0))
    margin = float(hpp.get("Margin_Persen", 0))
    tanggal = hpp.get("Tanggal", "")[:10]

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text(nama, size=T.FONT_MD, weight="w700", color=T.TEXT_PRIMARY, expand=True),
                ft.Text(tanggal, size=T.FONT_XS, color=T.TEXT_HINT),
            ]),
            ft.Divider(height=1, color=T.DIVIDER),
            cost_row("HPP/unit", format_currency(hpp_val)),
            cost_row("Margin", f"{margin:.0f}%"),
            cost_row("Harga Jual", format_currency(harga_jual)),
            cost_row("Harga Final", format_currency(harga_final), T.PRIMARY, True),
        ], spacing=6, tight=True),
        bgcolor=T.BG_CARD,
        padding=T.SPACE_LG,
        shadow=T.SHADOW_SM,
        border=ft.border.all(1, T.DIVIDER),
    )

# ─────────────────────────────────────────────────────────────
# DISCOUNT BADGE CARD
# ─────────────────────────────────────────────────────────────

DISKON_ICONS = {
    "persen": ft.Icons.PERCENT_ROUNDED,
    "nominal": ft.Icons.MONEY_OFF_ROUNDED,
    "beli_x_gratis_y": ft.Icons.CARD_GIFTCARD_ROUNDED,
    "gratis_ongkir": ft.Icons.LOCAL_SHIPPING_ROUNDED,
}

DISKON_COLORS = {
    "persen": "#E53935",
    "nominal": "#8E24AA",
    "beli_x_gratis_y": "#00897B",
    "gratis_ongkir": "#F57F17",
}

def diskon_card(diskon: dict, on_tap=None) -> ft.GestureDetector:
    tipe = diskon.get("Tipe", "persen")
    color = DISKON_COLORS.get(tipe, T.PRIMARY)
    icon = DISKON_ICONS.get(tipe, ft.Icons.DISCOUNT_ROUNDED)
    nama = diskon.get("Nama", "Diskon")
    nilai = diskon.get("Nilai", "0")
    kode = diskon.get("Kode_Promo", "")
    deskripsi = diskon.get("Deskripsi", "")

    label_nilai = f"{nilai}%" if tipe == "persen" else f"Rp {float(nilai):,.0f}" if tipe == "nominal" else nilai

    card = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(icon, color=T.TEXT_WHITE, size=22),
                bgcolor=color, border_radius=T.RADIUS_SM, padding=10,
            ),
            ft.Column([
                ft.Row([
                    ft.Text(nama, size=T.FONT_MD, weight="w700", color=T.TEXT_PRIMARY, expand=True),
                    ft.Container(
                        content=ft.Text(label_nilai, size=T.FONT_SM, color=T.TEXT_WHITE, weight="w700"),
                        bgcolor=color, border_radius=T.RADIUS_FULL, padding=ft.padding.symmetric(3, 10),
                    ),
                ]),
                ft.Text(deskripsi, size=T.FONT_XS, color=T.TEXT_HINT, max_lines=2, overflow="ellipsis"),
                ft.Row([
                    ft.Icon(ft.Icons.LOCAL_OFFER_ROUNDED, size=12, color=T.TEXT_HINT),
                    ft.Text(kode, size=T.FONT_XS, color=T.TEXT_HINT, weight="w600"),
                ], spacing=3),
            ], expand=True, spacing=3, tight=True),
        ], spacing=12, vertical_alignment="start"),
        bgcolor=T.BG_CARD,
        padding=T.SPACE_MD, shadow=T.SHADOW_SM,
        border=ft.border.all(1, ft.Colors.with_opacity(0.3, color)),
    )
    return ft.GestureDetector(content=card, on_tap=on_tap)

# ─────────────────────────────────────────────────────────────
# FUNCTION TO UPDATE APPBAR BACKGROUND
# ─────────────────────────────────────────────────────────────

def update_appbar_background(image_url: str):
    """Function to update appbar background image (to be used by theme)"""
    # This function is a placeholder - actual implementation will update the global appbar style
    pass