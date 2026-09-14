// lib/api.ts
// Client helper untuk berkomunikasi dengan FastAPI Backend

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface JobStatus {
  job_id: string;
  status:
    | "waiting_upload"
    | "uploading"
    | "uploaded"
    | "downloading_video"
    | "reading_metadata"
    | "extracting_frames"
    | "filtering_frames"
    | "clustering_frames"
    | "selecting_frames"
    | "generating_pdf"
    | "validating_pdf"
    | "completed"
    | "failed"
    | "cancelled"
    | "waiting";
  progress: number;
  current_step: string;
  message: string;
  video_title?: string;
  output_filename?: string;
  page_count?: number;
  file_size_bytes?: number;
  input_type?: string;
  youtube_url?: string;
  error?: string;
}

export async function checkBackendHealth() {
  const res = await fetch(`${API_BASE_URL}/health`, { method: "GET" });
  if (!res.ok) throw new Error("Backend tidak dapat dihubungi");
  return res.json();
}

export async function createJob(inputType: "upload" | "youtube" = "upload"): Promise<{ job_id: string }> {
  const res = await fetch(`${API_BASE_URL}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input_type: inputType }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal membuat sesi pekerjaan konversi.");
  }
  return res.json();
}

export function uploadVideoFile(
  jobId: string,
  file: File,
  onProgress?: (percentage: number) => void
): Promise<{ job_id: string; filename: string; size_bytes: number }> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append("file", file);

    xhr.open("POST", `${API_BASE_URL}/jobs/${jobId}/upload`);

    if (xhr.upload && onProgress) {
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          onProgress(percent);
        }
      };
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const resp = JSON.parse(xhr.responseText);
          resolve(resp);
        } catch {
          resolve({ job_id: jobId, filename: file.name, size_bytes: file.size });
        }
      } else {
        try {
          const err = JSON.parse(xhr.responseText);
          reject(new Error(err.detail || "Gagal mengunggah video."));
        } catch {
          reject(new Error(`Gagal mengunggah video (HTTP ${xhr.status}).`));
        }
      }
    };

    xhr.onerror = () => {
      reject(new Error("Terjadi gangguan jaringan saat mengunggah video."));
    };

    xhr.send(formData);
  });
}

export async function submitYoutubeLink(
  jobId: string,
  url: string,
  agreement: boolean
) {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/youtube`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, agreement }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal memproses tautan YouTube.");
  }
  return res.json();
}

export async function startJobProcessing(jobId: string) {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/start`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal memulai proses konversi.");
  }
  return res.json();
}

export async function fetchJobStatus(jobId: string): Promise<JobStatus> {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/status`, {
    method: "GET",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal membaca status pekerjaan.");
  }
  return res.json();
}

export function getPdfPreviewUrl(jobId: string): string {
  return `${API_BASE_URL}/jobs/${jobId}/preview`;
}

export function getPdfDownloadUrl(jobId: string): string {
  return `${API_BASE_URL}/jobs/${jobId}/download`;
}

export async function deleteJob(jobId: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
      method: "DELETE",
    });
    return res.json();
  } catch {
    return { success: false };
  }
}
