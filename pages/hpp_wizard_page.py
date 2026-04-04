"""
HppWizardPage – Calculator HPP Batik untuk menghitung biaya produksi
"""

import flet as ft
import datetime
from core.theme import BatikTheme as T
from components.widgets import (
    batik_appbar, BatikBottomNav, batik_textfield, batik_dropdown,
    primary_button, outline_button, show_snack, cost_row, section_header
)

class HppWizardPage:
    def __init__(self, page, state, db, router, **kwargs):
        self.page = page
        self.state = state
        self.db = db
        self.router = router
        self.step = 0
        self.total_steps = 7  # Reduced steps (remove image step)
        
    def build(self):
        def on_nav(index):
            pages = ["gallery", "home", "hpp_wizard", "crud_master", "setting"]
            self.router.navigate(pages[index])

        def next_step(_):
            if self.step < self.total_steps - 1:
                self.step += 1
                self._refresh_content()
            else:
                self._save_calculation()

        def prev_step(_):
            if self.step > 0:
                self.step -= 1
                self._refresh_content()

        # AppBar with step indicator
        step_indicator = ft.Container(
            content=ft.Row([
                ft.Text(f"Langkah {self.step + 1} dari {self.total_steps}", 
                       size=T.FONT_SM, color=T.TEXT_SECONDARY),
                ft.Container(expand=True),
                ft.ProgressRing(width=24, height=24, stroke_width=2, 
                              value=(self.step + 1) / self.total_steps, color=T.ACCENT),
            ], alignment="spaceBetween"),
            padding=ft.padding.all(T.SPACE_SM),
            bgcolor=T.BG_CARD,
        )

        # Step content - using ListView for scrollable content
        step_content = ft.ListView(ref=ft.Ref[ft.ListView](), spacing=T.SPACE_MD, expand=True)
        
        # Navigation buttons row
        nav_buttons = ft.Container(
            content=ft.Row([
                outline_button("Kembali", on_click=prev_step, icon=ft.Icons.ARROW_BACK) if self.step > 0 else ft.Container(),
                ft.Container(expand=True),
                primary_button("Lanjut" if self.step < self.total_steps - 1 else "Simpan Kalkulasi", 
                              on_click=next_step, 
                              icon=ft.Icons.ARROW_FORWARD if self.step < self.total_steps - 1 else ft.Icons.SAVE),
            ], spacing=T.SPACE_MD),
            padding=ft.padding.all(T.SPACE_LG),
        )
        
        content = ft.Column([
            batik_appbar("Calculator HPP Batik", subtitle="Hitung Harga Pokok Produksi", 
                        on_back=lambda _: self.router.navigate("home")),
            step_indicator,
            step_content,
            nav_buttons,
            ft.Container(height=80),
        ], spacing=0, expand=True)

        bottom_nav = BatikBottomNav(current_index=2, on_change=on_nav)

        self._step_content = step_content
        self._refresh_content()

        return ft.Container(
            content=ft.Stack([
                content,
                ft.Container(content=bottom_nav.build(), bottom=0, left=0, right=0),
            ]),
            bgcolor=T.BG_PRIMARY,
            expand=True,
        )

    def _refresh_content(self):
        if not self._step_content:
            return
        
        self._step_content.controls.clear()
        w = self.state.hpp_wizard
        
        if self.step == 0:
            self._step_content.controls.append(self._step_info_produk())
        elif self.step == 1:
            self._step_content.controls.append(self._step_bahan())
        elif self.step == 2:
            self._step_content.controls.append(self._step_pewarna_malam())
        elif self.step == 3:
            self._step_content.controls.append(self._step_alat_karyawan())
        elif self.step == 4:
            self._step_content.controls.append(self._step_overhead())
        elif self.step == 5:
            self._step_content.controls.append(self._step_biaya_tambahan())
        elif self.step == 6:
            self._step_content.controls.append(self._step_review())
        
        self.page.update()

    def _step_info_produk(self):
        w = self.state.hpp_wizard
        
        def update_produk(e):
            w["nama_produk"] = e.control.value
        
        def update_jenis(e):
            w["jenis_produk"] = e.control.value
        
        def update_deskripsi(e):
            w["deskripsi"] = e.control.value
        
        def update_kuantitas(e):
            try:
                w["kuantitas"] = int(e.control.value)
            except:
                w["kuantitas"] = 1
            self.state.hpp_wizard = self.state.hitung_hpp()
        
        return ft.Container(
            content=ft.Column([
                section_header("Informasi Produk", "Lengkapi detail produk (optional)"),
                ft.TextField(label="Nama Produk", value=w["nama_produk"], 
                            on_change=update_produk, bgcolor=T.BG_CARD),
                batik_dropdown("Jenis Produk", ["Kain Batik", "Kemeja Batik", "Selendang", "Sandal", "Aksesoris"],
                              value=w["jenis_produk"], on_change=update_jenis),
                ft.TextField(label="Deskripsi (optional)", value=w["deskripsi"], multiline=True, min_lines=2,
                            on_change=update_deskripsi, bgcolor=T.BG_CARD),
                ft.TextField(label="Kuantitas Produksi", value=str(w["kuantitas"]), 
                            keyboard_type="number", on_change=update_kuantitas, bgcolor=T.BG_CARD),
            ], spacing=T.SPACE_MD),
            padding=ft.padding.all(T.SPACE_MD),
        )

    def _step_bahan(self):
        w = self.state.hpp_wizard
        bahan_list = []
        for b in self.state.bahan:
            bahan_list.append(ft.Row([
                ft.Text(b.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(self.state.format_currency(float(b.get("Harga_Per_Satuan", 0))), size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=b: self._add_bahan(item)),
            ], spacing=8, vertical_alignment="center"))
        
        return ft.Container(
            content=ft.Column([
                section_header("Bahan Baku", "Pilih bahan yang digunakan"),
                ft.TextField(label="Cari Bahan", hint_text="Ketik nama bahan...", 
                            bgcolor=T.BG_CARD),
                ft.Column(bahan_list, spacing=T.SPACE_SM, height=300, scroll="auto"),
                ft.Divider(),
                ft.Text("Bahan Terpilih:", size=T.FONT_MD, weight="w600"),
                ft.Column([self._bahan_item(i) for i in w["bahan_list"]], spacing=T.SPACE_SM),
            ], spacing=T.SPACE_MD),
            padding=ft.padding.all(T.SPACE_MD),
        )

    def _step_pewarna_malam(self):
        w = self.state.hpp_wizard
        
        pewarna_list = []
        for p in self.state.pewarna:
            pewarna_list.append(ft.Row([
                ft.Text(p.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(self.state.format_currency(float(p.get("Harga_Per_Satuan", 0))), size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=p: self._add_pewarna(item)),
            ], spacing=8))
        
        malam_list = []
        for m in self.state.malam:
            malam_list.append(ft.Row([
                ft.Text(m.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(self.state.format_currency(float(m.get("Harga_Per_Satuan", 0))), size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=m: self._add_malam(item)),
            ], spacing=8))
        
        return ft.Container(
            content=ft.Column([
                section_header("Pewarna & Malam", "Pilih pewarna dan malam"),
                ft.Text("Pewarna:", size=T.FONT_MD, weight="w600"),
                ft.Column(pewarna_list, spacing=T.SPACE_SM, height=150, scroll="auto"),
                ft.Divider(),
                ft.Text("Malam:", size=T.FONT_MD, weight="w600"),
                ft.Column(malam_list, spacing=T.SPACE_SM, height=150, scroll="auto"),
                ft.Divider(),
                ft.Text("Pewarna Terpilih:", size=T.FONT_SM, weight="w600"),
                ft.Column([self._pewarna_item(i) for i in w["pewarna_list"]], spacing=T.SPACE_SM),
                ft.Text("Malam Terpilih:", size=T.FONT_SM, weight="w600"),
                ft.Column([self._malam_item(i) for i in w["malam_list"]], spacing=T.SPACE_SM),
            ], spacing=T.SPACE_MD),
            padding=ft.padding.all(T.SPACE_MD),
        )

    def _step_alat_karyawan(self):
        w = self.state.hpp_wizard
        
        alat_list = []
        for a in self.state.alat:
            alat_list.append(ft.Row([
                ft.Text(a.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(f"Rp {a.get('Biaya_Sewa_Per_Menit', 0)}/menit", size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=a: self._add_alat(item)),
            ], spacing=8))
        
        karyawan_list = []
        for k in self.state.karyawan:
            karyawan_list.append(ft.Row([
                ft.Text(k.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(f"Rp {k.get('Upah_Per_Jam', 0)}/jam", size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=k: self._add_karyawan(item)),
            ], spacing=8))
        
        return ft.Container(
            content=ft.Column([
                section_header("Alat & Karyawan", "Pilih alat dan karyawan"),
                ft.Text("Alat:", size=T.FONT_MD, weight="w600"),
                ft.Column(alat_list, spacing=T.SPACE_SM, height=200, scroll="auto"),
                ft.Divider(),
                ft.Text("Karyawan:", size=T.FONT_MD, weight="w600"),
                ft.Column(karyawan_list, spacing=T.SPACE_SM, height=200, scroll="auto"),
                ft.Divider(),
                ft.Text("Alat Terpilih:", size=T.FONT_SM, weight="w600"),
                ft.Column([self._alat_item(i) for i in w["alat_list"]], spacing=T.SPACE_SM),
                ft.Text("Karyawan Terpilih:", size=T.FONT_SM, weight="w600"),
                ft.Column([self._karyawan_item(i) for i in w["karyawan_list"]], spacing=T.SPACE_SM),
            ], spacing=T.SPACE_MD),
            padding=ft.padding.all(T.SPACE_MD),
        )

    def _step_overhead(self):
        w = self.state.hpp_wizard
        
        overhead_list = []
        for o in self.state.overhead:
            overhead_list.append(ft.Row([
                ft.Text(o.get("Nama", "-"), size=T.FONT_SM, expand=True),
                ft.Text(f"Rp {o.get('Biaya_Per_Satuan', 0)}/{o.get('Satuan', 'unit')}", size=T.FONT_SM),
                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=T.PRIMARY,
                            on_click=lambda _, item=o: self._add_overhead(item)),
            ], spacing=8))
        
        return ft.Container(
            content=ft.Column([
                section_header("Overhead", "Pilih biaya overhead"),
                ft.Column(overhead_list, spacing=T.SPACE_SM, height=300, scroll="auto"),
                ft.Divider(),
                ft.Text("Overhead Terpilih:", size=T.FONT_SM, weight="w600"),
                ft.Column([self._overhead_item(i) for i in w["overhead_list"]], spacing=T.SPACE_SM),
            ], spacing=T.SPACE_MD),
            padding=ft.padding.all(T.SPACE_MD),
        )

    def _step_biaya_tambahan(self):
        w = self.state.hpp_wizard
        
        def update_pengemasan(e):
            try:
                w["biaya_pengemasan"] = float(e.control.value)
            except:
                w["biaya_pengemasan"] = 0
            self.state.hpp_wizard = self.state.hitung_hpp()
        
        def update_pengiriman(e):
            try:
                w["biaya_pengiriman"] = float(e.control.value)
            except:
                w["biaya_pengiriman"] = 0
            self.state.hpp_wizard = self.state.hitung_hpp()
        
        def update_pajak(e):
            try:
                w["biaya_pajak"] = float(e.control.value)
            except:
                w["biaya_pajak"] = 0
            self.state.hpp_wizard = self.state.hitung_hpp()
        
        def update_lainnya(e):
            try:
                w["biaya_lainnya"] = float(e.control.value)
            except:
                w["biaya_lainnya"] = 0
            self.state.hpp_wizard = self.state.hitung_hpp()
        
        def update_margin(e):
            try:
                w["margin_persen"] = float(e.control.value)
            except:
                w["margin_persen"] = 30
            self.state.hpp_wizard = self.state.hitung_hpp()
        
        def update_diskon_persen(e):
            try:
                w["diskon_persen"] = float(e.control.value)
            except:
                w["diskon_persen"] = 0
            self.state.hpp_wizard = self.state.hitung_hpp()
        
        return ft.Container(
            content=ft.Column([
                section_header("Biaya Tambahan & Keuntungan", "Tambahkan biaya lain dan tentukan margin"),
                ft.TextField(label="Biaya Pengemasan (optional)", value=str(w.get("biaya_pengemasan", 0)),
                            keyboard_type="number", on_change=update_pengemasan, 
                            prefix="Rp", bgcolor=T.BG_CARD),
                ft.TextField(label="Biaya Pengiriman (optional)", value=str(w.get("biaya_pengiriman", 0)),
                            keyboard_type="number", on_change=update_pengiriman,
                            prefix="Rp", bgcolor=T.BG_CARD),
                ft.TextField(label="Pajak (optional)", value=str(w.get("biaya_pajak", 0)),
                            keyboard_type="number", on_change=update_pajak,
                            prefix="Rp", bgcolor=T.BG_CARD),
                ft.TextField(label="Biaya Lainnya (optional)", value=str(w.get("biaya_lainnya", 0)),
                            keyboard_type="number", on_change=update_lainnya,
                            prefix="Rp", bgcolor=T.BG_CARD),
                ft.Divider(),
                ft.TextField(label="Margin Keuntungan (%)", value=str(w.get("margin_persen", 30)),
                            keyboard_type="number", on_change=update_margin,
                            bgcolor=T.BG_CARD),
                ft.TextField(label="Diskon (%)", value=str(w.get("diskon_persen", 0)),
                            keyboard_type="number", on_change=update_diskon_persen,
                            bgcolor=T.BG_CARD),
            ], spacing=T.SPACE_MD),
            padding=ft.padding.all(T.SPACE_MD),
        )

    def _step_review(self):
        w = self.state.hpp_wizard
        self.state.hpp_wizard = self.state.hitung_hpp()
        
        return ft.Container(
            content=ft.Column([
                section_header("Review & Kalkulasi", "Detail perhitungan HPP"),
                ft.Container(
                    content=ft.Column([
                        cost_row("Total Bahan", self.state.format_currency(w.get("total_bahan", 0))),
                        cost_row("Total Pewarna", self.state.format_currency(w.get("total_pewarna", 0))),
                        cost_row("Total Malam", self.state.format_currency(w.get("total_malam", 0))),
                        cost_row("Total Sewa Alat", self.state.format_currency(w.get("total_alat", 0))),
                        cost_row("Total Upah", self.state.format_currency(w.get("total_upah", 0))),
                        cost_row("Total Overhead", self.state.format_currency(w.get("total_overhead", 0))),
                        cost_row("Biaya Tambahan", self.state.format_currency(w.get("total_biaya_tambahan", 0))),
                        ft.Divider(),
                        cost_row("Total Biaya Produksi", self.state.format_currency(w.get("total_biaya_produksi", 0)), bold=True),
                        cost_row("Kuantitas", str(w.get("kuantitas", 1))),
                        cost_row("HPP per Unit", self.state.format_currency(w.get("hpp_per_unit", 0)), T.PRIMARY, True),
                        cost_row("Margin", f"{w.get('margin_persen', 0)}%"),
                        cost_row("Harga Jual", self.state.format_currency(w.get("harga_jual", 0))),
                        cost_row("Diskon", f"{w.get('diskon_persen', 0)}%"),
                        cost_row("Harga Final", self.state.format_currency(w.get("harga_final", 0)), T.SUCCESS, True),
                        cost_row("Keuntungan per Unit", self.state.format_currency(w.get("keuntungan_akhir", 0)), T.ACCENT, True),
                        cost_row("Total Keuntungan", self.state.format_currency(w.get("keuntungan_nominal", 0)), T.ACCENT, True),
                        cost_row("ROI", f"{w.get('roi', 0):.1f}%", T.ACCENT, True),
                    ], spacing=T.SPACE_SM),
                    padding=ft.padding.symmetric(horizontal=T.SPACE_SM),
                ),
                ft.Container(height=T.SPACE_MD),
                ft.Text("💡 Hasil kalkulasi ini hanya untuk referensi. Untuk menyimpan produk, gunakan menu Master → Produk.",
                       size=T.FONT_XS, color=T.TEXT_HINT, italic=True, text_align="center"),
            ], spacing=T.SPACE_MD),
            padding=ft.padding.all(T.SPACE_MD),
        )

    # Add methods for adding items (same as before)
    def _add_bahan(self, item):
        w = self.state.hpp_wizard
        w["bahan_list"].append({
            "id": item.get("ID"),
            "nama": item.get("Nama"),
            "jumlah": 1,
            "satuan": item.get("Satuan", "pcs"),
            "harga": float(item.get("Harga_Per_Satuan", 0)),
            "subtotal": float(item.get("Harga_Per_Satuan", 0))
        })
        self._refresh_content()

    def _add_pewarna(self, item):
        w = self.state.hpp_wizard
        w["pewarna_list"].append({
            "id": item.get("ID"),
            "nama": item.get("Nama"),
            "jumlah": 1,
            "harga": float(item.get("Harga_Per_Satuan", 0)),
            "subtotal": float(item.get("Harga_Per_Satuan", 0))
        })
        self._refresh_content()

    def _add_malam(self, item):
        w = self.state.hpp_wizard
        w["malam_list"].append({
            "id": item.get("ID"),
            "nama": item.get("Nama"),
            "jumlah": 1,
            "harga": float(item.get("Harga_Per_Satuan", 0)),
            "subtotal": float(item.get("Harga_Per_Satuan", 0))
        })
        self._refresh_content()

    def _add_alat(self, item):
        w = self.state.hpp_wizard
        w["alat_list"].append({
            "id": item.get("ID"),
            "nama": item.get("Nama"),
            "durasi_menit": 60,
            "biaya_sewa": float(item.get("Biaya_Sewa_Per_Menit", 0)),
            "subtotal": float(item.get("Biaya_Sewa_Per_Menit", 0)) * 60
        })
        self._refresh_content()

    def _add_karyawan(self, item):
        w = self.state.hpp_wizard
        w["karyawan_list"].append({
            "id": item.get("ID"),
            "nama": item.get("Nama"),
            "durasi_menit": 60,
            "upah": float(item.get("Upah_Per_Jam", 0)),
            "subtotal": float(item.get("Upah_Per_Jam", 0))
        })
        self._refresh_content()

    def _add_overhead(self, item):
        w = self.state.hpp_wizard
        w["overhead_list"].append({
            "id": item.get("ID"),
            "nama": item.get("Nama"),
            "jumlah": 1,
            "biaya": float(item.get("Biaya_Per_Satuan", 0)),
            "subtotal": float(item.get("Biaya_Per_Satuan", 0))
        })
        self._refresh_content()

    def _bahan_item(self, item):
        def update_jumlah(e):
            try:
                jumlah = float(e.control.value)
                item["jumlah"] = jumlah
                item["subtotal"] = jumlah * item["harga"]
                self.state.hpp_wizard = self.state.hitung_hpp()
                self._refresh_content()
            except:
                pass
        
        def delete(_):
            self.state.hpp_wizard["bahan_list"].remove(item)
            self._refresh_content()
        
        return ft.Row([
            ft.Text(item["nama"], size=T.FONT_SM, expand=True),
            ft.TextField(value=str(item["jumlah"]), width=60, keyboard_type="number",
                        on_change=update_jumlah, text_align="center"),
            ft.Text(item["satuan"], size=T.FONT_XS),
            ft.Text(self.state.format_currency(item["subtotal"]), size=T.FONT_SM),
            ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, icon_color=T.ERROR, on_click=delete),
        ], spacing=8, vertical_alignment="center")

    def _pewarna_item(self, item):
        def update_jumlah(e):
            try:
                jumlah = float(e.control.value)
                item["jumlah"] = jumlah
                item["subtotal"] = jumlah * item["harga"]
                self.state.hpp_wizard = self.state.hitung_hpp()
                self._refresh_content()
            except:
                pass
        
        def delete(_):
            self.state.hpp_wizard["pewarna_list"].remove(item)
            self._refresh_content()
        
        return ft.Row([
            ft.Text(item["nama"], size=T.FONT_SM, expand=True),
            ft.TextField(value=str(item["jumlah"]), width=60, keyboard_type="number",
                        on_change=update_jumlah, text_align="center"),
            ft.Text("gram", size=T.FONT_XS),
            ft.Text(self.state.format_currency(item["subtotal"]), size=T.FONT_SM),
            ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, icon_color=T.ERROR, on_click=delete),
        ], spacing=8, vertical_alignment="center")

    def _malam_item(self, item):
        def update_jumlah(e):
            try:
                jumlah = float(e.control.value)
                item["jumlah"] = jumlah
                item["subtotal"] = jumlah * item["harga"]
                self.state.hpp_wizard = self.state.hitung_hpp()
                self._refresh_content()
            except:
                pass
        
        def delete(_):
            self.state.hpp_wizard["malam_list"].remove(item)
            self._refresh_content()
        
        return ft.Row([
            ft.Text(item["nama"], size=T.FONT_SM, expand=True),
            ft.TextField(value=str(item["jumlah"]), width=60, keyboard_type="number",
                        on_change=update_jumlah, text_align="center"),
            ft.Text("kg", size=T.FONT_XS),
            ft.Text(self.state.format_currency(item["subtotal"]), size=T.FONT_SM),
            ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, icon_color=T.ERROR, on_click=delete),
        ], spacing=8, vertical_alignment="center")

    def _alat_item(self, item):
        def update_durasi(e):
            try:
                durasi = float(e.control.value)
                item["durasi_menit"] = durasi
                item["subtotal"] = durasi * item["biaya_sewa"]
                self.state.hpp_wizard = self.state.hitung_hpp()
                self._refresh_content()
            except:
                pass
        
        def delete(_):
            self.state.hpp_wizard["alat_list"].remove(item)
            self._refresh_content()
        
        return ft.Row([
            ft.Text(item["nama"], size=T.FONT_SM, expand=True),
            ft.TextField(value=str(item["durasi_menit"]), width=60, keyboard_type="number",
                        on_change=update_durasi, text_align="center"),
            ft.Text("menit", size=T.FONT_XS),
            ft.Text(self.state.format_currency(item["subtotal"]), size=T.FONT_SM),
            ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, icon_color=T.ERROR, on_click=delete),
        ], spacing=8, vertical_alignment="center")

    def _karyawan_item(self, item):
        def update_durasi(e):
            try:
                durasi = float(e.control.value)
                item["durasi_menit"] = durasi
                item["subtotal"] = (durasi / 60) * item["upah"]
                self.state.hpp_wizard = self.state.hitung_hpp()
                self._refresh_content()
            except:
                pass
        
        def delete(_):
            self.state.hpp_wizard["karyawan_list"].remove(item)
            self._refresh_content()
        
        return ft.Row([
            ft.Text(item["nama"], size=T.FONT_SM, expand=True),
            ft.TextField(value=str(item["durasi_menit"]), width=60, keyboard_type="number",
                        on_change=update_durasi, text_align="center"),
            ft.Text("menit", size=T.FONT_XS),
            ft.Text(self.state.format_currency(item["subtotal"]), size=T.FONT_SM),
            ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, icon_color=T.ERROR, on_click=delete),
        ], spacing=8, vertical_alignment="center")

    def _overhead_item(self, item):
        def update_jumlah(e):
            try:
                jumlah = float(e.control.value)
                item["jumlah"] = jumlah
                item["subtotal"] = jumlah * item["biaya"]
                self.state.hpp_wizard = self.state.hitung_hpp()
                self._refresh_content()
            except:
                pass
        
        def delete(_):
            self.state.hpp_wizard["overhead_list"].remove(item)
            self._refresh_content()
        
        return ft.Row([
            ft.Text(item["nama"], size=T.FONT_SM, expand=True),
            ft.TextField(value=str(item["jumlah"]), width=60, keyboard_type="number",
                        on_change=update_jumlah, text_align="center"),
            ft.Text("unit", size=T.FONT_XS),
            ft.Text(self.state.format_currency(item["subtotal"]), size=T.FONT_SM),
            ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, icon_color=T.ERROR, on_click=delete),
        ], spacing=8, vertical_alignment="center")

    def _save_calculation(self):
        w = self.state.hpp_wizard
        w["tanggal"] = datetime.datetime.now().isoformat()
        self.state.hpp_list.append(w.copy())
        if self.db.is_configured():
            self.db.save_hpp(w)
        show_snack(self.page, "✅ Kalkulasi HPP berhasil disimpan!")
        self.state.reset_hpp_wizard()
        self.router.navigate("home")