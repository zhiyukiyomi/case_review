import type { TestCase } from "../types/coverage";

export function GeneratedCasesTable({ cases }: { cases: TestCase[] }) {
  return (
    <section className="content-card">
      <div className="card-header">
        <h3>建议新增测试用例</h3>
        <span>{cases.length}</span>
      </div>
      <div className="table-shell">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>标题</th>
              <th>前置条件</th>
              <th>步骤</th>
              <th>预期结果</th>
              <th>标签</th>
            </tr>
          </thead>
          <tbody>
            {cases.length === 0 ? (
              <tr>
                <td colSpan={6} className="empty-row">
                  当前没有自动生成的测试用例。
                </td>
              </tr>
            ) : (
              cases.map((item) => (
                <tr key={item.case_id}>
                  <td>{item.case_id}</td>
                  <td>{item.title}</td>
                  <td>{item.preconditions || "无"}</td>
                  <td>{item.steps}</td>
                  <td>{item.expected_result}</td>
                  <td>{item.tags.join(", ") || "无"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

