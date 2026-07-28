export interface User {
  id: string;
  email: string;
  full_name: string;
  auth_provider: string;
  is_verified: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Resume {
  id: string;
  original_filename: string;
  file_type: string;
  file_size_bytes: number;
  char_count: number;
  created_at: string;
}

export interface ResumeDetail extends Resume {
  extracted_text: string;
}

export interface JDMatch {
  jd_skills_found: string[];
  missing_skills: string[];
  match_percentage: number;
  semantic_similarity: number | null;
}

export interface AnalysisResult {
  ats_score: number;
  matched_skills: string[];
  sections_found: Record<string, boolean>;
  contact_info: Record<string, boolean>;
  formatting_issues: string[];
  recommendations: string[];
  jd_match: JDMatch | null;
}

export interface Analysis {
  id: string;
  resume_id: string;
  ats_score: number;
  result: AnalysisResult;
  created_at: string;
}

export interface Rewrite {
  id: string;
  resume_id: string;
  section: "summary" | "bullets" | "skills";
  original_text: string;
  rewritten_text: string;
  created_at: string;
}

export interface InterviewQuestion {
  id: string;
  category: "hr" | "technical" | "behavioral" | "resume_specific";
  question: string;
}

export interface InterviewAnswerFeedback {
  question_id: string;
  answer: string;
  communication_score: number;
  technical_accuracy_score: number;
  relevance_score: number;
  feedback: string;
  suggested_improvement: string;
}

export interface InterviewFinalReport {
  avg_communication_score: number;
  avg_technical_accuracy_score: number;
  avg_relevance_score: number;
  overall_score: number;
  questions_answered: number;
  questions_total: number;
}

export interface InterviewSession {
  id: string;
  resume_id: string;
  status: "in_progress" | "completed";
  questions: InterviewQuestion[];
  answers: InterviewAnswerFeedback[];
  final_report: InterviewFinalReport | null;
  created_at: string;
}

export interface LearningStep {
  skill: string;
  reason: string;
}

export interface CareerSuggestionsResult {
  suitable_roles: string[];
  missing_technologies: string[];
  learning_roadmap: LearningStep[];
  resume_readiness_score: number;
  readiness_summary: string;
}

export interface CareerSuggestion {
  id: string;
  resume_id: string;
  result: CareerSuggestionsResult;
  created_at: string;
}

export interface ApiError {
  detail: string;
}
