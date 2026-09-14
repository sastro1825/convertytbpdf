// components/ProgressStatus.tsx
"use client";

import React, { useEffect, useState } from "react";
import { JobStatus } from "@/lib/api";

interface ProgressStatusProps {
  statusData: JobStatus;
  onCancel: () => void;
}

export const ProgressStatus: React.FC<ProgressStatusProps> = ({
  statusData,
  onCancel,
}) => {
  const [elapsedSec, setElapsedSec] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSec((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatElapsed = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-5 animate-fadeIn">
      {/* Header Info */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center animate-spin">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 truncate max-w-md">
              {statusData.video_title || "Memproses Video..."}
            </h4>
            <p className="text-xs text-slate-500">{statusData.current_step}</p>
          </div>
        </div>

        <div className="text-right">
          <span className="text-xs font-mono text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">
            ⏱️ {formatElapsed(elapsedSec)}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between items-center text-xs text-slate-600 font-medium">
          <span>{statusData.message || "Sedang memproses..."}</span>
          <span className="font-bold text-blue-600">{statusData.progress}%</span>
        </div>
        <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${Math.max(4, Math.min(100, statusData.progress))}%` }}
          />
        </div>
      </div>

      {/* Tahap Alur Proses */}
      <div className="grid grid-cols-4 gap-2 text-center text-[11px] text-slate-400 font-medium pt-1">
        <div
          className={`p-1.5 rounded ${
            statusData.progress >= 15 ? "text-blue-600 bg-blue-50 font-semibold" : ""
          }`}
        >
          1. Ekstraksi
        </div>
        <div
          className={`p-1.5 rounded ${
            statusData.progress >= 50 ? "text-blue-600 bg-blue-50 font-semibold" : ""
          }`}
        >
          2. Filter & Seleksi
        </div>
        <div
          className={`p-1.5 rounded ${
            statusData.progress >= 85 ? "text-blue-600 bg-blue-50 font-semibold" : ""
          }`}
        >
          3. Susun PDF
        </div>
        <div
          className={`p-1.5 rounded ${
            statusData.progress >= 96 ? "text-blue-600 bg-blue-50 font-semibold" : ""
          }`}
        >
          4. Validasi
        </div>
      </div>

      {/* Tombol Batalkan */}
      <div className="pt-2 text-center">
        <button
          type="button"
          onClick={onCancel}
          className="text-xs text-slate-400 hover:text-red-600 font-medium transition py-1 px-3 rounded hover:bg-red-50"
        >
          Batalkan Proses Konversi
        </button>
      </div>
    </div>
  );
};
