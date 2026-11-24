import Placeholder from "./Placeholder";
import "./WorkItem.css";

export default function WorkItem({ work, onSelectWork }) {
  const handleOpen = (e) => {
    if (!onSelectWork) return;
    e.preventDefault();
    onSelectWork(work);
  };

  return (
    <article className="work-item">
      <div>
        <h3 className="work-item-title">
          <a href={`#work-${work.id}`} onClick={handleOpen}>
            {work.title}
          </a>
        </h3>

        {Array.isArray(work.tags) && work.tags.length > 0 && (
          <ul className="work-tags">
            {work.tags.map((tag, index) => {
              const label = typeof tag === "string" ? tag : tag.name;
              const key =
                typeof tag === "object" && tag !== null && tag.id != null
                  ? tag.id
                  : `${label}-${index}`;
              return (
                <li key={key} className="work-tag">
                  {label}
                </li>
              );
            })}
          </ul>
        )}

        <p className="work-item-description">
          {work.description || "Описания пока нет."}
        </p>
      </div>

      {/* Когда в API появится обложка, замените на <img src={work.cover_url} alt="" /> */}
      <Placeholder label="обложка" className="work-item-cover" />
    </article>
  );
}