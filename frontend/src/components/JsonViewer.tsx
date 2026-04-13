export function JsonViewer({ payload }: { payload: unknown }) {
  return (
    <section className="content-card">
      <div className="card-header">
        <h3>结构化 JSON</h3>
      </div>
      <pre className="json-viewer">{JSON.stringify(payload, null, 2)}</pre>
    </section>
  );
}

