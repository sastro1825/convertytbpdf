# -*- coding: utf-8 -*-
"""
Frame Extractor
Mengekstrak frame dari video menggunakan FFmpeg dengan interval adaptif.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Tuple

from .metadata import get_ffmpeg_cmd


def extract_video_frames(
    video_path: Path,
    output_dir: Path,
    interval_sec: int,
    timeout_sec: int = 300
) -> List[Tuple[Path, float]]:
    """
    Mengekstrak frame video ke folder output_dir menggunakan interval tertentu.
    Mengembalikan daftar tuple (frame_path, timestamp_sec).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pattern = output_dir / "frame_%05d.jpg"

    # Bersihkan file frame lama jika ada
    for old_file in output_dir.glob("frame_*.jpg"):
        try:
            old_file.unlink()
        except OSError:
            pass

    ffmpeg_bin = get_ffmpeg_cmd()
    cmd = [
        ffmpeg_bin,
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", str(video_path),
        "-vf", f"fps=1/{interval_sec}",
        "-q:v", "2",
        str(pattern)
    ]

    try:
        subprocess.run(cmd, check=True, timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Ekstraksi frame melebihi batas waktu ({timeout_sec} detik).")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg gagal mengekstrak frame: {e}")

    frame_files = sorted(output_dir.glob("frame_*.jpg"))
    frames_with_ts = []
    for idx, fpath in enumerate(frame_files):
        ts = float(idx * interval_sec)
        frames_with_ts.append((fpath, ts))

    return frames_with_ts
