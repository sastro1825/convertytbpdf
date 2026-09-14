# -*- coding: utf-8 -*-
"""
PDF Validator
Memvalidasi integritas struktur file PDF menggunakan pypdf dan merender visual menggunakan PyMuPDF.
"""

from pathlib import Path
from typing import Dict, Any, List
import pypdf
import fitz  # PyMuPDF


def validate_and_render_pdf(
    pdf_path: Path,
    rendered_dir: Path,
    expected_pages: int
) -> Dict[str, Any]:
    """
    Memeriksa validitas PDF dengan pypdf dan merender setiap halaman dengan PyMuPDF.
    """
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise ValueError(f"File PDF tidak ditemukan atau kosong: {pdf_path}")

    # 1. Validasi struktur dengan pypdf
    reader = pypdf.PdfReader(str(pdf_path))
    actual_pages = len(reader.pages)
    if actual_pages != expected_pages:
        raise ValueError(f"Jumlah halaman PDF ({actual_pages}) tidak sesuai dengan yang diharapkan ({expected_pages})")

    # 2. Render visual dengan PyMuPDF (tanpa dependensi eksternal Poppler)
    rendered_dir.mkdir(parents=True, exist_ok=True)
    rendered_files: List[str] = []

    doc = fitz.open(str(pdf_path))
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=150)
        out_image = rendered_dir / f"page_{page_num + 1:03d}.png"
        pix.save(str(out_image))
        rendered_files.append(str(out_image))
    doc.close()

    return {
        "valid": True,
        "page_count": actual_pages,
        "file_size_bytes": pdf_path.stat().st_size,
        "rendered_pages": rendered_files
    }
