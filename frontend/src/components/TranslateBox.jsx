const FANDOM_LANGUAGES = [
  "English", "Spanish", "Portuguese", "Russian", "French", "German", "Italian",
  "Polish", "Ukrainian", "Dutch", "Swedish", "Czech", "Romanian", "Greek",
  "Hungarian", "Finnish", "Danish", "Norwegian", "Bulgarian", "Serbian",
  "Croatian", "Slovak", "Catalan", "Chinese (Simplified)", "Chinese (Traditional)",
  "Japanese", "Korean", "Indonesian", "Thai", "Vietnamese", "Tagalog", "Arabic",
  "Turkish", "Persian", "Hebrew",
];

export default function TranslateBox({
  t,
  language,
  setLanguage,
  showTranslation,
  setShowTranslation,
}) {
  const { status, progress, error, start, reset } = t;

  if (status === "loading") {
    return (
      <div className="translate-box">
        <p className="translate-box__label">Ожидайте…</p>
        <p className="translate-box__notice">
          Переведено глав: {progress.done} из {progress.total}
        </p>
        <button className="translate-box__btn" onClick={reset}>
          Отмена
        </button>
      </div>
    );
  }

  if (status === "ready") {
    return (
      <div className="translate-box">
        <p className="translate-box__label">Перевод готов</p>
        <button
          className="translate-box__btn"
          onClick={() => setShowTranslation((v) => !v)}
        >
          {showTranslation ? "Показать оригинал" : "Показать перевод"}
        </button>
        <button
          className="translate-box__btn"
          onClick={() => {
            setShowTranslation(false);
            reset();
          }}
        >
          Другой язык
        </button>
      </div>
    );
  }

  // idle или error: выбор языка
  return (
    <div className="translate-box">
      <label className="translate-box__label">Язык перевода</label>
      <select
        className="translate-box__select"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
      >
        <option value="">Выберите язык</option>
        {FANDOM_LANGUAGES.map((lang) => (
          <option key={lang} value={lang}>
            {lang}
          </option>
        ))}
      </select>
      <button
        className="translate-box__btn"
        disabled={!language}
        onClick={() => start(language)}
      >
        Перевести
      </button>
      {status === "error" && <p className="translate-box__notice">{error}</p>}
    </div>
  );
}