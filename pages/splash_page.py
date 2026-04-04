"""
SplashPage - Minimal stub (main.py handles the actual splash + data loading)
Router memerlukan class ini sebagai entry point formal
"""
import flet as ft
from core.theme import BatikTheme as T

class SplashPage:
    def __init__(self, page, state, db, router, **kwargs):
        self.page = page
        self.state = state
        self.db = db
        self.router = router

    def build(self):
        # Splash sederhana - navigasi ke home sudah dihandle di main.py thread
        return ft.Container(
            content=ft.Column([
                ft.Text("🎨", size=72, text_align="center"),
                ft.Container(height=16),
                ft.Text("BatikPro ERP", size=28, weight="w700",
                        color=T.TEXT_WHITE, text_align="center"),
                ft.Text("Siap!", size=16, color=ft.Colors.with_opacity(0.9, T.TEXT_WHITE),
                        text_align="center"),
            ], horizontal_alignment="center", spacing=8, tight=True),
            alignment=ft.Alignment(0, 0),
            expand=True,
            gradient=T.GRADIENT_PRIMARY,
        )
