# -*- coding: utf-8 -*-
"""
Integration Tests untuk Video to PDF Conversion Pipeline
"""

import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.jobs import run_conversion_pipeline, get_job_status

client = TestClient(app)


import asyncio

def test_full_conversion_pipeline_integration():
    test_video_path = Path("test_short.mp4")
    if not test_video_path.exists():
        pytest.skip("File test_short.mp4 tidak ditemukan")

    # 1. Buat job baru
    res_job = client.post("/jobs", json={"input_type": "upload"})
    assert res_job.status_code == 200
    job_id = res_job.json()["job_id"]

    # 2. Upload video
    with open(test_video_path, "rb") as vf:
        res_upload = client.post(
            f"/jobs/{job_id}/upload",
            files={"file": ("test_video.mp4", vf, "video/mp4")}
        )
    assert res_upload.status_code == 200
    assert res_upload.json()["filename"] == "test_video.mp4"

    # 3. Jalankan pipeline langsung
    asyncio.run(run_conversion_pipeline(job_id))

    # 4. Verifikasi status completed
    status_data = get_job_status(job_id)
    assert status_data is not None
    assert status_data["status"] == "completed"
    assert status_data["page_count"] >= 1
    assert status_data["file_size_bytes"] > 0

    # 5. Uji preview endpoint
    res_preview = client.get(f"/jobs/{job_id}/preview")
    assert res_preview.status_code == 200
    assert res_preview.headers["content-type"] == "application/pdf"
    assert "inline" in res_preview.headers["content-disposition"]

    # 6. Uji download endpoint
    res_download = client.get(f"/jobs/{job_id}/download")
    assert res_download.status_code == 200
    assert res_download.headers["content-type"] == "application/pdf"
    assert "attachment" in res_download.headers["content-disposition"]

    # 7. Bersihkan job
    res_del = client.delete(f"/jobs/{job_id}")
    assert res_del.status_code == 200
