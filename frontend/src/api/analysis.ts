import type { CreateJobResponse, JobStatusResponse } from "../types/coverage";

export interface CreateAnalysisPayload {
  prdFile: File;
  testCaseFile: File;
  sheetName?: string;
  generateMissingCases: boolean;
}

export async function createAnalysisJob(payload: CreateAnalysisPayload): Promise<CreateJobResponse> {
  const formData = new FormData();
  formData.append("prd_file", payload.prdFile);
  formData.append("test_case_file", payload.testCaseFile);
  if (payload.sheetName) {
    formData.append("sheet_name", payload.sheetName);
  }
  formData.append("generate_missing_cases", String(payload.generateMissingCases));

  const response = await fetch("/api/analysis/jobs", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseErrorResponse(response, "创建分析任务失败。"));
  }

  return response.json();
}

export async function getAnalysisJob(taskId: string): Promise<JobStatusResponse> {
  const response = await fetch(`/api/analysis/jobs/${taskId}`);
  if (!response.ok) {
    throw new Error(await parseErrorResponse(response, "获取分析任务失败。"));
  }
  return response.json();
}

async function parseErrorResponse(response: Response, fallback: string): Promise<string> {
  try {
    const payload = await response.json();
    if (typeof payload?.detail === "string") {
      return payload.detail;
    }
  } catch {
    return fallback;
  }
  return fallback;
}
