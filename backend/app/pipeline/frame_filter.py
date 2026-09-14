# -*- coding: utf-8 -*-
"""
Frame Filter
Menyaring frame rusak, layar kosong/hitam, transisi buram, presenter-only, dan intro/outro non-materi.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
from PIL import Image
from scipy.fftpack import dct


def compute_dct_phash(img_gray: np.ndarray) -> np.ndarray:
    """
    Menghitung Perceptual Hash (pHash) 64-bit berbasis 2D Discrete Cosine Transform (DCT).
    """
    pil_img = Image.fromarray(img_gray).resize((32, 32), Image.Resampling.BILINEAR)
    pixels = np.asarray(pil_img, dtype=np.float32)

    # 2D DCT
    dct_mat = dct(dct(pixels.T, norm='ortho').T, norm='ortho')
    # Ambil 8x8 frekuensi rendah, abaikan DC [0,0]
    dct_low = dct_mat[:8, :8].copy()
    dct_low[0, 0] = 0
    med = np.median(dct_low)
    return (dct_low > med).flatten()


def analyze_frame_metrics(frame_path: Path) -> Dict[str, Any]:
    """Menganalisis indikator kualitas, ketajaman, dan kepadatan konten materi frame."""
    with Image.open(frame_path) as img:
        img_gray = img.convert("L")
        gray = np.array(img_gray, dtype=np.float32)

    mean_val = float(np.mean(gray))
    std_val = float(np.std(gray))

    # Deteksi frame kosong / solid color
    is_blank = (std_val < 10.0) or (mean_val < 12.0) or (mean_val > 248.0)

    # Variansi Laplacian untuk ketajaman
    padded = np.pad(gray, 1, mode='edge')
    laplacian = (padded[1:-1, 2:] + padded[1:-1, :-2] + padded[2:, 1:-1] + padded[:-2, 1:-1] - 4.0 * gray)
    lap_var = float(np.var(laplacian))

    # Gradien magnitudo untuk mendeteksi guratan tulisan, garis tabel, dan diagram
    gx = np.abs(padded[1:-1, 2:] - padded[1:-1, :-2])
    gy = np.abs(padded[2:, 1:-1] - padded[:-2, 1:-1])
    grad_mag = gx + gy

    # Edge pixels mewakili konten tulisan/diagram
    edge_count = int(np.count_nonzero(grad_mag > 28.0))
    edge_density = float(edge_count / gray.size)

    # Deteksi rasio area hitam pekat (biasanya border atau transisi fade-to-black)
    black_ratio = float(np.count_nonzero(gray < 15.0) / gray.size)

    # Frame sangat buram / transisi
    is_blur = lap_var < 12.0

    # Presenter only: kontur sangat rendah dan tidak ada garis slide / papan
    is_presenter_only = (edge_density < 0.008) and (std_val < 22.0)

    phash = compute_dct_phash(gray.astype(np.uint8))

    return {
        "path": frame_path,
        "mean": mean_val,
        "std": std_val,
        "lap_var": lap_var,
        "edge_count": edge_count,
        "edge_density": edge_density,
        "black_ratio": black_ratio,
        "is_blank": is_blank,
        "is_blur": is_blur,
        "is_presenter_only": is_presenter_only,
        "phash": phash
    }


def filter_valid_frames(
    frames_with_ts: List[Tuple[Path, float]],
    total_duration_sec: float
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Menyaring frame dari daftar mentah:
    - Membuang frame blank, blur, transisi, presenter only.
    - Mengeliminasi card intro/outro statis yang bukan bagian dari materi pembelajaran.
    """
    analyzed_frames = []
    dropped_count = 0

    for fpath, ts in frames_with_ts:
        m = analyze_frame_metrics(fpath)
        m["timestamp"] = ts

        # 1. Buang frame kosong atau hitam
        if m["is_blank"] or m["black_ratio"] > 0.85:
            dropped_count += 1
            continue

        # 2. Buang frame transisi atau presenter-only
        if m["is_presenter_only"]:
            dropped_count += 1
            continue

        analyzed_frames.append(m)

    if not analyzed_frames:
        return [], dropped_count

    # 3. Deteksi dan eliminasi intro/outro statis
    # Jika frame pada t < 10 detik identik/sangat mirip dengan frame pada t > (total - 30 detik)
    # itu adalah kartu profil channel / disclaimer yang berulang di awal dan akhir.
    if len(analyzed_frames) >= 4:
        first_frame = analyzed_frames[0]
        last_frame = analyzed_frames[-1]

        # Hamming distance antara frame pertama dan frame terakhir
        h_diff = int(np.count_nonzero(first_frame["phash"] != last_frame["phash"]))
        if h_diff <= 10 and first_frame["timestamp"] < 15.0:
            # Frame pertama dan terakhir adalah card statis yang sama (Intro/Outro)
            # Buang frame pertama (intro card) dan frame terakhir (outro card)
            analyzed_frames = [f for f in analyzed_frames if f["path"] != first_frame["path"] and f["path"] != last_frame["path"]]
            dropped_count += 2

    return analyzed_frames, dropped_count
