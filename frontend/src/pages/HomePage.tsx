import { startTransition, useDeferredValue, useEffect, useState, useTransition } from "react";
import { createAnalysisJob, getAnalysisJob } from "../api/analysis";
import { CoverageLists } from "../components/CoverageLists";
import { DimensionCards } from "../components/DimensionCards";
import { GeneratedCasesTable } from "../components/GeneratedCasesTable";
import { HeroUpload } from "../components/HeroUpload";
import { JsonViewer } from "../components/JsonViewer";
import { ScorePanel } from "../components/ScorePanel";
import { SuggestionsPanel } from "../components/SuggestionsPanel";
import type { CoverageResult } from "../types/coverage";

const statusText: Record<string, string> = {
  idle: "请选择需求文档和测试用例文件。",
  creating: "正在创建分析任务...",
  running: "正在评估，请稍候...",
  completed: "评估完成。",
  failed: "评估失败，请检查错误信息。",
};

export function HomePage() {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [result, setResult] = useState<CoverageResult | null>(null);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startUiTransition] = useTransition();
  const deferredResult = useDeferredValue(result);

  useEffect(() => {
    if (!taskId) {
      return;
    }

    const timer = window.setInterval(async () => {
      try {
        const job = await getAnalysisJob(taskId);
        setStatus(job.status);

        if (job.status === "completed" && job.result) {
          startTransition(() => {
            setResult(job.result);
            setError(null);
          });
          window.clearInterval(timer);
        }

        if (job.status === "failed") {
          setError(job.error ?? "分析失败，请检查后端日志。");
          window.clearInterval(timer);
        }
      } catch (pollError) {
        setError(pollError instanceof Error ? pollError.message : "轮询任务状态失败。");
        setStatus("failed");
        window.clearInterval(timer);
      }
    }, 2500);

    return () => window.clearInterval(timer);
  }, [taskId]);

  const handleSubmit = async (payload: {
    prdFile: File;
    testCaseFile: File;
    sheetName?: string;
    generateMissingCases: boolean;
  }) => {
    startUiTransition(() => {
      void (async () => {
        try {
          setError(null);
          setResult(null);
          setStatus("creating");
          const job = await createAnalysisJob(payload);
          setTaskId(job.task_id);
          setStatus(job.status);
        } catch (submitError) {
          setError(submitError instanceof Error ? submitError.message : "创建分析任务失败。");
          setStatus("failed");
        }
      })();
    });
  };

  return (
    <main className="page-shell compact-shell">
      <section className="center-panel">
        <HeroUpload onSubmit={handleSubmit} isPending={isPending || status === "running"} />
        <div className={`status-strip ${status === "failed" ? "status-strip-error" : ""}`}>
          <span className="status-dot" />
          <p>{error ?? statusText[status] ?? "正在处理..."}</p>
        </div>
      </section>

      {deferredResult ? (
        <section className="results-shell compact-results">
          <ScorePanel result={deferredResult} />
          <DimensionCards result={deferredResult} />
          <CoverageLists
            coveredPoints={deferredResult.covered_points}
            missingPoints={deferredResult.missing_points}
          />
          <SuggestionsPanel suggestions={deferredResult.suggestions} />
          <GeneratedCasesTable cases={deferredResult.generated_cases} />
          <section className="content-card">
            <div className="card-header">
              <h3>Markdown 报告</h3>
              {taskId ? (
                <a className="report-link" href={`/api/analysis/jobs/${taskId}/report`} target="_blank" rel="noreferrer">
                  打开原始报告
                </a>
              ) : null}
            </div>
            <pre className="json-viewer">{deferredResult.markdown_report}</pre>
          </section>
          <JsonViewer payload={deferredResult} />
        </section>
      ) : null}
    </main>
  );
}
