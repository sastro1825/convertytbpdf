// components/VideoUpload.tsx
"use client";

import React, { useState, useRef } from "react";

interface VideoUploadProps {
  onStartUpload: (file: File) => void;
  disabled?: boolean;
}

const SUPPORTED_FORMATS = [".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v"];

export const VideoUpload: React.FC<VideoUploadProps> = ({
  onStartUpload,
  disabled = false,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [formatError, setFormatError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleValidateAndSetFile = (file: File) => {
    setFormatError(null);
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!SUPPORTED_FORMATS.includes(ext)) {
      setFormatError(
        `Format file '${ext}' tidak didukung. Silakan gunakan format: ${SUPPORTED_FORMATS.join(", ")}`
      );
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleValidateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleValidateAndSetFile(e.target.files[0]);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setFormatError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = () => {
    if (selectedFile && !disabled) {
      onStartUpload(selectedFile);
    }
  };

  const formatFileSize = (bytes: number) => {
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  return (
    <div className="space-y-5">
      {/* Drag & Drop Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragging
            ? "border-blue-500 bg-blue-50/60 scale-[1.01]"
            : "border-slate-300 hover:border-blue-400 bg-slate-50/50 hover:bg-slate-50"
        } ${disabled ? "opacity-60 cursor-not-allowed" : ""}`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".mp4,.mkv,.mov,.avi,.webm,.m4v,video/*"
          className="hidden"
          disabled={disabled}
        />

        <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 shadow-sm">
          <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>

        <h3 className="text-base font-semibold text-slate-800">
          Tarik & Lepaskan File Video ke Sini
        </h3>
        <p className="text-sm text-slate-500 mt-1">
          atau{" "}
          <span className="text-blue-600 font-medium hover:underline">
            Pilih Video dari Komputer
          </span>
        </p>
        <p className="text-xs text-slate-400 mt-3 font-mono">
          Format: MP4, MKV, MOV, AVI, WEBM, M4V (Maks. 500 MB / 90 Menit)
        </p>
      </div>

      {formatError && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {formatError}
        </div>
      )}

      {/* Info File Terpilih */}
      {selectedFile && (
        <div className="p-4 bg-white border border-slate-200 rounded-xl flex items-center justify-between shadow-sm animate-fadeIn">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
            </div>
            <div className="truncate">
              <p className="text-sm font-semibold text-slate-800 truncate">
                {selectedFile.name}
              </p>
              <p className="text-xs text-slate-500">
                Ukuran: {formatFileSize(selectedFile.size)} &bull; Format:{" "}
                {selectedFile.name.split(".").pop()?.toUpperCase()}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleClear}
            disabled={disabled}
            className="text-xs text-slate-400 hover:text-red-600 transition px-2 py-1"
          >
            Ganti
          </button>
        </div>
      )}

      {/* Tombol Aksi */}
      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!selectedFile || disabled}
          className="flex-1 py-3 px-5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 text-white font-medium text-sm transition shadow-sm flex items-center justify-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
          Mulai Konversi ke PDF
        </button>

        {selectedFile && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="py-3 px-4 rounded-xl border border-slate-300 hover:bg-slate-100 text-slate-700 text-sm font-medium transition"
          >
            Batal
          </button>
        )}
      </div>

      <div className="text-xs text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-200 leading-relaxed">
        💡 <strong>Metode Utama & Direkomendasikan:</strong> Mengunggah video langsung menghasilkan proses konversi yang paling cepat, akurat, dan tidak terpengaruh batasan unduhan pihak ketiga.
      </div>
    </div>
  );
};
