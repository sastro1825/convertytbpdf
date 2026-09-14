# -*- coding: utf-8 -*-
"""
Job Manager
Mengelola state file-based JSON status.json, antrian konkurensi (asyncio.Lock),
pemrosesan latar belakang, dan penanganan unduhan YouTube via yt-dlp.
"""

import asyncio
import json
import os
import re
import time
from pathlib import Path
from typing import Dict, Any, Optional
import yt_dlp

from .cleanup import get_job_dir, remove_job_video_file
from .pipeline.metadata import get_video_metadata, calculate_adaptive_interval, clean_video_title
from .pipeline.frame_extractor import extract_video_frames
from .pipeline.frame_filter import filter_valid_frames
from .pipeline.frame_cluster import cluster_material_frames
from .pipeline.frame_selector import select_best_frames
from .pipeline.enhancer import enhance_material_frames
from .pipeline.pdf_builder import build_material_pdf
from .pipeline.validator import validate_and_render_pdf

# Global Concurrency Lock (Maksimal 1 proses konversi video dalam satu waktu)
PROCESSING_LOCK = asyncio.Lock()


def get_status_file(job_id: str) -> Path:
    return get_job_dir(job_id) / "status.json"


def init_job_status(job_id: str, input_type: str = "upload") -> Dict[str, Any]:
    """Inisialisasi record status awal job."""
    jdir = get_job_dir(job_id)
    jdir.mkdir(parents=True, exist_ok=True)
    (jdir / "input").mkdir(exist_ok=True)
    (jdir / "frames").mkdir(exist_ok=True)
    (jdir / "selected_frames").mkdir(exist_ok=True)
    (jdir / "rendered_pdf").mkdir(exist_ok=True)
    (jdir / "output").mkdir(exist_ok=True)

    status_data = {
        "job_id": job_id,
        "status": "waiting_upload" if input_type == "upload" else "downloading_video",
        "progress": 0,
        "current_step": "Inisialisasi pekerjaan",
        "message": "Menunggu video disiapkan",
        "video_title": "",
        "output_filename": "",
        "page_count": 0,
        "file_size_bytes": 0,
        "input_type": input_type,
        "youtube_url": None,
        "error": None,
        "created_at": time.time(),
        "updated_at": time.time()
    }
    save_job_status(job_id, status_data)
    return status_data


def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Membaca status.json dari folder job."""
    sfile = get_status_file(job_id)
    if not sfile.exists():
        return None
    try:
        with open(sfile, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_job_status(job_id: str, data: Dict[str, Any]):
    """Menyimpan status ke status.json secara atomik."""
    sfile = get_status_file(job_id)
    sfile.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = time.time()
    temp_file = sfile.with_suffix(".tmp")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    temp_file.replace(sfile)


def update_job_progress(
    job_id: str,
    status: str,
    progress: int,
    current_step: str,
    message: str,
    error: str = None,
    **kwargs
):
    """Memperbarui kolom progres pada status.json."""
    data = get_job_status(job_id) or {"job_id": job_id}
    data["status"] = status
    data["progress"] = progress
    data["current_step"] = current_step
    data["message"] = message
    if error:
        data["error"] = error
    for k, v in kwargs.items():
        data[k] = v
    save_job_status(job_id, data)


def is_valid_youtube_url(url: str) -> bool:
    """Validasi format URL YouTube standar."""
    if not url:
        return False
    yt_regex = r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/|youtube\.com/embed/)[a-zA-Z0-9_\-]{6,15}'
    return bool(re.match(yt_regex, url.strip()))


def download_youtube_video(job_id: str, youtube_url: str, target_dir: Path) -> Path:
    """Mengunduh video YouTube sementara menggunakan yt-dlp."""
    target_dir.mkdir(parents=True, exist_ok=True)
    out_template = str(target_dir / "%(title).60s_%(id)s.%(ext)s")

    ydl_opts = {
        'format': 'best[height<=720]/bestvideo[height<=720]+bestaudio/best',
        'outtmpl': out_template,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'socket_timeout': 30,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            filename = ydl.prepare_filename(info)
            # Kadang ekstensi di-convert jadi mkv/mp4
            p = Path(filename)
            if p.exists():
                return p
            # Cari file yang baru dibuat di folder
            files = list(target_dir.glob("*.*"))
            if files:
                return files[0]
            raise RuntimeError("File hasil unduhan YouTube tidak ditemukan.")
    except Exception as e:
        raise RuntimeError(
            "Video tidak dapat diambil dari link. Silakan unduh secara legal lalu gunakan fitur Upload Video."
        )


async def run_conversion_pipeline(job_id: str):
    """
    Fungsi pemrosesan latar belakang (Background Task) dengan antrian konkurensi (Lock).
    """
    # Beri status 'waiting' jika sedang ada proses lain yang berjalan
    if PROCESSING_LOCK.locked():
        update_job_progress(
            job_id,
            status="waiting",
            progress=5,
            current_step="Menunggu antrean",
            message="Sedang menunggu konversi video lain selesai..."
        )

    async with PROCESSING_LOCK:
        try:
            status_data = get_job_status(job_id)
            if not status_data:
                return

            jdir = get_job_dir(job_id)
            input_dir = jdir / "input"
            frames_dir = jdir / "frames"
            selected_dir = jdir / "selected_frames"
            rendered_dir = jdir / "rendered_pdf"
            output_dir = jdir / "output"

            # 1. Dapatkan file video input (upload langsung atau YouTube)
            video_file = None
            if status_data.get("input_type") == "youtube":
                yt_url = status_data.get("youtube_url")
                update_job_progress(
                    job_id,
                    status="downloading_video",
                    progress=5,
                    current_step="Mengunduh video dari YouTube",
                    message="Mengambil video via yt-dlp..."
                )
                loop = asyncio.get_running_loop()
                video_file = await loop.run_in_executor(
                    None,
                    download_youtube_video,
                    job_id,
                    yt_url,
                    input_dir
                )
            else:
                # Cari file video di input_dir
                video_files = [f for f in input_dir.iterdir() if f.is_file() and not f.name.endswith(".tmp")]
                if not video_files:
                    raise FileNotFoundError("Tidak ada file video yang diunggah.")
                video_file = video_files[0]

            # 2. Membaca Metadata (10% - 15%)
            update_job_progress(
                job_id,
                status="reading_metadata",
                progress=12,
                current_step="Membaca metadata video",
                message=f"Membaca properti file: {video_file.name}",
                video_title=video_file.name
            )
            loop = asyncio.get_running_loop()
            meta = await loop.run_in_executor(None, get_video_metadata, video_file)
            cleaned_title = meta["cleaned_title"]
            interval = calculate_adaptive_interval(meta["duration_sec"])

            # 3. Mengekstrak Frame (15% - 50%)
            update_job_progress(
                job_id,
                status="extracting_frames",
                progress=25,
                current_step="Mengekstrak frame video",
                message=f"Mengambil frame setiap {interval} detik (durasi {meta['duration_str']})...",
                video_title=cleaned_title
            )
            frames = await loop.run_in_executor(
                None,
                extract_video_frames,
                video_file,
                frames_dir,
                interval
            )
            if not frames:
                raise RuntimeError("Tidak ada frame yang berhasil diekstrak dari video.")

            # 4. Menyaring Frame (50% - 65%)
            update_job_progress(
                job_id,
                status="filtering_frames",
                progress=55,
                current_step="Menyaring frame materi",
                message=f"Memeriksa {len(frames)} frame dari blur, intro/outro, dan layar kosong..."
            )
            valid_frames, dropped_cnt = await loop.run_in_executor(
                None,
                filter_valid_frames,
                frames,
                meta["duration_sec"]
            )
            if not valid_frames:
                raise RuntimeError("Tidak ditemukan materi visual yang memadai pada video ini.")

            # 5. Clustering Frame Serupa (65% - 78%)
            update_job_progress(
                job_id,
                status="clustering_frames",
                progress=70,
                current_step="Mengelompokkan materi serupa",
                message="Menganalisis pHash untuk menggabungkan slide/papan yang sama..."
            )
            clusters = await loop.run_in_executor(
                None,
                cluster_material_frames,
                valid_frames,
                12
            )

            # 6. Seleksi Frame Terbaik (78% - 88%)
            update_job_progress(
                job_id,
                status="selecting_frames",
                progress=82,
                current_step="Memilih frame paling lengkap",
                message=f"Memilih frame paling tajam dan lengkap dari {len(clusters)} kelompok materi..."
            )
            selected = await loop.run_in_executor(None, select_best_frames, clusters)
            if not selected:
                raise RuntimeError("Gagal memilih frame materi visual.")

            # 7. Image Enhancement
            enhanced = await loop.run_in_executor(
                None,
                enhance_material_frames,
                selected,
                selected_dir,
                1280
            )

            # 8. Menyusun PDF (88% - 96%)
            update_job_progress(
                job_id,
                status="generating_pdf",
                progress=90,
                current_step="Menyusun dokumen PDF",
                message=f"Membuat dokumen PDF A4 Lanskap ({len(enhanced)} halaman)..."
            )
            output_pdf_name = f"Materi_{cleaned_title}.pdf"
            output_pdf_path = output_dir / output_pdf_name
            await loop.run_in_executor(
                None,
                build_material_pdf,
                enhanced,
                output_pdf_path,
                cleaned_title
            )

            # 9. Validasi PDF (96% - 100%)
            update_job_progress(
                job_id,
                status="validating_pdf",
                progress=97,
                current_step="Memvalidasi dokumen PDF",
                message="Merender ulang seluruh halaman untuk verifikasi integritas visual..."
            )
            validation_res = await loop.run_in_executor(
                None,
                validate_and_render_pdf,
                output_pdf_path,
                rendered_dir,
                len(enhanced)
            )

            # 10. Selesai (Completed)
            # Hapus file video input untuk menghemat kapasitas disk
            remove_job_video_file(job_id)

            pdf_size = output_pdf_path.stat().st_size
            update_job_progress(
                job_id,
                status="completed",
                progress=100,
                current_step="Selesai",
                message="Dokumen PDF berhasil dibuat dan siap diunduh.",
                video_title=cleaned_title,
                output_filename=output_pdf_name,
                page_count=validation_res["page_count"],
                file_size_bytes=pdf_size
            )

        except Exception as err:
            err_msg = str(err)
            update_job_progress(
                job_id,
                status="failed",
                progress=0,
                current_step="Terjadi kesalahan",
                message=err_msg,
                error=err_msg
            )
