import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import type { ApiError } from "../types";
import { isAxiosError } from "axios";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      const message = isAxiosError<ApiError>(err)
        ? err.response?.data?.detail ?? "Something went wrong. Please try again."
        : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-paper px-6">
      <div className="w-full max-w-sm">
        <h1 className="font-display text-3xl font-semibold text-ink">Welcome back</h1>
        <p className="mt-2 font-body text-sm text-ink-soft">Log in to keep working on your resume.</p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div>
            <label htmlFor="email" className="mb-1.5 block font-body text-sm font-medium text-ink">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border border-line bg-white px-3 py-2 font-body text-ink outline-none focus:border-verdigris"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label htmlFor="password" className="mb-1.5 block font-body text-sm font-medium text-ink">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-line bg-white px-3 py-2 font-body text-ink outline-none focus:border-verdigris"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <p role="alert" className="rounded-md bg-clay-soft px-3 py-2 font-body text-sm text-clay">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-md bg-ink py-2.5 font-body text-sm font-medium text-paper transition hover:bg-verdigris disabled:opacity-60"
          >
            {isSubmitting ? "Logging in…" : "Log in"}
          </button>
        </form>

        <p className="mt-6 text-center font-body text-sm text-ink-soft">
          Don't have an account?{" "}
          <Link to="/register" className="font-medium text-verdigris hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
