export default function WorkCard({ work }) {
  return (
    <article className="card">
      <h2 className="card-title">{work.title}</h2>
      {/* white-space: pre-line в CSS сохраняет абзацы из описания */}
      <p className="card-description">{work.description || "Описания пока нет."}</p>
      {work.tags.length > 0 && (
        <ul className="tags">
          {work.tags.map((tag) => (
            <li key={tag} className="tag">{tag}</li>
          ))}
        </ul>
      )}
    </article>
  );
}
