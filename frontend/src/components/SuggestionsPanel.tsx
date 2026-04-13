export function SuggestionsPanel({ suggestions }: { suggestions: string[] }) {
  return (
    <section className="content-card">
      <div className="card-header">
        <h3>补充建议</h3>
      </div>
      <div className="suggestion-list">
        {suggestions.length === 0 ? (
          <p className="muted-copy">当前没有额外建议。</p>
        ) : (
          suggestions.map((item, index) => (
            <div className="suggestion-item" key={`${item}-${index}`}>
              <span>{index + 1}</span>
              <p>{item}</p>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

