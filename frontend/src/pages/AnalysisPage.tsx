import { useState, type FormEvent } from "react";
import { useParams, Link } from "react-router-dom";
import { isAxiosError } from "axios";
import { AppShell } from "../components/AppShell";
import { ScoreGauge } from "../components/ScoreGauge";
import { analysisApi } from "../lib/endpoints";
import type { Analysis, ApiError } from "../types";

const SECTION_LABELS: Record<string, string> = {
  contact: "Contact info",
  education: "Education",
  experience_or_projects: "Experience / Projects",
  skills: "Skills",
};

export function AnalysisPage() {
  const { resumeId } = useParams<{ resumeId: string }>();
  const [jobDescription, setJobDescription] = useState("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze(e: FormEvent) {
    e.preventDefault();
    if (!resumeId) return;
    setError(null);
    setIsRunning(true);
    try {
      const { data } = await analysisApi.run(resumeId, jobDescription.trim() || undefined);
      setAnalysis(data);
    } catch (err) {
      const message = isAxiosError<ApiError>(err)
        ? err.response?.data?.detail ?? "Analysis failed. Please try again."
        : "Analysis failed. Please try again.";
      setError(message);
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <AppShell>
      <Link to="/dashboard" className="font-body text-sm text-ink-soft hover:text-verdigris">
        ← Back to dashboard
      </Link>

      <h1 className="mt-3 font-display text-2xl font-semibold text-ink">ATS Analysis</h1>
      <p className="mt-1 font-body text-sm text-ink-soft">
        Optionally paste a job description to see how well your resume matches it.
      </p>

      <form onSubmit={handleAnalyze} className="mt-6">
        <textarea
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          rows={6}
          placeholder="Paste a job description here (optional)…"
          className="w-full rounded-md border border-line bg-white px-3 py-2.5 font-body text-sm text-ink outline-none focus:border-verdigris"
        />
        <button
          type="submit"
          disabled={isRunning}
          className="mt-3 rounded-md bg-ink px-5 py-2.5 font-body text-sm font-medium text-paper transition hover:bg-verdigris disabled:opacity-60"
        >
          {isRunning ? "Analyzing…" : "Run analysis"}
        </button>
      </form>

      {error && (
        <p role="alert" className="mt-4 rounded-md bg-clay-soft px-3 py-2 font-body text-sm text-clay">
          {error}
        </p>
      )}

      {analysis && (
        <div className="mt-10 grid gap-8 md:grid-cols-[auto_1fr]">
          <div className="flex justify-center md:justify-start">
            <ScoreGauge score={analysis.result.ats_score} />
          </div>

          <div className="space-y-8">
            <section>
              <h2 className="font-display text-lg font-semibold text-ink">Sections detected</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {Object.entries(analysis.result.sections_found).map(([key, found]) => (
                  <span
                    key={key}
                    className={`rounded-full px-3 py-1 font-mono text-xs ${
                      found ? "bg-verdigris-soft text-verdigris" : "bg-clay-soft text-clay"
                    }`}
                  >
                    {found ? "✓" : "✗"} {SECTION_LABELS[key] ?? key}
                  </span>
                ))}
              </div>
            </section>

            <section>
              <h2 className="font-display text-lg font-semibold text-ink">
                Skills found ({analysis.result.matched_skills.length})
              </h2>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {analysis.result.matched_skills.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-md bg-paper-dim px-2.5 py-1 font-mono text-xs text-ink-soft"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </section>

            {analysis.result.jd_match && (
              <section>
                <h2 className="font-display text-lg font-semibold text-ink">
                  Job description match — {analysis.result.jd_match.match_percentage}%
                </h2>
                {analysis.result.jd_match.missing_skills.length > 0 ? (
                  <>
                    <p className="mt-2 font-body text-sm text-ink-soft">Missing from your resume:</p>
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {analysis.result.jd_match.missing_skills.map((skill) => (
                        <span
                          key={skill}
                          className="rounded-md bg-clay-soft px-2.5 py-1 font-mono text-xs text-clay"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </>
                ) : (
                  <p className="mt-2 font-body text-sm text-verdigris">
                    Every skill mentioned in the job description was found in your resume.
                  </p>
                )}
              </section>
            )}

            <section>
              <h2 className="font-display text-lg font-semibold text-ink">Recommendations</h2>
              <ul className="mt-3 space-y-2">
                {analysis.result.recommendations.map((rec, i) => (
                  <li key={i} className="flex gap-2 font-body text-sm text-ink-soft">
                    <span className="text-verdigris">→</span>
                    {rec}
                  </li>
                ))}
                {analysis.result.recommendations.length === 0 && (
                  <li className="font-body text-sm text-verdigris">
                    No issues found — your resume looks solid.
                  </li>
                )}
              </ul>
            </section>
          </div>
        </div>
      )}
    </AppShell>
  );
}
