# -*- coding: utf-8 -*-
"""
Unit Tests untuk FastAPI Backend
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.pipeline.metadata import clean_video_title, calculate_adaptive_interval, format_timestamp

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data


def test_job_lifecycle():
    # 1. Buat job baru
    res = client.post("/jobs")
    assert res.status_code == 200
    data = res.json()
    assert "job_id" in data
    job_id = data["job_id"]

    # 2. Cek status awal
    res_status = client.get(f"/jobs/{job_id}/status")
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert status_data["status"] == "waiting_upload"
    assert status_data["progress"] == 0

    # 3. Hapus job
    res_del = client.delete(f"/jobs/{job_id}")
    assert res_del.status_code == 200
    assert res_del.json()["deleted"] is True


def test_youtube_validation():
    res = client.post("/jobs")
    job_id = res.json()["job_id"]

    # Tanpa persetujuan
    res_no_agree = client.post(
        f"/jobs/{job_id}/youtube",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "agreement": False}
    )
    assert res_no_agree.status_code == 400

    # URL tidak valid
    res_invalid_url = client.post(
        f"/jobs/{job_id}/youtube",
        json={"url": "https://random-website.com/video.mp4", "agreement": True}
    )
    assert res_invalid_url.status_code == 400

    # URL valid dan disetujui
    res_valid = client.post(
        f"/jobs/{job_id}/youtube",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "agreement": True}
    )
    assert res_valid.status_code == 200

    client.delete(f"/jobs/{job_id}")


def test_clean_video_title():
    raw_name = "BANK 101.BONGKAR TUNTAS !! RAHASIA DI BALIK JUAL BELI PIUTANG (CESSIE). Durasi 1 Jam. - Catatan AminW (CATATAN PETANI MASALAH) (240p, h264).mp4"
    cleaned = clean_video_title(raw_name)
    assert "240p" not in cleaned
    assert "h264" not in cleaned
    assert "!!" not in cleaned
    assert "BANK_101" in cleaned

    simple_name = "Tutorial Microsoft Excel Dasar.mp4"
    assert clean_video_title(simple_name) == "Tutorial_Microsoft_Excel_Dasar"


def test_adaptive_interval():
    # <= 10 menit
    assert calculate_adaptive_interval(300) == 2
    # 10 - 30 menit
    assert calculate_adaptive_interval(1200) == 3
    # 30 - 60 menit
    assert calculate_adaptive_interval(3400) == 5
    # > 60 menit
    assert calculate_adaptive_interval(4500) == 8


def test_format_timestamp():
    assert format_timestamp(45) == "00:45"
    assert format_timestamp(125) == "02:05"
    assert format_timestamp(3665) == "01:01:05"
