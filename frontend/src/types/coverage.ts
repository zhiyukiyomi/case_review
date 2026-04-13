export interface RequirementPoint {
  id: string;
  module: string;
  type: string;
  description: string;
  priority: string;
  source_text: string;
}

export interface TestCase {
  case_id: string;
  title: string;
  preconditions: string;
  steps: string;
  expected_result: string;
  tags: string[];
}

export interface DimensionScore {
  score: number;
  full_score: number;
  reason: string;
}

export interface CoverageResult {
  score: number;
  level: string;
  dimension_scores: Record<string, DimensionScore>;
  covered_points: RequirementPoint[];
  missing_points: RequirementPoint[];
  suggestions: string[];
  generated_cases: TestCase[];
  markdown_report: string;
  requirement_points: RequirementPoint[];
  test_cases: TestCase[];
  metadata?: Record<string, string | null>;
}

export interface CreateJobResponse {
  task_id: string;
  status: string;
}

export interface JobStatusResponse {
  task_id: string;
  status: "queued" | "running" | "completed" | "failed";
  result: CoverageResult | null;
  error: string | null;
  created_at: string;
  updated_at: string;
}

