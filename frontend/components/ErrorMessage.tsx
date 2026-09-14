// components/ErrorMessage.tsx
import React from "react";

interface ErrorMessageProps {
  message: string;
  onDismiss?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  onDismiss,
}) => {
  if (!message) return null;

  return (
    <div className="p-4 mb-6 rounded-xl bg-red-50 border border-red-200 flex items-start justify-between shadow-sm animate-fadeIn">
      <div className="flex items-start gap-3">
        <svg
          className="w-5 h-5 text-red-600 mt-0.5 shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <div>
          <h4 className="text-sm font-semibold text-red-900">
            Terjadi Kendala
          </h4>
          <p className="text-sm text-red-700 mt-0.5 leading-relaxed">{message}</p>
        </div>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-400 hover:text-red-700 transition p-1"
          aria-label="Tutup pesan error"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
};
