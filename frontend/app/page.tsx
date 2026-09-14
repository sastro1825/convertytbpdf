// app/page.tsx
"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  createJob,
  uploadVideoFile,
  submitYoutubeLink,
  startJobProcessing,
  fetchJobStatus,
  deleteJob,
  JobStatus,
} from "@/lib/api";
import { VideoUpload } from "@/components/VideoUpload";
import { YoutubeInput } from "@/components/YoutubeInput";
import { ProgressStatus } from "@/components/ProgressStatus";
import { ResultCard } from "@/components/ResultCard";
import { ErrorMessage } from "@/components/ErrorMessage";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"upload" | "youtube">("upload");
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // Polling Status Job setiap 2 detik jika proses sedang berjalan
  useEffect(() => {
    if (!currentJobId) return;

    const poll = async () => {
      try {
        const data = await fetchJobStatus(currentJobId);
        setJobStatus(data);

        if (data.status === "completed") {
          setIsBusy(false);
          if (pollingRef.current) clearInterval(pollingRef.current);
        } else if (data.status === "failed") {
          setIsBusy(false);
          setErrorMessage(data.error || data.message || "Proses konversi gagal.");
          if (pollingRef.current) clearInterval(pollingRef.current);
        } else if (data.status === "cancelled") {
          setIsBusy(false);
          if (pollingRef.current) clearInterval(pollingRef.current);
        }
      } catch (err: unknown) {
        console.error("Polling error:", err);
      }
    };

    // Jalankan pertama kali langsung, lalu setiap 2 detik
    poll();
    pollingRef.current = setInterval(poll, 2000);

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [currentJobId]);

  // Handler: Mulai Upload File Video
  const handleStartUpload = async (file: File) => {
    setErrorMessage(null);
    setIsBusy(true);

    try {
      // 1. Buat job di backend
      const { job_id } = await createJob("upload");
      setCurrentJobId(job_id);

      // 2. Upload file video
      setJobStatus({
        job_id,
        status: "uploading",
        progress: 5,
        current_step: "Mengunggah video ke server",
        message: `Mengunggah ${file.name}...`,
        video_title: file.name,
      });

      await uploadVideoFile(job_id, file, (percent) => {
        setJobStatus((prev) => (prev ? { ...prev, progress: Math.min(15, Math.round(percent * 0.15)) } : null));
      });

      // 3. Picu pemrosesan pipeline di latar belakang
      await startJobProcessing(job_id);
    } catch (err: unknown) {
      setIsBusy(false);
      const msg = err instanceof Error ? err.message : "Gagal memulai proses unggahan.";
      setErrorMessage(msg);
      setCurrentJobId(null);
      setJobStatus(null);
    }
  };

  // Handler: Mulai Proses Link YouTube
  const handleSubmitYoutube = async (url: string, agreement: boolean) => {
    setErrorMessage(null);
    setIsBusy(true);

    try {
      // 1. Buat job di backend
      const { job_id } = await createJob("youtube");
      setCurrentJobId(job_id);

      // 2. Kirim URL YouTube
      await submitYoutubeLink(job_id, url, agreement);

      // 3. Picu pemrosesan pipeline
      await startJobProcessing(job_id);
    } catch (err: unknown) {
      setIsBusy(false);
      const msg = err instanceof Error ? err.message : "Gagal memproses tautan YouTube.";
      setErrorMessage(msg);
      setCurrentJobId(null);
      setJobStatus(null);
    }
  };

  // Handler: Batalkan Proses
  const handleCancelJob = async () => {
    if (currentJobId) {
      await deleteJob(currentJobId);
    }
    if (pollingRef.current) clearInterval(pollingRef.current);
    setCurrentJobId(null);
    setJobStatus(null);
    setIsBusy(false);
    setErrorMessage("Proses konversi telah dibatalkan.");
  };

  // Handler: Reset Form untuk Video Baru
  const handleReset = () => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    setCurrentJobId(null);
    setJobStatus(null);
    setIsBusy(false);
    setErrorMessage(null);
  };

  // Handler: Hapus Hasil dari Server
  const handleDeleteResult = async () => {
    if (currentJobId) {
      await deleteJob(currentJobId);
    }
    handleReset();
  };

  const isCompleted = jobStatus?.status === "completed";
  const isInProgress = Boolean(
    isBusy || (jobStatus && !["completed", "failed", "cancelled"].includes(jobStatus.status))
  );

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col justify-between text-slate-800">
      {/* Header Utama */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 shadow-xs">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-base shadow-sm">
              RF
            </div>
            <div>
              <h1 className="text-base font-bold text-slate-900 leading-tight">
                RidhoFajar Video to PDF
              </h1>
              <p className="text-[11px] text-slate-500">
                Konverter Visual Materi Video Pembelajaran
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200/60">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse" />
              Sistem Aktif
            </span>
          </div>
        </div>
      </header>

      {/* Konten Utama */}
      <main className="flex-1 max-w-3xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Banner Penjelasan Singkat */}
        <div className="text-center mb-8 space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Ubah Video Materi Menjadi PDF Rapi
          </h2>
          <p className="text-sm sm:text-base text-slate-600 max-w-xl mx-auto leading-relaxed">
            Ekstrak seluruh papan tulis, diagram, slide, dan catatan penting dari video secara otomatis ke dalam dokumen PDF A4 tanpa memotong materi asli.
          </p>
        </div>

        {/* Pesan Kesalahan jika ada */}
        <ErrorMessage
          message={errorMessage || ""}
          onDismiss={() => setErrorMessage(null)}
        />

        {/* Tampilan Kondisional: Hasil Selesai / Sedang Berjalan / Form Input */}
        {isCompleted && jobStatus ? (
          <ResultCard
            statusData={jobStatus}
            onReset={handleReset}
            onDelete={handleDeleteResult}
          />
        ) : isInProgress && jobStatus ? (
          <ProgressStatus
            statusData={jobStatus}
            onCancel={handleCancelJob}
          />
        ) : (
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
            {/* Navigasi Tab */}
            <div className="flex border-b border-slate-200 bg-slate-50/70 p-1.5 gap-1.5">
              <button
                type="button"
                onClick={() => {
                  setActiveTab("upload");
                  setErrorMessage(null);
                }}
                disabled={isInProgress}
                className={`flex-1 py-2.5 px-4 rounded-xl text-sm font-semibold transition flex items-center justify-center gap-2 ${
                  activeTab === "upload"
                    ? "bg-white text-blue-700 shadow-xs border border-slate-200/80"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                  />
                </svg>
                Upload Video (Utama)
              </button>

              <button
                type="button"
                onClick={() => {
                  setActiveTab("youtube");
                  setErrorMessage(null);
                }}
                disabled={isInProgress}
                className={`flex-1 py-2.5 px-4 rounded-xl text-sm font-semibold transition flex items-center justify-center gap-2 ${
                  activeTab === "youtube"
                    ? "bg-white text-blue-700 shadow-xs border border-slate-200/80"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                </svg>
                Link YouTube
              </button>
            </div>

            {/* Isi Tab */}
            <div className="p-6 sm:p-8">
              {activeTab === "upload" ? (
                <VideoUpload
                  onStartUpload={handleStartUpload}
                  disabled={isInProgress}
                />
              ) : (
                <YoutubeInput
                  onSubmitYoutube={handleSubmitYoutube}
                  disabled={isInProgress}
                />
              )}
            </div>
          </div>
        )}

        {/* Fitur Utama Informasi */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8">
          <div className="p-4 bg-white rounded-xl border border-slate-200/80 shadow-xs">
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-sm mb-2">
              1
            </div>
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide">
              Tanpa Crop Buatan
            </h4>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Seluruh frame video dipertahankan utuh dari sudut ke sudut dengan format A4 lanskap.
            </p>
          </div>

          <div className="p-4 bg-white rounded-xl border border-slate-200/80 shadow-xs">
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-sm mb-2">
              2
            </div>
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide">
              Filter Cerdas & pHash
            </h4>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Menghapus layar kosong, transisi buram, dan duplikat, serta memilih versi tulisan terlengkap.
            </p>
          </div>

          <div className="p-4 bg-white rounded-xl border border-slate-200/80 shadow-xs">
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-sm mb-2">
              3
            </div>
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide">
              Privasi & Aman
            </h4>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Semua file di server bersifat sementara dan langsung dihapus setelah proses selesai.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        <p>
          &copy; {new Date().getFullYear()} RidhoFajar Video to PDF Converter &bull; Penggunaan Pribadi & Publik Terbatas
        </p>
        <p className="mt-1 text-slate-400">
          Frontend Next.js di Vercel &bull; Backend FastAPI di Render
        </p>
      </footer>
    </div>
  );
}
