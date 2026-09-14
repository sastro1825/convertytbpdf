// components/ResultCard.tsx
"use client";

import React from "react";
import { JobStatus, getPdfDownloadUrl, getPdfPreviewUrl } from "@/lib/api";

interface ResultCardProps {
  statusData: JobStatus;
  onReset: () => void;
  onDelete: () => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({
  statusData,
  onReset,
  onDelete,
}) => {
  const previewUrl = getPdfPreviewUrl(statusData.job_id);
  const downloadUrl = getPdfDownloadUrl(statusData.job_id);

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "0 MB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  return (
    <div className="bg-white border border-emerald-200 rounded-2xl p-6 sm:p-8 shadow-sm space-y-6 animate-fadeIn">
      {/* Success Badge & Title */}
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <span className="inline-block text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200/60 mb-1">
            Konversi Berhasil
          </span>
          <h3 className="text-lg font-bold text-slate-900 leading-snug">
            {statusData.output_filename || "Dokumen Materi Video.pdf"}
          </h3>
        </div>
      </div>

      {/* Detail Ringkasan */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 bg-slate-50 rounded-xl border border-slate-200/80 text-sm">
        <div>
          <span className="block text-xs text-slate-500">Jumlah Halaman:</span>
          <span className="font-semibold text-slate-800">
            {statusData.page_count || 0} Halaman (A4)
          </span>
        </div>
        <div>
          <span className="block text-xs text-slate-500">Ukuran File PDF:</span>
          <span className="font-semibold text-slate-800">
            {formatFileSize(statusData.file_size_bytes)}
          </span>
        </div>
        <div className="col-span-2 sm:col-span-1">
          <span className="block text-xs text-slate-500">Kualitas Visual:</span>
          <span className="font-semibold text-slate-800 text-emerald-600">
            HD Lanczos 100%
          </span>
        </div>
      </div>

      {/* Tombol Aksi Utama */}
      <div className="flex flex-col sm:flex-row gap-3 pt-1">
        {/* Tombol Download PDF */}
        <a
          href={downloadUrl}
          download
          className="flex-1 py-3 px-5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm transition shadow-sm flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          Unduh Dokumen PDF
        </a>

        {/* Tombol Preview PDF */}
        <a
          href={previewUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="py-3 px-5 rounded-xl border border-slate-300 hover:bg-slate-100 text-slate-700 font-medium text-sm transition flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
            />
          </svg>
          Buka Preview
        </a>
      </div>

      {/* Tombol Reset & Hapus */}
      <div className="flex items-center justify-between border-t border-slate-100 pt-4 text-xs text-slate-500">
        <button
          type="button"
          onClick={onDelete}
          className="text-red-500 hover:text-red-700 font-medium transition flex items-center gap-1.5"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
          Hapus Hasil dari Server
        </button>

        <button
          type="button"
          onClick={onReset}
          className="text-blue-600 hover:text-blue-800 font-medium transition"
        >
          &larr; Konversi Video Lain
        </button>
      </div>
    </div>
  );
};
