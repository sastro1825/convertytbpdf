# -*- coding: utf-8 -*-
"""
Metadata Inspector & Video Title Cleaner
Membaca metadata video menggunakan imageio-ffmpeg / ffprobe dan membersihkan judul file.
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any

try:
    import imageio_ffmpeg
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False


def get_ffmpeg_cmd() -> str:
    """Mengambil path executable ffmpeg dari imageio-ffmpeg atau sistem PATH."""
    if IMAGEIO_AVAILABLE:
        try:
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                return exe
        except Exception:
            pass

    system_cmd = shutil.which("ffmpeg")
    if system_cmd:
        return system_cmd

    # WinGet packages fallback di Windows
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_path = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_path.exists():
            matches = list(winget_path.glob("**/ffmpeg.exe"))
            if matches:
                return str(matches[0])

    return "ffmpeg"


def clean_video_title(filename: str) -> str:
    """
    Membersihkan judul video dari metadata durasi, resolusi, codec, channel,
    dan karakter tidak aman untuk nama file PDF yang bersih.
    """
    base = Path(filename).stem
    # Hapus konten dalam kurung yang mengandung resolusi, codec, channel, durasi
    base = re.sub(
        r'[\(\[\{][^\)\]\}]*(?:240p|360p|480p|720p|1080p|1440p|2160p|4k|8k|h264|h265|x264|x265|avc1|hevc|av1|vp9|CATATAN|CHANNEL|YOUTUBE|OFFICIAL|REUP)[^\)\]\}]*[\)\]\}]',
        '',
        base,
        flags=re.IGNORECASE
    )
    # Hapus tag resolusi atau codec yang berdiri sendiri
    base = re.sub(
        r'\b(240p|360p|480p|720p|1080p|1440p|2160p|4k|8k|hd|fhd|uhd|h\.?264|h\.?265|x264|x265|avc1|hevc|av1|vp9|aac|mp3)\b',
        '',
        base,
        flags=re.IGNORECASE
    )
    # Hapus teks durasi
    base = re.sub(r'\bDurasi\s+[\w\d\s]+?(?=\.|\-|\(|$)', '', base, flags=re.IGNORECASE)
    # Hapus kurung kosong
    base = re.sub(r'[\(\[\{]\s*[\)\]\}]', '', base)
    # Ganti karakter non-alphanumeric dengan spasi
    base = re.sub(r'[^a-zA-Z0-9]', ' ', base)
    # Gabungkan kata dengan underscore
    words = base.strip().split()
    cleaned = "_".join(words)
    return cleaned or "Video_Materi"


def format_timestamp(seconds: float) -> str:
    """Mengubah detik ke format HH:MM:SS atau MM:SS."""
    s = int(round(seconds))
    hrs = s // 3600
    mins = (s % 3600) // 60
    secs = s % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def calculate_adaptive_interval(duration_sec: float, manual_interval: float = None) -> int:
    """Menghitung interval ekstraksi frame secara adaptif."""
    if manual_interval is not None and manual_interval > 0:
        return max(1, int(round(manual_interval)))

    if duration_sec <= 600:        # <= 10 menit
        return 2
    elif duration_sec <= 1800:     # 10 - 30 menit
        return 3
    elif duration_sec <= 3600:     # 30 - 60 menit
        return 5
    else:                          # > 60 menit
        return 8


def get_video_metadata(video_path: Path) -> Dict[str, Any]:
    """
    Mendapatkan durasi, resolusi, codec, fps, dan aspect ratio dari video.
    Menggunakan ffprobe jika tersedia, atau ffmpeg probe.
    """
    ffprobe_cmd = shutil.which("ffprobe")
    if not ffprobe_cmd:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            winget_path = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
            if winget_path.exists():
                matches = list(winget_path.glob("**/ffprobe.exe"))
                if matches:
                    ffprobe_cmd = str(matches[0])

    if ffprobe_cmd:
        try:
            cmd = [
                ffprobe_cmd, "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", str(video_path)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            vstream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
            fmt = data.get("format", {})

            width = int(vstream.get("width", 0))
            height = int(vstream.get("height", 0))
            codec = vstream.get("codec_name", "unknown")
            fps_str = vstream.get("avg_frame_rate", "30/1")
            if "/" in fps_str:
                num, den = map(float, fps_str.split("/"))
                fps = round(num / den, 2) if den > 0 else 30.0
            else:
                fps = float(fps_str) if fps_str else 30.0

            duration = float(fmt.get("duration", vstream.get("duration", 0.0)))
            bitrate = int(fmt.get("bit_rate", vstream.get("bit_rate", 0)))
            dar = vstream.get("display_aspect_ratio", f"{width}:{height}")

            return {
                "filename": video_path.name,
                "cleaned_title": clean_video_title(video_path.name),
                "duration_sec": duration,
                "duration_str": format_timestamp(duration),
                "width": width,
                "height": height,
                "codec": codec,
                "fps": fps,
                "bitrate": bitrate,
                "aspect_ratio": dar
            }
        except Exception:
            pass

    # Fallback menggunakan ffmpeg standard error parsing
    ffmpeg_exe = get_ffmpeg_cmd()
    cmd = [ffmpeg_exe, "-hide_banner", "-i", str(video_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = proc.stderr

    dur_match = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', out)
    if dur_match:
        h, m, s = map(float, dur_match.groups())
        duration = h * 3600 + m * 60 + s
    else:
        duration = 0.0

    res_match = re.search(r'Stream.*Video:.*?(\d{2,5})x(\d{2,5})', out)
    if res_match:
        width = int(res_match.group(1))
        height = int(res_match.group(2))
    else:
        width = 1280
        height = 720

    fps_match = re.search(r'(\d+(?:\.\d+)?)\s*fps', out)
    fps = float(fps_match.group(1)) if fps_match else 30.0

    codec_match = re.search(r'Stream.*Video:\s*([a-zA-Z0-9_]+)', out)
    codec = codec_match.group(1) if codec_match else "h264"

    return {
        "filename": video_path.name,
        "cleaned_title": clean_video_title(video_path.name),
        "duration_sec": duration,
        "duration_str": format_timestamp(duration),
        "width": width,
        "height": height,
        "codec": codec,
        "fps": fps,
        "bitrate": 0,
        "aspect_ratio": f"{width}:{height}"
    }
