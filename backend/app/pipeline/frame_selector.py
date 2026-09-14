# -*- coding: utf-8 -*-
"""
Frame Selector
Memilih frame terbaik per klaster materi (paling lengkap, tajam, utuh)
dan mengurutkannya secara ketat berdasarkan timestamp numerik asli.
"""

from typing import List, Dict, Any


def select_best_frames(clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Memilih frame terbaik dari setiap klaster visual materi:
    - Memilih versi dengan tulisan/diagram paling lengkap (edge_count tertinggi).
    - Memastikan frame tidak sedang dalam gerakan buram (lap_var memadai).
    - Menempatkan frame terpilih sesuai timestamp pertama kali topik dibahas.
    """
    selected = []

    for cl in clusters:
        frames = cl.get("frames", [])
        if not frames:
            continue

        # Evaluasi skor kelengkapan dan ketajaman setiap frame
        def frame_quality_score(fr: Dict[str, Any]) -> float:
            blur_factor = 0.4 if fr.get("is_blur", False) else 1.0
            # edge_count mengukur banyaknya tulisan/diagram pada papan
            # lap_var mengukur ketajaman garis/teks
            score = (fr["edge_count"] * blur_factor) + (fr["lap_var"] * 0.15)
            return score

        best_fr = max(frames, key=frame_quality_score)

        selected.append({
            "first_seen_ts": cl["first_seen_ts"],
            "best_ts": best_fr["timestamp"],
            "source_path": best_fr["path"],
            "edge_count": best_fr["edge_count"],
            "lap_var": best_fr["lap_var"],
            "cluster_size": len(frames)
        })

    # Urutkan secara mutlak berdasarkan timestamp kemunculan pertama (numerik asli)
    selected.sort(key=lambda x: x["first_seen_ts"])

    # Beri nomor urut indeks materi
    indexed_results = []
    for idx, item in enumerate(selected, 1):
        item["index"] = idx
        item["title"] = f"Materi {idx}"
        indexed_results.append(item)

    return indexed_results
