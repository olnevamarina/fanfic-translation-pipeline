import { useEffect, useState } from "react";
import { fetchChapters, fetchWork } from "../api";
import "./WorkPage.css";
import TranslateBox from "./TranslateBox";
import { useTranslation } from "../hooks/useTranslation";

const FANDOM_LANGUAGES = [
  "English",
  "Spanish",
  "Portuguese",
  "Russian",
  "French",
  "German",
  "Italian",
  "Polish",
  "Ukrainian",
  "Dutch",
  "Swedish",
  "Czech",
  "Romanian",
  "Greek",
  "Hungarian",
  "Finnish",
  "Danish",
  "Norwegian",
  "Bulgarian",
  "Serbian",
  "Croatian",
  "Slovak",
  "Catalan",
  "Chinese (Simplified)",
  "Chinese (Traditional)",
  "Japanese",
  "Korean",
  "Indonesian",
  "Thai",
  "Vietnamese",
  "Tagalog",
  "Arabic",
  "Turkish",
  "Persian",
  "Hebrew",
];

function formatDate(isoString) {
  if (!isoString) return "";
  return new Date(isoString).toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}


export default function WorkPage({ workId, initialWork = null, onBack }) {
  const [work, setWork] = useState(initialWork);
  const [chapters, setChapters] = useState([]);
  const [activeNumber, setActiveNumber] = useState(null);
  const [loading, setLoading] = useState(!initialWork);
  const [error, setError] = useState("");


  const [language, setLanguage] = useState("");
  const [showTranslation, setShowTranslation] = useState(false);
  const t = useTranslation(workId, chapters);

  useEffect(() => {
    const controller = new AbortController();
    setError("");
    if (!initialWork || initialWork.id !== workId) {
      setLoading(true);
    }

    Promise.all([
      fetchWork(workId, controller.signal),
      fetchChapters(workId, controller.signal),
    ])
      .then(([workData, chaptersData]) => {
        setWork(workData);
        setChapters(chaptersData);
        if (chaptersData.length > 0) {
          setActiveNumber((prev) =>
            chaptersData.some((c) => c.number === prev) ? prev : chaptersData[0].number
          );
        } else {
          setActiveNumber(null);
        }
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(err.message || "Не удалось загрузить работу");
        }
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [workId]);

  const currentChapter =
    chapters.find((ch) => ch.number === activeNumber) || chapters[0] || null;

  const displayText =
    showTranslation && currentChapter && t.translations[currentChapter.id]
      ? t.translations[currentChapter.id]
      : currentChapter?.text ?? "";
  return (
    <article className="work-page">
      <div className="work-page__topbar">
        <button type="button" className="work-page__back" onClick={onBack}>
          ← Назад ко всем работам
        </button>
      </div>

      {loading && !work && <p className="message">Загрузка работы...</p>}
      {error && <p className="message message-error">{error}</p>}

      {work && (
        <div className="work-layout">
          <div className="work-layout__main">
            {/* Шапка работы + облако тегов */}
            <header className="work-header">
              <div className="work-header__meta">
                {work.age_rating === "18+" && (
                  <span className="work-badge work-badge--rating">18+</span>
                )}
                {work.status && (
                  <span className="work-badge work-badge--status">{work.status}</span>
                )}
                {work.last_updated_at && (
                  <span className="work-meta-date">
                    Обновлено: {formatDate(work.last_updated_at)}
                  </span>
                )}
              </div>

              <h1 className="work-header__title">{work.title}</h1>

              {Array.isArray(work.tags) && work.tags.length > 0 && (
                <div className="work-tags-cloud" aria-label="Теги">
                  {work.tags.map((tag, idx) => {
                    const label = typeof tag === "string" ? tag : tag.name;
                    const key =
                      typeof tag === "object" && tag !== null && tag.id != null
                        ? tag.id
                        : `${label}-${idx}`;
                    return (
                      <span key={key} className="work-tags-cloud__item">
                        {label}
                      </span>
                    );
                  })}
                </div>
              )}

              {work.description && (
                <p className="work-header__description">{work.description}</p>
              )}
            </header>

            {/* Переключатель глав и сам текст */}
            <section className="work-body" aria-label="Текст работы">
              {chapters.length > 1 && (
                <div className="chapter-nav">
                  {chapters.map((ch) => (
                    <button
                      key={ch.id}
                      type="button"
                      className={`chapter-nav__btn ${
                        currentChapter?.number === ch.number ? "is-active" : ""
                      }`}
                      onClick={() => setActiveNumber(ch.number)}
                    >
                      Глава {ch.number}
                      {ch.title ? `: ${ch.title}` : ""}
                    </button>
                  ))}
                </div>
              )}

              {currentChapter ? (
                <div className="chapter-content">
                  <h2 className="chapter-content__title">
                    Глава {currentChapter.number}
                    {currentChapter.title ? ` — ${currentChapter.title}` : ""}
                  </h2>
                  <div className="chapter-content__text">
                    {displayText.split("\n").map((paragraph, i) =>
                      paragraph.trim() ? <p key={i}>{paragraph}</p> : null
                    )}
                  </div>
                </div>
              ) : (
                <p className="message">Глав пока нет.</p>
              )}
            </section>
          </div>

          {/* Боковая панель перевода */}
          <aside className="work-sidebar">
            <TranslateBox
              t={t}
              language={language}
              setLanguage={setLanguage}
              showTranslation={showTranslation}
              setShowTranslation={setShowTranslation}
            />
          </aside>
        </div>
      )}
    </article>
  );
}