# -*- coding: utf-8 -*-
"""
FastAPI Main Application
Backend REST API untuk RidhoFajar Video to PDF Converter.
"""

import os
import re
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl

from .cleanup import cleanup_expired_jobs, delete_job_dir, get_job_dir
from .jobs import (
    init_job_status,
    get_job_status,
    save_job_status,
    update_job_progress,
    is_valid_youtube_url,
    run_conversion_pipeline
)

# Konfigurasi Environment
ALLOWED_ORIGINS_RAW = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://ridhofajar-convert-video-pdf.vercel.app,https://ridhofajar-video-to-pdf.vercel.app"
)
ALLOWED_ORIGINS = [orig.strip() for orig in ALLOWED_ORIGINS_RAW.split(",") if orig.strip()]
MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "500"))
MAX_VIDEO_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024
SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v"}

app = FastAPI(
    title="RidhoFajar Video to PDF API",
    description="Backend API untuk konversi materi visual video ke PDF",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateJobRequest(BaseModel):
    input_type: Optional[str] = "upload"


class YoutubeJobRequest(BaseModel):
    url: str
    agreement: bool


@app.get("/health")
def health_check():
    """Memeriksa kesiapan dan status backend."""
    return {
        "status": "ok",
        "service": "ridhofajar-video-to-pdf-backend",
        "max_video_size_mb": MAX_VIDEO_SIZE_MB,
        "max_concurrent_jobs": 1
    }


@app.post("/jobs")
def create_job(payload: Optional[CreateJobRequest] = None):
    """Membuat job baru dengan ID UUID acak."""
    cleanup_expired_jobs(6.0)
    job_id = str(uuid.uuid4())
    input_type = payload.input_type if payload else "upload"
    status_data = init_job_status(job_id, input_type=input_type)
    return status_data


@app.post("/jobs/{job_id}/upload")
async def upload_video(job_id: str, file: UploadFile = File(...)):
    """Menerima unggahan file video pengguna."""
    status_data = get_job_status(job_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="Job ID tidak ditemukan.")

    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Format file '{ext}' tidak didukung. Format yang diizinkan: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    jdir = get_job_dir(job_id)
    input_dir = jdir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    # Sanitasi nama file
    safe_name = re.sub(r'[^\w\.\-]', '_', file.filename)
    target_path = input_dir / safe_name

    # Baca stream dengan batasan ukuran
    total_bytes = 0
    chunk_size = 1024 * 1024  # 1MB
    with open(target_path, "wb") as buffer:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > MAX_VIDEO_BYTES:
                buffer.close()
                target_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"Ukuran video melebihi batas maksimal {MAX_VIDEO_SIZE_MB} MB."
                )
            buffer.write(chunk)

    update_job_progress(
        job_id,
        status="uploaded",
        progress=10,
        current_step="Video berhasil diunggah",
        message=f"File {file.filename} ({round(total_bytes / (1024*1024), 1)} MB) siap diproses.",
        video_title=file.filename
    )

    return {"job_id": job_id, "filename": safe_name, "size_bytes": total_bytes}


@app.post("/jobs/{job_id}/youtube")
def submit_youtube_url(job_id: str, payload: YoutubeJobRequest):
    """Menerima dan memvalidasi tautan URL video YouTube."""
    status_data = get_job_status(job_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="Job ID tidak ditemukan.")

    if not payload.agreement:
        raise HTTPException(
            status_code=400,
            detail="Anda harus menyetujui pernyataan izin kepemilikan atau hak penggunaan video."
        )

    if not is_valid_youtube_url(payload.url):
        raise HTTPException(
            status_code=400,
            detail="Format URL YouTube tidak valid. Contoh: https://www.youtube.com/watch?v=xxxxx"
        )

    status_data["youtube_url"] = payload.url.strip()
    status_data["input_type"] = "youtube"
    status_data["status"] = "downloading_video"
    status_data["progress"] = 5
    status_data["current_step"] = "Tautan YouTube diterima"
    status_data["message"] = "Tautan YouTube siap diproses."
    save_job_status(job_id, status_data)

    return {"job_id": job_id, "youtube_url": payload.url}


@app.post("/jobs/{job_id}/start")
def start_job_processing(job_id: str):
    """Memulai pemrosesan video di latar belakang."""
    status_data = get_job_status(job_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="Job ID tidak ditemukan.")

    if status_data["status"] in ["completed", "extracting_frames", "generating_pdf"]:
        return {"job_id": job_id, "status": status_data["status"], "message": "Proses sedang atau telah berjalan."}

    # Jalankan background pipeline task tanpa memblokir request HTTP
    asyncio.create_task(run_conversion_pipeline(job_id))
    return {"job_id": job_id, "status": "started", "message": "Pemrosesan dimulai di latar belakang."}


@app.get("/jobs/{job_id}/status")
def get_status(job_id: str):
    """Mengembalikan status progres terbaru job."""
    status_data = get_job_status(job_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="Job ID tidak ditemukan.")
    return status_data


@app.get("/jobs/{job_id}/preview")
def preview_pdf(job_id: str):
    """Menampilkan PDF langsung di peramban (inline preview)."""
    status_data = get_job_status(job_id)
    if not status_data or status_data.get("status") != "completed":
        raise HTTPException(status_code=400, detail="PDF belum selesai dibuat.")

    pdf_name = status_data.get("output_filename", "hasil.pdf")
    pdf_path = get_job_dir(job_id) / "output" / pdf_name
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="File PDF tidak ditemukan di server.")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{pdf_name}"'}
    )


@app.get("/jobs/{job_id}/download")
def download_pdf(job_id: str):
    """Mengunduh PDF sebagai berkas lampiran (attachment download)."""
    status_data = get_job_status(job_id)
    if not status_data or status_data.get("status") != "completed":
        raise HTTPException(status_code=400, detail="PDF belum selesai dibuat.")

    pdf_name = status_data.get("output_filename", "Materi_Video.pdf")
    pdf_path = get_job_dir(job_id) / "output" / pdf_name
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="File PDF tidak ditemukan di server.")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_name,
        headers={"Content-Disposition": f'attachment; filename="{pdf_name}"'}
    )


@app.delete("/jobs/{job_id}")
def cancel_or_delete_job(job_id: str):
    """Membatalkan atau menghapus direktori job."""
    status_data = get_job_status(job_id)
    if status_data and status_data["status"] not in ["completed", "failed"]:
        update_job_progress(
            job_id,
            status="cancelled",
            progress=0,
            current_step="Dibatalkan",
            message="Proses dibatalkan oleh pengguna."
        )

    deleted = delete_job_dir(job_id)
    return {"job_id": job_id, "deleted": deleted, "message": "Pekerjaan dan file sementara berhasil dihapus."}
