import type { CoverageResult } from "../types/coverage";


export function ScorePanel({ result }: { result: CoverageResult }) {
  return (
    <section className="score-panel">
      <div>
        <p className="section-kicker">综合评分</p>
        <h2>{result.score}</h2>
        <p className="section-subtitle">{result.level}</p>
      </div>
      <div className="score-aside">
        <div>
          <span>需求点</span>
          <strong>{result.requirement_points.length}</strong>
        </div>
        <div>
          <span>已覆盖</span>
          <strong>{result.covered_points.length}</strong>
        </div>
        <div>
          <span>缺失点</span>
          <strong>{result.missing_points.length}</strong>
        </div>
      </div>
    </section>
  );
}

