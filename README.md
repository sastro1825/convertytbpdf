# RidhoFajar Video to PDF Converter (Web Version)

Aplikasi web modern, sederhana, dan ramah pengguna untuk mengonversi materi visual penting (papan tulis, slide presentasi, diagram alur, perhitungan, tutorial, dan dokumen) dari file video menjadi dokumen PDF berkualitas tinggi (A4 Lanskap) tanpa mengubah susunan materi asli dan tanpa manipulasi teks/angka.

---

## 📌 Ringkasan Proyek

- **Nama Aplikasi**: RidhoFajar Video to PDF
- **Target URL Vercel**: `https://ridhofajar-convert-video-pdf.vercel.app`
- **Repository GitHub**: `https://github.com/sastro1825/convertytbpdf.git`
- **Branch Kerja**: `feature/simple-web-converter`
- **Desktop Baseline**: Sistem desktop lama berbasis `run.bat` di root folder tetap aman dan dapat digunakan secara terpisah.

---

## 🏛️ Arsitektur Sederhana (Tanpa Docker & Tanpa Database)

Aplikasi dirancang khusus untuk penggunaan pribadi dan publik terbatas dengan memprioritaskan kesederhanaan pemeliharaan:

```
[Browser Klien]
      │
      ▼
[Frontend: Next.js di Vercel]
      │  (REST API & Polling Progres setiap 2 detik)
      ▼
[Backend: FastAPI di Render]
      ├── Job Manager (File-Based status.json & asyncio.Lock)
      ├── Pipeline Python (FFmpeg, Pillow Lanczos, DCT pHash, ReportLab)
      ├── yt-dlp (Untuk tautan YouTube)
      └── PyMuPDF (Render & Validasi PDF tanpa Poppler)
      │
      ▼
[Penyimpanan Sementara: backend/temp/jobs/{job_id}/]
      └── File video langsung dihapus setelah PDF selesai
```

> [!NOTE]
> **Pernyataan Kejujuran & Batasan Sistem:**
> 1. **Tanpa Database**: Sistem tidak menggunakan MySQL, PostgreSQL, Redis, Supabase, atau Firebase. Semua status disimpan sementara dalam file `status.json`.
> 2. **Penyimpanan Bersifat Sementara (Ephemeral)**: Karena hosting Render bersifat sementara, restart server dapat menghapus file job lama. File hasil konversi otomatis dibersihkan dalam 6 jam.
> 3. **Single Concurrency Lock**: Untuk menjaga kestabilan memori di server Render gratis/ringan, sistem memproses **1 video dalam satu waktu**. Job lain akan mendapatkan status `waiting`.
> 4. **Upload Video Lebih Stabil**: Input link YouTube disediakan sebagai fitur tambahan menggunakan `yt-dlp`. Karena kebijakan YouTube (DRM, proteksi bot/IP, video privat), fitur YouTube dapat gagal. Mengunggah video secara langsung adalah metode yang paling andal dan direkomendasikan.

---

## 🛠️ Tech Stack

### Frontend:
- **Framework**: Next.js 15+ (App Router)
- **Bahasa**: TypeScript
- **Styling**: Tailwind CSS (Latar terang, biru tua slate `#0f172a`, aksen biru cerah `#2563eb`)
- **Deployment**: Vercel

### Backend:
- **Framework**: FastAPI + Uvicorn
- **Bahasa**: Python 3.10+ (teruji pada Python 3.13)
- **Pengolahan Video**: `imageio-ffmpeg` (binary ffmpeg portabel otomatis)
- **Pengolahan Citra & pHash**: `Pillow`, `NumPy`, `SciPy` (DCT frekuensi rendah 8x8)
- **Penyusunan PDF**: `ReportLab` (Format A4 Lanskap, contain/preserved aspect ratio)
- **Validasi & Render PDF**: `PyMuPDF` (`fitz`) dan `pypdf` (tanpa butuh Poppler sistem)
- **Unduhan YouTube**: `yt-dlp`
- **Deployment**: Render (Python Web Service)

---

## 📁 Struktur Direktori

```
web convert/
├── frontend/                          # Aplikasi Next.js (Deploy ke Vercel)
│   ├── app/
│   │   ├── page.tsx                   # Halaman utama (Tab Upload, YouTube, Progres, Hasil)
│   │   ├── layout.tsx                 # Layout & SEO metadata
│   │   └── globals.css                # Style Tailwind
│   ├── components/
│   │   ├── VideoUpload.tsx            # Form upload drag-and-drop
│   │   ├── YoutubeInput.tsx           # Form input YouTube & persetujuan izin
│   │   ├── ProgressStatus.tsx         # Progress bar & timer real-time
│   │   ├── ResultCard.tsx             # Kartu hasil: tombol preview & download
│   │   └── ErrorMessage.tsx           # Banner pesan kendala
│   ├── lib/
│   │   └── api.ts                     # API client penghubung frontend-backend
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
├── backend/                           # Aplikasi FastAPI (Deploy ke Render)
│   ├── app/
│   │   ├── main.py                    # REST API endpoints & CORS
│   │   ├── jobs.py                    # Job manager, concurrency lock, background tasks
│   │   ├── cleanup.py                 # Manajemen retensi & pembersihan file
│   │   └── pipeline/
│   │       ├── metadata.py            # Inspeksi durasi & sanitasi judul
│   │       ├── frame_extractor.py     # Ekstraksi frame adaptif via FFmpeg
│   │       ├── frame_filter.py        # Filter blur, intro/outro, presenter-only
│   │       ├── frame_cluster.py       # pHash DCT & penanganan zoom kamera
│   │       ├── frame_selector.py      # Seleksi frame paling lengkap & sorting timestamp
│   │       ├── enhancer.py            # Resize Lanczos proporsional & ketajaman
│   │       ├── pdf_builder.py         # ReportLab A4 Lanskap
│   │       └── validator.py           # Validasi PyMuPDF & pypdf
│   ├── temp/                          # Folder kerja sementara per job
│   ├── tests/                         # Pengujian otomatis pytest
│   ├── requirements.txt               # Dependensi pip backend
│   ├── render.yaml                    # Blueprint deployment Render
│   └── .env.example
├── run_backend.bat                    # Script lokal: jalankan FastAPI port 8000
├── run_frontend.bat                   # Script lokal: jalankan Next.js port 3000
├── run_web_local.bat                  # Script lokal 1-klik: buka backend, frontend, & browser
├── .gitignore
└── README.md
```

---

## 🚀 Cara Menjalankan Secara Lokal (Development)

### Metode 1-Klik:
Klik ganda pada file:
```
E:\ppt pak kakan\web convert\run_web_local.bat
```
Script ini akan:
1. Menjalankan Backend di `http://localhost:8000` pada jendela terpisah.
2. Menjalankan Frontend di `http://localhost:3000` pada jendela terpisah.
3. Membuka browser Anda secara otomatis ke `http://localhost:3000`.

### Menjalankan Secara Manual:
1. **Terminal 1 (Backend):**
   ```cmd
   cd "web convert"
   run_backend.bat
   ```
2. **Terminal 2 (Frontend):**
   ```cmd
   cd "web convert"
   run_frontend.bat
   ```

---

## 🌐 Panduan Deployment ke Cloud

### 1. Deploy Backend ke Render
1. Buka dashboard [Render.com](https://render.com).
2. Pilih **New +** &rarr; **Web Service**.
3. Hubungkan repository GitHub: `https://github.com/sastro1825/convertytbpdf.git`.
4. Atur konfigurasi:
   - **Root Directory**: `web convert/backend` (atau `backend` jika repo root mengarah ke web convert).
   - **Runtime**: Python 3.
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Tambahkan Environment Variable di Render:
   - `ALLOWED_ORIGINS`: `https://ridhofajar-convert-video-pdf.vercel.app,http://localhost:3000`
   - `MAX_VIDEO_SIZE_MB`: `500`
   - `MAX_VIDEO_DURATION_MINUTES`: `90`
   - `JOB_RETENTION_HOURS`: `6`
   - `MAX_CONCURRENT_JOBS`: `1`
6. Salin URL backend yang diberikan Render (misal: `https://ridhofajar-backend.onrender.com`).

---

### 2. Deploy Frontend ke Vercel
1. Buka dashboard [Vercel.com](https://vercel.com).
2. Tambahkan New Project dari repository: `https://github.com/sastro1825/convertytbpdf.git`.
3. Atur konfigurasi:
   - **Project Name**: `ridhofajar-convert-video-pdf`
   - **Root Directory**: `web convert/frontend` (atau `frontend`).
   - **Framework Preset**: Next.js.
4. Tambahkan Environment Variable di Vercel:
   - `NEXT_PUBLIC_API_URL`: URL Backend Render Anda (contoh: `https://ridhofajar-backend.onrender.com`).
5. Klik **Deploy**.

---

## 🔒 Keamanan & Batasan Penggunaan

- **UUID Job**: Setiap sesi proses menggunakan ID UUID4 acak yang aman dari tabrakan data.
- **Sanitasi File**: Nama file dibersihkan dari simbol berbahaya untuk mencegah serangan Path Traversal.
- **Validasi Format**: Hanya file video berekstensi `.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`, `.m4v` yang diizinkan.
- **Batas Ukuran**: Default maksimal 500 MB dan durasi maksimal 90 menit.
- **Timeout Subprocess**: Ekstraksi FFmpeg dan unduhan YouTube dilengkapi timeout untuk mencegah proses menggantung (hang).
- **Download Resmi Browser**: Tombol download mengirim header standar `Content-Disposition: attachment; filename="..."` sehingga berkas otomatis masuk ke folder `Downloads` pengguna atau sesuai preferensi browser tanpa mencoba menulis folder lokal secara paksa.

---

## 🔄 Hubungan dengan Sistem Desktop `run.bat` Lama

Sistem desktop lokal yang berada di folder:
```
E:\ppt pak kakan\run.bat
```
**Tetap utuh 100% dan tidak terganggu sama sekali**. Anda tetap dapat memproses video lokal secara offline tanpa membuka web dengan mengeklik `run.bat` lama kapan saja.
