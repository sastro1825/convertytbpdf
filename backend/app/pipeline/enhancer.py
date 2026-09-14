# -*- coding: utf-8 -*-
"""
Image Enhancer
Meningkatkan kualitas visual frame terpilih secara proporsional dengan Lanczos,
sedikit penajaman kontras, dan ketajaman tanpa mengubah isi teks/angka asli.
"""

from pathlib import Path
from typing import List, Dict, Any
from PIL import Image, ImageEnhance

from .metadata import format_timestamp


def enhance_material_frames(
    selected_items: List[Dict[str, Any]],
    output_dir: Path,
    target_width: int = 1280,
    contrast_factor: float = 1.08,
    sharpness_factor: float = 1.30
) -> List[Dict[str, Any]]:
    """
    Melakukan resize proporsional Lanczos dan peningkatan keterbacaan ringan
    untuk setiap frame yang telah terpilih.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    enhanced_results = []

    for item in selected_items:
        idx = item["index"]
        src_path = item["source_path"]
        out_path = output_dir / f"enhanced_{idx:03d}.jpg"

        with Image.open(src_path).convert("RGB") as img:
            w, h = img.size
            target_height = round(target_width * h / w)

            # Resize proporsional dengan Lanczos (menjaga rasio asli 100%)
            resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

            # Penyesuaian kontras & ketajaman ringan
            enhanced = ImageEnhance.Contrast(resized).enhance(contrast_factor)
            enhanced = ImageEnhance.Sharpness(enhanced).enhance(sharpness_factor)

            enhanced.save(out_path, quality=95, subsampling=0)

        enhanced_results.append({
            "index": idx,
            "title": item["title"],
            "first_seen_ts": item["first_seen_ts"],
            "best_ts": item["best_ts"],
            "timestamp_str": format_timestamp(item["first_seen_ts"]),
            "enhanced_path": out_path,
            "source_filename": Path(src_path).name,
            "edge_count": item.get("edge_count", 0),
            "lap_var": item.get("lap_var", 0)
        })

    return enhanced_results
