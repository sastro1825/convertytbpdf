# -*- coding: utf-8 -*-
"""
Frame Clustering
Mengelompokkan frame-frame materi serupa menggunakan pHash DCT dan Hamming Distance,
serta menggabungkan papan yang sama meskipun terjadi kamera zoom atau penulisan bertahap.
"""

from typing import List, Dict, Any
import numpy as np


def hamming_distance(h1: np.ndarray, h2: np.ndarray) -> int:
    """Menghitung jarak Hamming antara dua hash biner 64-bit."""
    return int(np.count_nonzero(h1 != h2))


def cluster_material_frames(
    analyzed_frames: List[Dict[str, Any]],
    phash_threshold: int = 12
) -> List[Dict[str, Any]]:
    """
    Mengelompokkan frame-frame visual ke dalam klaster materi.
    Setiap klaster menyimpan daftar frame, waktu kemunculan pertama,
    serta hash representatif.
    """
    if not analyzed_frames:
        return []

    clusters = []

    for item in analyzed_frames:
        cur_hash = item["phash"]
        matched_cluster = None
        min_dist = 999

        # Cari klaster yang cocok, dengan prioritas klaster yang paling baru/berdekatan
        for cl in reversed(clusters):
            dist = hamming_distance(cur_hash, cl["representative_phash"])
            if dist <= phash_threshold and dist < min_dist:
                min_dist = dist
                matched_cluster = cl
                break

        if matched_cluster is not None:
            matched_cluster["frames"].append(item)
            # Update representatif jika frame ini memiliki konten lebih lengkap
            if item["edge_count"] > matched_cluster["max_edge_count"]:
                matched_cluster["max_edge_count"] = item["edge_count"]
                matched_cluster["representative_phash"] = cur_hash
        else:
            new_cluster = {
                "cluster_id": len(clusters) + 1,
                "first_seen_ts": item["timestamp"],
                "representative_phash": cur_hash,
                "max_edge_count": item["edge_count"],
                "frames": [item]
            }
            clusters.append(new_cluster)

    # Penggabungan klaster sekunder untuk kamera zoom/geser pada papan yang sama:
    # Jika dua klaster berurutan memiliki kemiripan tata letak atau merupakan bagian dari topik yang sama,
    # dan klaster kedua hanya berlangsung singkat (< 15 detik), gabungkan ke klaster utama.
    merged_clusters = []
    for cl in clusters:
        if not merged_clusters:
            merged_clusters.append(cl)
            continue

        prev = merged_clusters[-1]
        dist = hamming_distance(cl["representative_phash"], prev["representative_phash"])

        # Jarak Hamming hingga 16 untuk variasi zoom ringan
        time_gap = cl["first_seen_ts"] - prev["frames"][-1]["timestamp"]
        if dist <= 16 and time_gap <= 25.0:
            prev["frames"].extend(cl["frames"])
            if cl["max_edge_count"] > prev["max_edge_count"]:
                prev["max_edge_count"] = cl["max_edge_count"]
                prev["representative_phash"] = cl["representative_phash"]
        else:
            merged_clusters.append(cl)

    return merged_clusters
