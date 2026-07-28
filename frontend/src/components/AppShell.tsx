import type { ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-paper">
      <header className="border-b border-line">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link to="/dashboard" className="font-display text-xl font-semibold tracking-tight text-ink">
            Resume Coach
          </Link>
          <nav className="flex items-center gap-6 font-body text-sm">
            <Link to="/dashboard" className="text-ink-soft transition hover:text-ink">
              Dashboard
            </Link>
            <span className="text-ink-soft">{user?.full_name}</span>
            <button
              onClick={handleLogout}
              className="rounded-md border border-line px-3 py-1.5 text-ink-soft transition hover:border-clay hover:text-clay"
            >
              Log out
            </button>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
    </div>
  );
}
