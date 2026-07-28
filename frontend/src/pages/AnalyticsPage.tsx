import { useEffect, useState } from "react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { AppShell } from "../components/AppShell";
import { analyticsApi } from "../lib/endpoints";
import type { AnalyticsSummary } from "../types";

const INK = "#23281F";
const VERDIGRIS = "#3D7A6C";
const LINE_COLOR = "#DDD5C2";

export function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    analyticsApi
      .getSummary()
      .then(({ data }) => setSummary(data))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <AppShell>
        <p className="font-mono text-sm text-ink-soft">Loading…</p>
      </AppShell>
    );
  }

  if (!summary) {
    return (
      <AppShell>
        <p className="font-body text-sm text-clay">Could not load analytics.</p>
      </AppShell>
    );
  }

  const hasAtsData = summary.ats_score_trend.length > 0;
  const hasInterviewData = summary.interview_score_trend.length > 0;
  const hasSkillsData = summary.skills_frequency.length > 0;

  const formattedAtsTrend = summary.ats_score_trend.map((p, i) => ({
    ...p,
    label: `#${i + 1}`,
  }));
  const formattedInterviewTrend = summary.interview_score_trend.map((p, i) => ({
    ...p,
    label: `#${i + 1}`,
  }));

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink">Analytics</h1>
      <p className="mt-1 font-body text-sm text-ink-soft">
        Your progress across resumes, analyses, and mock interviews.
      </p>

      <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-5">
        <StatCard label="Resumes" value={summary.total_resumes} />
        <StatCard label="Analyses run" value={summary.total_analyses} />
        <StatCard label="Interviews" value={summary.total_interviews} />
        <StatCard label="Latest ATS score" value={summary.latest_ats_score ?? "—"} />
        <StatCard label="Latest interview score" value={summary.latest_interview_score ?? "—"} />
      </div>

      <section className="mt-10">
        <h2 className="font-display text-lg font-semibold text-ink">ATS score over time</h2>
        {hasAtsData ? (
          <div className="mt-3 h-64 rounded-lg border border-line bg-white p-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={formattedAtsTrend}>
                <CartesianGrid stroke={LINE_COLOR} strokeDasharray="3 3" />
                <XAxis dataKey="label" stroke={INK} fontSize={12} />
                <YAxis domain={[0, 100]} stroke={INK} fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke={VERDIGRIS} strokeWidth={2} dot={{ fill: VERDIGRIS }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <EmptyChart message="Run an ATS analysis to see your score trend here." />
        )}
      </section>

      <section className="mt-10">
        <h2 className="font-display text-lg font-semibold text-ink">Mock interview scores over time</h2>
        {hasInterviewData ? (
          <div className="mt-3 h-64 rounded-lg border border-line bg-white p-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={formattedInterviewTrend}>
                <CartesianGrid stroke={LINE_COLOR} strokeDasharray="3 3" />
                <XAxis dataKey="label" stroke={INK} fontSize={12} />
                <YAxis domain={[0, 100]} stroke={INK} fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke={VERDIGRIS} strokeWidth={2} dot={{ fill: VERDIGRIS }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <EmptyChart message="Complete a mock interview to see your score trend here." />
        )}
      </section>

      <section className="mt-10">
        <h2 className="font-display text-lg font-semibold text-ink">Skills distribution</h2>
        {hasSkillsData ? (
          <div className="mt-3 h-72 rounded-lg border border-line bg-white p-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={summary.skills_frequency} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid stroke={LINE_COLOR} strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" allowDecimals={false} stroke={INK} fontSize={12} />
                <YAxis type="category" dataKey="skill" stroke={INK} fontSize={12} width={90} />
                <Tooltip />
                <Bar dataKey="count" fill={VERDIGRIS} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <EmptyChart message="Run an analysis to see which skills show up most in your resume." />
        )}
      </section>
    </AppShell>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-line bg-white px-4 py-3">
      <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">{label}</p>
      <p className="mt-1 font-display text-2xl font-semibold text-ink">{value}</p>
    </div>
  );
}

function EmptyChart({ message }: { message: string }) {
  return (
    <div className="mt-3 flex h-40 items-center justify-center rounded-lg border border-dashed border-line">
      <p className="font-body text-sm text-ink-soft">{message}</p>
    </div>
  );
}
