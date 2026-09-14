# -*- coding: utf-8 -*-
"""
Cleanup Manager
Mengelola penghapusan file sementara di backend (menghapus video setelah selesai, menghapus job > 6 jam).
"""

import os
import shutil
import time
from pathlib import Path

TEMP_ROOT = Path(__file__).resolve().parent.parent / "temp" / "jobs"


def get_job_dir(job_id: str) -> Path:
    """Mengambil path direktori job."""
    return TEMP_ROOT / job_id


def delete_job_dir(job_id: str) -> bool:
    """Menghapus seluruh folder job tertentu."""
    jdir = get_job_dir(job_id)
    if jdir.exists():
        try:
            shutil.rmtree(jdir)
            return True
        except Exception:
            return False
    return False


def remove_job_video_file(job_id: str):
    """Menghapus file video input setelah PDF selesai untuk menghemat penyimpanan."""
    input_dir = get_job_dir(job_id) / "input"
    if input_dir.exists():
        for f in input_dir.iterdir():
            if f.is_file():
                try:
                    f.unlink()
                except OSError:
                    pass


def cleanup_expired_jobs(retention_hours: float = 6.0):
    """
    Menghapus direktori job yang lebih tua dari retention_hours.
    Dipanggil secara berkala atau saat ada request baru.
    """
    if not TEMP_ROOT.exists():
        return

    now = time.time()
    cutoff_time = now - (retention_hours * 3600)

    for item in TEMP_ROOT.iterdir():
        if item.is_dir():
            try:
                # Periksa waktu modifikasi direktori
                mtime = item.stat().st_mtime
                if mtime < cutoff_time:
                    shutil.rmtree(item)
            except Exception:
                pass
