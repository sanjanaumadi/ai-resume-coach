import { useState, type FormEvent } from "react";
import { isAxiosError } from "axios";
import { rewriteApi } from "../lib/endpoints";
import type { ApiError } from "../types";

const SECTION_OPTIONS = [
  { value: "summary", label: "Career summary" },
  { value: "bullets", label: "Bullet points" },
  { value: "skills", label: "Skills section" },
] as const;

export function RewritePanel({ resumeId }: { resumeId: string }) {
  const [section, setSection] = useState<"summary" | "bullets" | "skills">("summary");
  const [text, setText] = useState("");
  const [rewrittenText, setRewrittenText] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRewrite(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setRewrittenText(null);
    setIsRunning(true);
    try {
      const { data } = await rewriteApi.run(resumeId, section, text);
      setRewrittenText(data.rewritten_text);
    } catch (err) {
      const message = isAxiosError<ApiError>(err)
        ? err.response?.data?.detail ?? "Rewrite failed. Please try again."
        : "Rewrite failed. Please try again.";
      setError(message);
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <section className="mt-10 rounded-lg border border-line bg-white p-6">
      <h2 className="font-display text-lg font-semibold text-ink">Rewrite a section</h2>
      <p className="mt-1 font-body text-sm text-ink-soft">
        Paste a section of your resume and get an AI-improved version.
      </p>

      <form onSubmit={handleRewrite} className="mt-4 space-y-3">
        <div className="flex gap-2">
          {SECTION_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setSection(opt.value)}
              className={`rounded-md border px-3 py-1.5 font-body text-sm transition ${
                section === opt.value
                  ? "border-verdigris bg-verdigris-soft text-verdigris"
                  : "border-line text-ink-soft hover:border-verdigris"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={4}
          minLength={10}
          required
          placeholder="Paste the section you want to improve…"
          className="w-full rounded-md border border-line bg-white px-3 py-2.5 font-body text-sm text-ink outline-none focus:border-verdigris"
        />

        <button
          type="submit"
          disabled={isRunning}
          className="rounded-md bg-ink px-5 py-2.5 font-body text-sm font-medium text-paper transition hover:bg-verdigris disabled:opacity-60"
        >
          {isRunning ? "Rewriting…" : "Rewrite with AI"}
        </button>
      </form>

      {error && (
        <p role="alert" className="mt-4 rounded-md bg-clay-soft px-3 py-2 font-body text-sm text-clay">
          {error}
        </p>
      )}

      {rewrittenText && (
        <div className="mt-5 rounded-md bg-verdigris-soft px-4 py-3">
          <p className="font-mono text-[10px] uppercase tracking-wider text-verdigris">Rewritten</p>
          <p className="mt-1.5 whitespace-pre-wrap font-body text-sm text-ink">{rewrittenText}</p>
        </div>
      )}
    </section>
  );
}
