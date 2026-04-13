import type { CoverageResult } from "../types/coverage";

const dimensionTitles: Record<string, string> = {
  core_function: "核心功能点覆盖",
  business_rules_and_boundaries: "业务规则与边界值",
  exception_flows: "异常场景与逆向流程",
  non_functional: "非功能需求",
};

export function DimensionCards({ result }: { result: CoverageResult }) {
  return (
    <section className="card-grid">
      {Object.entries(result.dimension_scores).map(([key, value]) => (
        <article key={key} className="glass-card">
          <p className="section-kicker">{dimensionTitles[key] ?? key}</p>
          <h3>
            {value.score} / {value.full_score}
          </h3>
          <p>{value.reason}</p>
        </article>
      ))}
    </section>
  );
}

