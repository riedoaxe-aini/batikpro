"""
Router – Manajemen Navigasi Halaman BatikPro
"""

import flet as ft
from core.app_state import AppState
from core.sheets_db import SheetsDB

class Router:
    def __init__(self, page: ft.Page, state: AppState, db: SheetsDB):
        self.page = page
        self.state = state
        self.db = db
        self._pages: dict = {}
        self._history: list = []
        self._register_pages()

    def _register_pages(self):
        from pages.home_page import HomePage
        from pages.gallery_page import GalleryPage
        from pages.product_detail_page import ProductDetailPage
        from pages.hpp_wizard_page import HppWizardPage
        from pages.crud_master_page import CrudMasterPage
        from pages.diskon_page import DiskonPage
        from pages.laporan_page import LaporanPage
        from pages.setting_page import SettingPage
        from pages.admin_page import AdminPage

        self._page_classes = {
            "home":           HomePage,
            "gallery":        GalleryPage,
            "product_detail": ProductDetailPage,
            "hpp_wizard":     HppWizardPage,
            "crud_master":    CrudMasterPage,
            "diskon":         DiskonPage,
            "laporan":        LaporanPage,
            "setting":        SettingPage,
            "admin":          AdminPage,
        }

    def navigate(self, page_name: str, **kwargs):
        if page_name in self._page_classes:
            self._history.append(self.state.current_page)
            self.state.current_page = page_name
            self.page.controls.clear()
            try:
                page_class = self._page_classes[page_name]
                page_instance = page_class(self.page, self.state, self.db, self, **kwargs)
                self.page.controls.append(page_instance.build())
                self.page.update()
                print(f"[Router] Navigated to: {page_name}")
            except Exception as e:
                print(f"[Router] Error: {e}")
                self._show_error_page(str(e))
        else:
            self._show_error_page(f"Page '{page_name}' not found")

    def _show_error_page(self, error_message: str):
        self.page.controls.clear()
        self.page.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color="red"),
                    ft.Text("Error", size=24, weight="bold"),
                    ft.Text(error_message, size=14, selectable=True),
                    ft.ElevatedButton("Kembali", on_click=lambda _: self.go_back()),
                ], horizontal_alignment="center", spacing=20),
                expand=True,
            )
        )
        self.page.update()

    def go_back(self):
        if self._history:
            prev = self._history.pop()
            self.navigate(prev)
        else:
            self.navigate("gallery")