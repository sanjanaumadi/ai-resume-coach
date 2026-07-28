import { api } from "./api";
import type { Analysis, CareerSuggestion, InterviewSession, Rewrite, ResumeDetail, TokenResponse, User } from "../types";

export const authApi = {
  register: (email: string, full_name: string, password: string) =>
    api.post<TokenResponse>("/auth/register", { email, full_name, password }),

  login: (email: string, password: string) =>
    api.post<TokenResponse>("/auth/login", { email, password }),

  me: () => api.get<User>("/auth/me"),
};

export const resumeApi = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<ResumeDetail>("/resumes/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  list: () => api.get<{ resumes: ResumeDetail[]; total: number }>("/resumes"),

  get: (id: string) => api.get<ResumeDetail>(`/resumes/${id}`),
};

export const analysisApi = {
  run: (resume_id: string, job_description?: string) =>
    api.post<Analysis>("/analysis", { resume_id, job_description: job_description || null }),

  list: () => api.get<{ analyses: Analysis[]; total: number }>("/analysis"),

  get: (id: string) => api.get<Analysis>(`/analysis/${id}`),
};

export const rewriteApi = {
  run: (resume_id: string, section: "summary" | "bullets" | "skills", text: string, job_description?: string) =>
    api.post<Rewrite>("/rewrite", { resume_id, section, text, job_description: job_description || null }),

  list: () => api.get<{ rewrites: Rewrite[]; total: number }>("/rewrite"),
};

export const interviewApi = {
  start: (resume_id: string, job_description?: string) =>
    api.post<InterviewSession>("/interview", { resume_id, job_description: job_description || null }),

  submitAnswer: (sessionId: string, question_id: string, answer: string) =>
    api.post<InterviewSession>(`/interview/${sessionId}/answer`, { question_id, answer }),

  finish: (sessionId: string) => api.post<InterviewSession>(`/interview/${sessionId}/finish`),

  list: () => api.get<{ sessions: InterviewSession[]; total: number }>("/interview"),

  get: (sessionId: string) => api.get<InterviewSession>(`/interview/${sessionId}`),
};

export const careerSuggestionApi = {
  generate: (resume_id: string, target_role?: string) =>
    api.post<CareerSuggestion>("/career-suggestions", { resume_id, target_role: target_role || null }),

  list: () => api.get<{ suggestions: CareerSuggestion[]; total: number }>("/career-suggestions"),
};
