import { useState, type FormEvent } from "react";
import { useParams, Link } from "react-router-dom";
import { isAxiosError } from "axios";
import { AppShell } from "../components/AppShell";
import { ScoreGauge } from "../components/ScoreGauge";
import { careerSuggestionApi } from "../lib/endpoints";
import type { ApiError, CareerSuggestion } from "../types";

export function CareerSuggestionsPage() {
  const { resumeId } = useParams<{ resumeId: string }>();
  const [targetRole, setTargetRole] = useState("");
  const [suggestion, setSuggestion] = useState<CareerSuggestion | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate(e: FormEvent) {
    e.preventDefault();
    if (!resumeId) return;
    setError(null);
    setIsLoading(true);
    try {
      const { data } = await careerSuggestionApi.generate(resumeId, targetRole.trim() || undefined);
      setSuggestion(data);
    } catch (err) {
      const message = isAxiosError<ApiError>(err)
        ? err.response?.data?.detail ?? "Something went wrong. Please try again."
        : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <AppShell>
      <Link to="/dashboard" className="font-body text-sm text-ink-soft hover:text-verdigris">
        ← Back to dashboard
      </Link>

      <h1 className="mt-3 font-display text-2xl font-semibold text-ink">Career Suggestions</h1>
      <p className="mt-1 font-body text-sm text-ink-soft">
        Get AI-suggested roles, skill gaps, and a learning roadmap based on your resume.
      </p>

      <form onSubmit={handleGenerate} className="mt-6 flex gap-2">
        <input
          type="text"
          value={targetRole}
          onChange={(e) => setTargetRole(e.target.value)}
          placeholder="Target role (optional) — e.g. Backend Engineer"
          className="flex-1 rounded-md border border-line bg-white px-3 py-2.5 font-body text-sm text-ink outline-none focus:border-verdigris"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="rounded-md bg-ink px-5 py-2.5 font-body text-sm font-medium text-paper transition hover:bg-verdigris disabled:opacity-60"
        >
          {isLoading ? "Generating…" : "Generate suggestions"}
        </button>
      </form>

      {error && (
        <p role="alert" className="mt-4 rounded-md bg-clay-soft px-3 py-2 font-body text-sm text-clay">
          {error}
        </p>
      )}

      {suggestion && (
        <div className="mt-10 grid gap-8 md:grid-cols-[auto_1fr]">
          <div className="flex flex-col items-center gap-2 md:items-start">
            <ScoreGauge score={suggestion.result.resume_readiness_score} />
            <p className="max-w-[160px] text-center font-body text-xs text-ink-soft md:text-left">
              Resume readiness
            </p>
          </div>

          <div className="space-y-8">
            <section>
              <p className="font-body text-sm text-ink-soft">{suggestion.result.readiness_summary}</p>
            </section>

            <section>
              <h2 className="font-display text-lg font-semibold text-ink">Suitable roles</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {suggestion.result.suitable_roles.map((role) => (
                  <span
                    key={role}
                    className="rounded-full bg-verdigris-soft px-3 py-1 font-body text-sm text-verdigris"
                  >
                    {role}
                  </span>
                ))}
              </div>
            </section>

            <section>
              <h2 className="font-display text-lg font-semibold text-ink">Technologies to add</h2>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {suggestion.result.missing_technologies.map((tech) => (
                  <span
                    key={tech}
                    className="rounded-md bg-clay-soft px-2.5 py-1 font-mono text-xs text-clay"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </section>

            <section>
              <h2 className="font-display text-lg font-semibold text-ink">Learning roadmap</h2>
              <ol className="mt-3 space-y-3">
                {suggestion.result.learning_roadmap.map((step, i) => (
                  <li key={i} className="flex gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-ink font-mono text-xs text-paper">
                      {i + 1}
                    </span>
                    <div>
                      <p className="font-body text-sm font-medium text-ink">{step.skill}</p>
                      <p className="font-body text-sm text-ink-soft">{step.reason}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </section>
          </div>
        </div>
      )}
    </AppShell>
  );
}
