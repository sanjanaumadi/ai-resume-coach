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

export interface ApiError {
  detail: string;
}
