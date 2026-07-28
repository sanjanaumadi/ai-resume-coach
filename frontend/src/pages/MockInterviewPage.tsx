import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { isAxiosError } from "axios";
import { AppShell } from "../components/AppShell";
import { interviewApi } from "../lib/endpoints";
import type { ApiError, InterviewSession } from "../types";

const CATEGORY_LABELS: Record<string, string> = {
  hr: "HR",
  technical: "Technical",
  behavioral: "Behavioral",
  resume_specific: "About your resume",
};

export function MockInterviewPage() {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleStart() {
    if (!resumeId) return;
    setError(null);
    setIsLoading(true);
    try {
      const { data } = await interviewApi.start(resumeId);
      setSession(data);
    } catch (err) {
      setError(extractError(err));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSubmitAnswer() {
    if (!session || !currentAnswer.trim()) return;
    const nextQuestion = session.questions[session.answers.length];
    if (!nextQuestion) return;

    setError(null);
    setIsLoading(true);
    try {
      const { data } = await interviewApi.submitAnswer(session.id, nextQuestion.id, currentAnswer.trim());
      setSession(data);
      setCurrentAnswer("");
    } catch (err) {
      setError(extractError(err));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleFinish() {
    if (!session) return;
    setError(null);
    setIsLoading(true);
    try {
      const { data } = await interviewApi.finish(session.id);
      setSession(data);
    } catch (err) {
      setError(extractError(err));
    } finally {
      setIsLoading(false);
    }
  }

  const currentQuestion = session ? session.questions[session.answers.length] : null;
  const isComplete = session?.status === "completed";
  const allAnswered = session ? session.answers.length === session.questions.length : false;

  return (
    <AppShell>
      <Link to="/dashboard" className="font-body text-sm text-ink-soft hover:text-verdigris">
        ← Back to dashboard
      </Link>

      <h1 className="mt-3 font-display text-2xl font-semibold text-ink">Mock Interview</h1>

      {!session && (
        <div className="mt-8 rounded-lg border border-dashed border-line py-16 text-center">
          <p className="font-display text-lg text-ink">Ready to practice?</p>
          <p className="mt-1 font-body text-sm text-ink-soft">
            We'll generate questions based on your resume - HR, technical, behavioral, and
            resume-specific.
          </p>
          <button
            onClick={handleStart}
            disabled={isLoading}
            className="mt-5 rounded-md bg-ink px-5 py-2.5 font-body text-sm font-medium text-paper transition hover:bg-verdigris disabled:opacity-60"
          >
            {isLoading ? "Generating questions…" : "Start mock interview"}
          </button>
        </div>
      )}

      {error && (
        <p role="alert" className="mt-4 rounded-md bg-clay-soft px-3 py-2 font-body text-sm text-clay">
          {error}
        </p>
      )}

      {session && !isComplete && (
        <div className="mt-8 space-y-6">
          <p className="font-mono text-xs uppercase tracking-wider text-ink-soft">
            Question {session.answers.length + 1} of {session.questions.length}
          </p>

          {/* Answered questions with feedback, most recent first */}
          {[...session.answers].reverse().map((a) => {
            const q = session.questions.find((q) => q.id === a.question_id);
            return (
              <div key={a.question_id} className="rounded-lg border border-line bg-white p-5">
                <p className="font-mono text-[10px] uppercase tracking-wider text-verdigris">
                  {q ? CATEGORY_LABELS[q.category] : ""}
                </p>
                <p className="mt-1 font-body text-sm font-medium text-ink">{q?.question}</p>
                <p className="mt-3 font-body text-sm text-ink-soft italic">"{a.answer}"</p>
                <div className="mt-3 flex gap-4 font-mono text-xs text-ink-soft">
                  <span>Communication: {a.communication_score}</span>
                  <span>Technical: {a.technical_accuracy_score}</span>
                  <span>Relevance: {a.relevance_score}</span>
                </div>
                <p className="mt-2 font-body text-sm text-ink">{a.feedback}</p>
                <p className="mt-1 font-body text-sm text-verdigris">→ {a.suggested_improvement}</p>
              </div>
            );
          })}

          {currentQuestion && (
            <div className="rounded-lg border-2 border-verdigris bg-verdigris-soft p-5">
              <p className="font-mono text-[10px] uppercase tracking-wider text-verdigris">
                {CATEGORY_LABELS[currentQuestion.category]}
              </p>
              <p className="mt-1 font-display text-lg text-ink">{currentQuestion.question}</p>
              <textarea
                value={currentAnswer}
                onChange={(e) => setCurrentAnswer(e.target.value)}
                rows={4}
                placeholder="Type your answer as you would say it out loud…"
                className="mt-3 w-full rounded-md border border-line bg-white px-3 py-2.5 font-body text-sm text-ink outline-none focus:border-verdigris"
              />
              <button
                onClick={handleSubmitAnswer}
                disabled={isLoading || !currentAnswer.trim()}
                className="mt-3 rounded-md bg-ink px-5 py-2.5 font-body text-sm font-medium text-paper transition hover:bg-verdigris disabled:opacity-60"
              >
                {isLoading ? "Evaluating…" : "Submit answer"}
              </button>
            </div>
          )}

          {allAnswered && (
            <button
              onClick={handleFinish}
              disabled={isLoading}
              className="rounded-md bg-verdigris px-5 py-2.5 font-body text-sm font-medium text-paper transition hover:opacity-90 disabled:opacity-60"
            >
              {isLoading ? "Finishing…" : "Finish interview & see report"}
            </button>
          )}
        </div>
      )}

      {session && isComplete && session.final_report && (
        <div className="mt-8">
          <div className="rounded-lg border border-line bg-white p-6 text-center">
            <p className="font-mono text-xs uppercase tracking-wider text-ink-soft">Overall score</p>
            <p className="mt-1 font-display text-5xl font-semibold text-ink">
              {session.final_report.overall_score}
            </p>
            <div className="mt-4 flex justify-center gap-6 font-mono text-sm text-ink-soft">
              <span>Communication: {session.final_report.avg_communication_score}</span>
              <span>Technical: {session.final_report.avg_technical_accuracy_score}</span>
              <span>Relevance: {session.final_report.avg_relevance_score}</span>
            </div>
          </div>

          <button
            onClick={() => navigate("/dashboard")}
            className="mt-6 rounded-md border border-line px-5 py-2.5 font-body text-sm text-ink transition hover:border-verdigris hover:text-verdigris"
          >
            Back to dashboard
          </button>
        </div>
      )}
    </AppShell>
  );
}

function extractError(err: unknown): string {
  return isAxiosError<ApiError>(err)
    ? err.response?.data?.detail ?? "Something went wrong. Please try again."
    : "Something went wrong. Please try again.";
}
