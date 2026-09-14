# -*- coding: utf-8 -*-
"""
PDF Builder
Menyusun dokumen PDF A4 Lanskap menggunakan ReportLab dengan gambar utuh di tengah (contain),
header judul & timestamp, footer penomoran halaman, dan metadata dokumen lengkap.
"""

from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def build_material_pdf(
    image_items: List[Dict[str, Any]],
    output_pdf_path: Path,
    video_title: str
) -> Path:
    """
    Menyusun seluruh gambar materi terpilih menjadi satu dokumen PDF A4 Lanskap.
    """
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_pdf_path), pagesize=landscape(A4))
    page_w, page_h = landscape(A4)

    # Set Metadata Dokumen PDF
    c.setTitle(video_title)
    c.setAuthor("Ridho Fajar")
    c.setSubject("Materi hasil ekstraksi video")
    c.setCreator("RidhoFajar Video to PDF")

    total_pages = len(image_items)

    for idx, item in enumerate(image_items, 1):
        # 1. Background bersih
        c.setFillColor(colors.HexColor("#ffffff"))
        c.rect(0, 0, page_w, page_h, fill=True, stroke=False)

        # 2. Header
        header_y = page_h - 40
        c.setFillColor(colors.HexColor("#0f172a"))  # Deep slate/blue
        c.setFont("Helvetica-Bold", 14)
        c.drawString(36, header_y, f"{item['title']}")

        c.setFillColor(colors.HexColor("#475569"))
        c.setFont("Helvetica", 10)
        c.drawString(page_w - 210, header_y, f"Timestamp Video: {item['timestamp_str']}")

        # Garis pemisah header
        c.setStrokeColor(colors.HexColor("#e2e8f0"))
        c.setLineWidth(1)
        c.line(36, header_y - 8, page_w - 36, header_y - 8)

        # 3. Area Gambar Screenshot Utama (Contain & Preserved Aspect Ratio)
        img_path = str(item["enhanced_path"])
        with Image.open(img_path) as im:
            orig_w, orig_h = im.size

        margin_x = 36
        max_img_w = page_w - (margin_x * 2)
        max_img_h = header_y - 8 - 45  # Sisakan ruang untuk footer

        scale = min(max_img_w / orig_w, max_img_h / orig_h)
        draw_w = orig_w * scale
        draw_h = orig_h * scale

        # Posisi gambar persis di tengah area konten
        draw_x = margin_x + (max_img_w - draw_w) / 2
        draw_y = 38 + (max_img_h - draw_h) / 2

        # Kotak bingkai tipis elegan di sekeliling gambar
        c.setStrokeColor(colors.HexColor("#cbd5e1"))
        c.setLineWidth(0.5)
        c.rect(draw_x - 1, draw_y - 1, draw_w + 2, draw_h + 2, fill=False, stroke=True)

        # Gambar utuh tanpa crop buatan
        c.drawImage(img_path, draw_x, draw_y, width=draw_w, height=draw_h, preserveAspectRatio=True)

        # 4. Footer
        footer_line_y = 32
        c.setStrokeColor(colors.HexColor("#e2e8f0"))
        c.line(36, footer_line_y, page_w - 36, footer_line_y)

        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica", 8)
        clean_name = video_title[:65] + ("..." if len(video_title) > 65 else "")
        c.drawString(36, 18, f"Sumber Video: {clean_name}")

        c.setFillColor(colors.HexColor("#64748b"))
        c.setFont("Helvetica", 9)
        c.drawRightString(page_w - 36, 18, f"Halaman {idx} dari {total_pages}")

        c.showPage()

    c.save()
    return output_pdf_path
