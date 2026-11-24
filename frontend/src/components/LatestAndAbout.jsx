import "./LatestAndAbout.css";

function getLatestWork(works) {
  if (!Array.isArray(works) || works.length === 0) return null;

  return [...works].sort((a, b) => {
    if (a.created_at && b.created_at) {
      return new Date(b.created_at) - new Date(a.created_at);
    }
    return (b.id ?? 0) - (a.id ?? 0);
  })[0];
}

export default function LatestAndAbout({ works = [], onSelectWork }) {
  const latestWork = getLatestWork(works);

  return (
    <section className="featured-split" aria-label="Последнее обновление и информация о сайте">
      {/* Левая большая плашка: Последнее обновление */}
      <div className="panel panel--latest">
        <div className="panel__header">
          <h2 className="panel__tLatestAndAbout.jsxitle">Последнее обновление</h2>
        </div>

        {latestWork ? (
          <article
            className="latest-card"
            onClick={() => onSelectWork && onSelectWork(latestWork)}
          >
            {latestWork.cover_url && (
              <div className="latest-card__cover-wrap">
                <img
                  src={latestWork.cover_url}
                  alt={latestWork.title}
                  className="latest-card__cover"
                />
              </div>
            )}

            <div className="latest-card__body">
              <h3 className="latest-card__title">{latestWork.title}</h3>
              {latestWork.summary && (
                <p className="latest-card__summary">{latestWork.summary}</p>
              )}
            </div>
          </article>
        ) : (
          <p className="panel__empty">Работ пока нет.</p>
        )}
      </div>

      {/* Правая плашка: О сайте */}
      <aside className="panel panel--about">
        <div className="panel__header">
          <h2 className="panel__title">О сайте</h2>
        </div>

        <p className="about-card__text">
          Тут вы можете прочитать мои фанфики и переводы, в том числе с ИИ-переводом.
        </p>
      </aside>
    </section>
  );
}