// components/YoutubeInput.tsx
"use client";

import React, { useState } from "react";

interface YoutubeInputProps {
  onSubmitYoutube: (url: string, agreement: boolean) => void;
  disabled?: boolean;
}

export const YoutubeInput: React.FC<YoutubeInputProps> = ({
  onSubmitYoutube,
  disabled = false,
}) => {
  const [url, setUrl] = useState("");
  const [agreement, setAgreement] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const cleanUrl = url.trim();
    if (!cleanUrl) {
      setError("Silakan masukkan tautan URL video YouTube.");
      return;
    }

    const ytRegex =
      /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/shorts\/|youtube\.com\/embed\/)[a-zA-Z0-9_\-]{6,15}/;
    if (!ytRegex.test(cleanUrl)) {
      setError("Format URL YouTube tidak valid. Contoh: https://www.youtube.com/watch?v=xxxxx");
      return;
    }

    if (!agreement) {
      setError("Anda wajib mencentang persetujuan hak cipta sebelum memproses video YouTube.");
      return;
    }

    onSubmitYoutube(cleanUrl, agreement);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Masukkan Tautan Video YouTube
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
            </svg>
          </div>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            disabled={disabled}
            className="w-full pl-11 pr-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm text-slate-800 placeholder-slate-400 bg-white transition shadow-sm"
          />
        </div>
      </div>

      {/* Persetujuan Hak Cipta */}
      <div className="flex items-start gap-3 p-3.5 bg-slate-50 border border-slate-200 rounded-xl">
        <input
          type="checkbox"
          id="yt-agree"
          checked={agreement}
          onChange={(e) => setAgreement(e.target.checked)}
          disabled={disabled}
          className="mt-1 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
        />
        <label htmlFor="yt-agree" className="text-xs text-slate-700 leading-relaxed cursor-pointer select-none">
          Saya menyatakan memiliki hak atau izin untuk memproses video ini.
        </label>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Tombol Ambil Video */}
      <button
        type="submit"
        disabled={disabled || !url.trim() || !agreement}
        className="w-full py-3 px-5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 text-white font-medium text-sm transition shadow-sm flex items-center justify-center gap-2"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        Ambil Video & Mulai Konversi
      </button>

      {/* Catatan Batasan YouTube */}
      <div className="text-xs text-slate-500 bg-amber-50/60 p-3 rounded-lg border border-amber-200/80 leading-relaxed">
        ⚠️ <strong>Catatan Fitur YouTube:</strong> Sistem mematuhi kebijakan YouTube dan tidak mencoba melewati DRM, login, proteksi usia, atau video privat. Jika proses gagal karena pembatasan YouTube, silakan unduh video secara legal lalu gunakan tab <strong>Upload Video</strong>.
      </div>
    </form>
  );
};
