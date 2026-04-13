import type { RequirementPoint } from "../types/coverage";

interface CoverageListsProps {
  coveredPoints: RequirementPoint[];
  missingPoints: RequirementPoint[];
}

function PointList({ title, points }: { title: string; points: RequirementPoint[] }) {
  return (
    <article className="content-card">
      <div className="card-header">
        <h3>{title}</h3>
        <span>{points.length}</span>
      </div>
      <div className="point-list">
        {points.length === 0 ? (
          <p className="muted-copy">暂无数据</p>
        ) : (
          points.map((point) => (
            <div key={point.id} className="point-item">
              <div className="point-chip">
                <span>{point.id}</span>
                <span>{point.type}</span>
              </div>
              <strong>{point.description}</strong>
              <p>{point.module}</p>
              <small>{point.source_text}</small>
            </div>
          ))
        )}
      </div>
    </article>
  );
}

export function CoverageLists({ coveredPoints, missingPoints }: CoverageListsProps) {
  return (
    <section className="dual-column">
      <PointList title="已覆盖需求点" points={coveredPoints} />
      <PointList title="未覆盖需求点" points={missingPoints} />
    </section>
  );
}

