"""
LaporanPage – Halaman Laporan & Cetak PDF
- Tabel semua produk
- Rekap HPP
- Export PDF (menggunakan reportlab jika tersedia, fallback ke HTML)
"""

import flet as ft
from core.theme import BatikTheme as T
from components.widgets import batik_appbar, BatikBottomNav, hpp_summary_card, show_snack, stat_card

class LaporanPage:
    def __init__(self, page, state, db, router, **kwargs):
        self.page = page
        self.state = state
        self.db = db
        self.router = router
        self._tab_index = 0

    def build(self):
        def on_nav(index):
            pages = ["home", "gallery", "hpp_wizard", "crud_master", "setting"]
            self.router.navigate(pages[index])

        def on_tab(e):
            self._tab_index = e.control.selected_index
            self.page.update()

        # Stats overview
        produk = self.state.produk
        hpp_list = self.state.hpp_list
        fc = self.state.format_currency

        total_produk = len(produk)
        total_hpp = len(hpp_list)
        avg_margin = 0
        total_nilai = 0
        if hpp_list:
            margins = []
            for h in hpp_list:
                try: margins.append(float(h.get("Margin_Persen",0)))
                except: pass
                try: total_nilai += float(h.get("Harga_Final", 0))
                except: pass
            if margins: avg_margin = sum(margins) / len(margins)

        stats = ft.Container(
            content=ft.Column([
                ft.Row([
                    stat_card("Total Produk", str(total_produk), ft.Icons.INVENTORY_2_ROUNDED, T.PRIMARY),
                    ft.Container(width=8),
                    stat_card("Kalkulasi HPP", str(total_hpp), ft.Icons.CALCULATE_ROUNDED, T.SECONDARY),
                ]),
                ft.Row([
                    stat_card("Avg Margin", f"{avg_margin:.1f}%", ft.Icons.TRENDING_UP_ROUNDED, T.SUCCESS),
                    ft.Container(width=8),
                    stat_card("Total Nilai Jual", fc(total_nilai), ft.Icons.ATTACH_MONEY_ROUNDED, T.ACCENT),
                ]),
            ], spacing=8, tight=True),
            padding=ft.padding.symmetric(0, T.SPACE_LG),
        )

        # Tab content
        tab_produk = self._build_tab_produk()
        tab_hpp = self._build_tab_hpp()

        tabs = ft.Tabs(content=[
                ft.Tab(label="Semua Produk", content=tab_produk),
                ft.Tab(label="Kalkulasi HPP", content=tab_hpp),
            ],
            selected_index=self._tab_index,
            on_change=on_tab,
            expand=True,
        )

        content = ft.Column([
            batik_appbar(
                "Laporan & Cetak",
                on_back=lambda _: self.router.navigate("home"),
                subtitle="Rekap produk & HPP",
                actions=[
                    ft.IconButton(
                        icon=ft.Icons.PICTURE_AS_PDF_ROUNDED,
                        icon_color=T.TEXT_WHITE, icon_size=22,
                        on_click=self._export_pdf,
                    )
                ],
            ),
            stats,
            ft.Container(content=tabs, expand=True, padding=0),
            ft.Container(height=80),
        ], spacing=T.SPACE_SM, expand=True)

        bottom_nav = BatikBottomNav(current_index=3, on_change=on_nav)

        return ft.Container(
            content=ft.Stack([
                content,
                ft.Container(content=bottom_nav.build(), bottom=0, left=0, right=0),
            ]),
            bgcolor=T.BG_PRIMARY, expand=True,
        )

    def _build_tab_produk(self) -> ft.Control:
        produk = self.state.produk
        fc = self.state.format_currency

        if not produk:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX_ROUNDED, size=50, color=T.TEXT_HINT),
                    ft.Text("Belum ada produk", size=T.FONT_SM, color=T.TEXT_HINT),
                ], horizontal_alignment="center", spacing=8),
                alignment=ft.Alignment(0, 0), padding=60,
            )

        # Table header
        def header_cell(text, expand=1):
            return ft.Container(
                content=ft.Text(text, size=T.FONT_XS, weight="w700", color=T.TEXT_WHITE),
                expand=expand, padding=ft.padding.symmetric(6, 8),
            )

        header = ft.Container(
            content=ft.Row([
                header_cell("ID", 1),
                header_cell("Nama Produk", 3),
                header_cell("Jenis", 2),
                header_cell("Harga Jual", 2),
                header_cell("Stok", 1),
            ], spacing=0),
            bgcolor=T.PRIMARY,
            border_radius=ft.BorderRadius(T.RADIUS_SM, T.RADIUS_SM, 0, 0),
        )

        def row_cell(text, expand=1, bold=False):
            return ft.Container(
                content=ft.Text(text, size=T.FONT_XS, color=T.TEXT_PRIMARY if bold else T.TEXT_SECONDARY,
                                 weight="w600" if bold else "w400",
                                 overflow="ellipsis", max_lines=2),
                expand=expand, padding=ft.padding.symmetric(6, 8),
            )

        rows = []
        for i, p in enumerate(produk):
            try: harga = float(p.get("Harga_Jual", 0))
            except: harga = 0
            bg = T.BG_CARD if i % 2 == 0 else T.BG_SECONDARY
            rows.append(ft.Container(
                content=ft.Row([
                    row_cell(p.get("ID","")[-4:], 1),
                    row_cell(p.get("Nama","-"), 3, True),
                    row_cell(p.get("Jenis_Produk","-"), 2),
                    row_cell(fc(harga), 2),
                    row_cell(str(p.get("Stok","-")), 1),
                ], spacing=0),
                bgcolor=bg,
                border=ft.border.only(bottom=ft.BorderSide(0.5, T.DIVIDER)),
            ))

        table = ft.Container(
            content=ft.Column([header, *rows], spacing=0, tight=True),
            border=ft.border.all(1, T.DIVIDER),
            clip_behavior="hardEdge",
        )

        return ft.Container(
            content=ft.ListView([table, ft.Container(height=20)], spacing=0),
            padding=ft.padding.symmetric(0, T.SPACE_LG),
            expand=True,
        )

    def _build_tab_hpp(self) -> ft.Control:
        hpp_list = self.state.hpp_list
        fc = self.state.format_currency

        if not hpp_list:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CALCULATE_OUTLINED, size=50, color=T.TEXT_HINT),
                    ft.Text("Belum ada kalkulasi HPP", size=T.FONT_SM, color=T.TEXT_HINT),
                    ft.Container(
                        content=ft.Row([ft.Icon(ft.Icons.ADD_ROUNDED, size=14, color="white"), ft.Text("Hitung HPP Sekarang", color="white", weight="w600", size=12)], spacing=4, tight=True),
                        bgcolor=T.PRIMARY,
                        padding=ft.padding.symmetric(8, 14),
                        on_click=lambda _: self.router.navigate("hpp_wizard"), ink=True,
                    ),
                ], horizontal_alignment="center", spacing=12),
                alignment=ft.Alignment(0, 0), padding=60,
            )

        cards = [hpp_summary_card(h, fc) for h in reversed(hpp_list)]

        return ft.Container(
            content=ft.ListView(cards + [ft.Container(height=20)], spacing=T.SPACE_MD),
            padding=ft.padding.symmetric(0, T.SPACE_LG),
            expand=True,
        )

    def _export_pdf(self, _=None):
        """Generate PDF laporan produk"""
        try:
            self._generate_pdf()
            show_snack(self.page, "✅ PDF berhasil diekspor ke folder Download!")
        except Exception as e:
            show_snack(self.page, f"⚠️ Gagal export PDF: {str(e)[:60]}", T.WARNING)

    def _generate_pdf(self):
        """Generate PDF menggunakan reportlab"""
        import os
        from datetime import datetime

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

            produk = self.state.produk
            hpp_list = self.state.hpp_list
            s = self.state.setting
            fc = self.state.format_currency

            # Output path
            download_dir = os.path.expanduser("~/Downloads")
            os.makedirs(download_dir, exist_ok=True)
            filename = os.path.join(download_dir, f"BatikPro_Laporan_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf")

            doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm,
                                    leftMargin=1.5*cm, rightMargin=1.5*cm)
            styles = getSampleStyleSheet()
            primary_color = colors.HexColor("#7B3F00")
            accent_color = colors.HexColor("#C9A84C")
            elements = []

            # Header
            title_style = ParagraphStyle("title", parent=styles["Title"],
                                          textColor=primary_color, fontSize=20, spaceAfter=4)
            sub_style = ParagraphStyle("sub", parent=styles["Normal"],
                                        textColor=colors.grey, fontSize=10, spaceAfter=12)
            elements.append(Paragraph(s.nama_toko, title_style))
            elements.append(Paragraph(s.deskripsi, sub_style))
            elements.append(Paragraph(f"Laporan dibuat: {datetime.now().strftime('%d %B %Y %H:%M')}", sub_style))
            elements.append(Spacer(1, 0.3*cm))

            # Tabel Produk
            elements.append(Paragraph("Daftar Produk", ParagraphStyle("h2", parent=styles["Heading2"],
                                                                         textColor=primary_color, fontSize=13)))
            elements.append(Spacer(1, 0.2*cm))

            prod_data = [["No", "ID", "Nama Produk", "Jenis", "Harga Jual", "Stok", "Status"]]
            for i, p in enumerate(produk):
                try: harga = float(p.get("Harga_Jual", 0))
                except: harga = 0
                prod_data.append([
                    str(i+1),
                    p.get("ID","")[-6:],
                    p.get("Nama","-")[:40],
                    p.get("Jenis_Produk","-")[:15],
                    fc(harga),
                    str(p.get("Stok","-")),
                    p.get("Status","-"),
                ])

            col_widths = [1*cm, 1.5*cm, 5*cm, 3*cm, 3*cm, 1.5*cm, 2*cm]
            prod_table = Table(prod_data, colWidths=col_widths, repeatRows=1)
            prod_table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), primary_color),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,0), 9),
                ("FONTSIZE", (0,1), (-1,-1), 8),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FDF8F2")]),
                ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E8DDD0")),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ]))
            elements.append(prod_table)
            elements.append(Spacer(1, 0.5*cm))

            # Tabel HPP
            if hpp_list:
                elements.append(Paragraph("Rekap Kalkulasi HPP", ParagraphStyle("h2", parent=styles["Heading2"],
                                                                                   textColor=primary_color, fontSize=13)))
                elements.append(Spacer(1, 0.2*cm))
                hpp_data = [["ID HPP", "Nama Produk", "Tanggal", "HPP/unit", "Margin", "Harga Jual", "Harga Final"]]
                for h in hpp_list:
                    try: hpp_v = float(h.get("HPP_Per_Unit",0))
                    except: hpp_v = 0
                    try: hj = float(h.get("Harga_Jual",0))
                    except: hj = 0
                    try: hf = float(h.get("Harga_Final",0))
                    except: hf = 0
                    hpp_data.append([
                        h.get("ID","")[-6:],
                        h.get("Nama_Produk","-")[:25],
                        h.get("Tanggal","")[:10],
                        fc(hpp_v),
                        f"{h.get('Margin_Persen','0')}%",
                        fc(hj),
                        fc(hf),
                    ])
                hpp_col_w = [1.5*cm, 4*cm, 2.5*cm, 2.5*cm, 1.5*cm, 2.5*cm, 2.5*cm]
                hpp_tbl = Table(hpp_data, colWidths=hpp_col_w, repeatRows=1)
                hpp_tbl.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1B4F72")),
                    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                    ("FONTSIZE", (0,0), (-1,0), 9),
                    ("FONTSIZE", (0,1), (-1,-1), 8),
                    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F5EDE0")]),
                    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E8DDD0")),
                    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                    ("TOPPADDING", (0,0), (-1,-1), 4),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ]))
                elements.append(hpp_tbl)

            # Footer
            elements.append(Spacer(1, 0.5*cm))
            elements.append(Paragraph(s.footer_text, ParagraphStyle("footer", parent=styles["Normal"],
                                                                      textColor=colors.grey, fontSize=8,
                                                                      alignment=1)))

            doc.build(elements)

        except ImportError:
            # Fallback: simpan sebagai HTML
            self._generate_html_fallback()

    def _generate_html_fallback(self):
        import os
        from datetime import datetime
        s = self.state.setting
        produk = self.state.produk
        fc = self.state.format_currency

        rows = ""
        for i, p in enumerate(produk):
            try: harga = float(p.get("Harga_Jual",0))
            except: harga = 0
            bg = "#ffffff" if i % 2 == 0 else "#fdf8f2"
            rows += f"""<tr style="background:{bg}">
                <td>{i+1}</td><td>{p.get('ID','')}</td>
                <td>{p.get('Nama','-')}</td><td>{p.get('Jenis_Produk','-')}</td>
                <td>{fc(harga)}</td><td>{p.get('Stok','-')}</td>
            </tr>"""

        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
        <title>Laporan {s.nama_toko}</title>
        <style>body{{font-family:Arial;margin:20px}}
        table{{width:100%;border-collapse:collapse}}
        th{{background:#7B3F00;color:white;padding:8px}}
        td{{padding:6px;border:1px solid #eee}}</style></head>
        <body><h1>{s.nama_toko}</h1><p>{s.deskripsi}</p>
        <p>Dicetak: {datetime.now().strftime('%d %B %Y %H:%M')}</p>
        <h2>Daftar Produk</h2>
        <table><tr><th>No</th><th>ID</th><th>Nama</th><th>Jenis</th><th>Harga</th><th>Stok</th></tr>
        {rows}</table>
        <p style="text-align:center;color:gray">{s.footer_text}</p></body></html>"""

        download_dir = os.path.expanduser("~/Downloads")
        os.makedirs(download_dir, exist_ok=True)
        fp = os.path.join(download_dir, f"BatikPro_Laporan_{datetime.now().strftime('%Y%m%d_%H%M')}.html")
        with open(fp, "w", encoding="utf-8") as f:
            f.write(html)
