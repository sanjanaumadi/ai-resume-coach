import { useEffect, useRef, useState } from "react";
import { isAxiosError } from "axios";
import { Link } from "react-router-dom";
import { AppShell } from "../components/AppShell";
import { resumeApi } from "../lib/endpoints";
import type { ApiError, ResumeDetail } from "../types";

export function DashboardPage() {
  const [resumes, setResumes] = useState<ResumeDetail[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function loadResumes() {
    setIsLoading(true);
    try {
      const { data } = await resumeApi.list();
      setResumes(data.resumes);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadResumes();
  }, []);

  async function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);
    setIsUploading(true);
    try {
      await resumeApi.upload(file);
      await loadResumes();
    } catch (err) {
      const message = isAxiosError<ApiError>(err)
        ? err.response?.data?.detail ?? "Upload failed. Please try again."
        : "Upload failed. Please try again.";
      setError(message);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Your resumes</h1>
          <p className="mt-1 font-body text-sm text-ink-soft">
            Upload a resume to get an ATS score and closing the gap on any job description.
          </p>
        </div>
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileSelect}
            className="hidden"
            id="resume-upload"
          />
          <label
            htmlFor="resume-upload"
            className="cursor-pointer rounded-md bg-ink px-4 py-2.5 font-body text-sm font-medium text-paper transition hover:bg-verdigris"
          >
            {isUploading ? "Uploading…" : "Upload resume"}
          </label>
        </div>
      </div>

      {error && (
        <p role="alert" className="mt-4 rounded-md bg-clay-soft px-3 py-2 font-body text-sm text-clay">
          {error}
        </p>
      )}

      <div className="mt-8">
        {isLoading ? (
          <p className="font-mono text-sm text-ink-soft">Loading…</p>
        ) : resumes.length === 0 ? (
          <div className="rounded-lg border border-dashed border-line py-16 text-center">
            <p className="font-display text-lg text-ink">No resumes yet</p>
            <p className="mt-1 font-body text-sm text-ink-soft">
              Upload a PDF or DOCX to get your first ATS score.
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-line rounded-lg border border-line bg-white">
            {resumes.map((resume) => (
              <li key={resume.id} className="flex items-center justify-between px-5 py-4">
                <div>
                  <p className="font-body text-sm font-medium text-ink">{resume.original_filename}</p>
                  <p className="mt-0.5 font-mono text-xs text-ink-soft">
                    {resume.file_type.toUpperCase()} · {resume.char_count.toLocaleString()} characters ·{" "}
                    {new Date(resume.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Link
                    to={`/analyze/${resume.id}`}
                    className="rounded-md border border-line px-3 py-1.5 font-body text-sm text-ink transition hover:border-verdigris hover:text-verdigris"
                  >
                    Analyze →
                  </Link>
                  <Link
                    to={`/interview/${resume.id}`}
                    className="rounded-md border border-line px-3 py-1.5 font-body text-sm text-ink transition hover:border-verdigris hover:text-verdigris"
                  >
                    Mock interview →
                  </Link>
                  <Link
                    to={`/career/${resume.id}`}
                    className="rounded-md border border-line px-3 py-1.5 font-body text-sm text-ink transition hover:border-verdigris hover:text-verdigris"
                  >
                    Career fit →
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </AppShell>
  );
}
