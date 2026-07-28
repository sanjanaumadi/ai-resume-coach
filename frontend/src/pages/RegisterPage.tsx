import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { isAxiosError } from "axios";
import { useAuth } from "../context/AuthContext";
import type { ApiError } from "../types";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await register(email, fullName, password);
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
        <h1 className="font-display text-3xl font-semibold text-ink">Create your account</h1>
        <p className="mt-2 font-body text-sm text-ink-soft">Start improving your resume today.</p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div>
            <label htmlFor="fullName" className="mb-1.5 block font-body text-sm font-medium text-ink">
              Full name
            </label>
            <input
              id="fullName"
              type="text"
              required
              minLength={2}
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-md border border-line bg-white px-3 py-2 font-body text-ink outline-none focus:border-verdigris"
              placeholder="Jane Doe"
            />
          </div>
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
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-line bg-white px-3 py-2 font-body text-ink outline-none focus:border-verdigris"
              placeholder="At least 8 characters"
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
            {isSubmitting ? "Creating account…" : "Sign up"}
          </button>
        </form>

        <p className="mt-6 text-center font-body text-sm text-ink-soft">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-verdigris hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
