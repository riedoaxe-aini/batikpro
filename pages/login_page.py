"""
LoginPage – Halaman Login Admin
"""

import flet as ft
import datetime
import os
from core.theme import BatikTheme as T

class LoginPage:
    def __init__(self, page, state, db, router):
        self.page = page
        self.state = state
        self.db = db
        self.router = router
        self.username_ref = ft.Ref[ft.TextField]()
        self.password_ref = ft.Ref[ft.TextField]()
        self.error_ref = ft.Ref[ft.Text]()

    def build(self):
        def on_login(e):
            username = self.username_ref.current.value
            password = self.password_ref.current.value
            
            if not username or not password:
                self.error_ref.current.value = "Username dan password harus diisi!"
                self.page.update()
                return
            
            # Check admin credentials
            admin_found = None
            for admin in self.state.admins:
                if admin.get("username") == username and admin.get("password") == password:
                    admin_found = admin
                    break
            
            if admin_found:
                # Save login history
                login_record = {
                    "username": username,
                    "nama": admin_found.get("nama", username),
                    "timestamp": datetime.datetime.now().isoformat(),
                    "status": "success"
                }
                if self.state.local_db:
                    self.state.local_db.upsert("login_history", login_record)
                
                # Set current user
                self.state.current_user = admin_found
                
                # Navigate to gallery
                if self.router is None:
                    from core.router import Router
                    self.router = Router(self.page, self.state, self.db)
                self.router.navigate("gallery")
            else:
                # Save failed login attempt
                login_record = {
                    "username": username,
                    "nama": username,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "status": "failed"
                }
                if self.state.local_db:
                    self.state.local_db.upsert("login_history", login_record)
                
                self.error_ref.current.value = "Username atau password salah!"
                self.page.update()

        # Logo - cek apakah file ada
        logo = ft.Container(
            content=ft.Image(
                src="assets/logo_login.png",
                width=300,
                height=100,
                fit="contain",
            ),
            margin=ft.margin.only(bottom=10),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=30),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    logo,
                                    ft.Text("BatikPro ERP", size=26, weight="w700", color=T.PRIMARY),
                                    ft.Text(
                                        "Aplikasi Manajemen & Kalkulasi HPP Batik",
                                        size=12,
                                        color=T.TEXT_SECONDARY,
                                        text_align="center",
                                    ),
                                    ft.Divider(height=1, color=T.DIVIDER),
                                    ft.Text("Login Admin", size=16, weight="w600", color=T.TEXT_PRIMARY),
                                    ft.Container(height=10),
                                    ft.TextField(
                                        ref=self.username_ref,
                                        label="Username",
                                        hint_text="Masukkan username",
                                        prefix_icon=ft.Icons.PERSON,
                                        bgcolor=T.BG_CARD,
                                        border_radius=8,
                                        width=320,
                                    ),
                                    ft.TextField(
                                        ref=self.password_ref,
                                        label="Password",
                                        hint_text="Masukkan password",
                                        prefix_icon=ft.Icons.LOCK,
                                        password=True,
                                        can_reveal_password=True,
                                        bgcolor=T.BG_CARD,
                                        border_radius=8,
                                        width=320,
                                    ),
                                    ft.Text(
                                        ref=self.error_ref,
                                        color=T.ERROR,
                                        size=T.FONT_SM,
                                        text_align="center",
                                    ),
                                    ft.Container(height=10),
                                    ft.ElevatedButton(
                                        "Masuk",
                                        on_click=on_login,
                                        style=ft.ButtonStyle(
                                            bgcolor=T.PRIMARY,
                                            color=T.TEXT_WHITE,
                                            padding=ft.padding.symmetric(20, 12),
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                        width=200,
                                    ),
                                ],
                                horizontal_alignment="center",
                                spacing=12,
                            ),
                            padding=ft.padding.all(30),
                            width=400,
                        ),
                        elevation=8,
                    ),
                    ft.Container(height=30),
                ],
                horizontal_alignment="center",
                expand=True,
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[T.BG_PRIMARY, T.BG_SECONDARY],
            ),
            expand=True,
        )