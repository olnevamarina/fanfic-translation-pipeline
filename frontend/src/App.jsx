import { Flower2 } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchWorks } from "./api";
import Header from "./components/Header";
import Hero from "./components/Hero";
import LatestAndAbout from "./components/LatestAndAbout";
import WorkList from "./components/WorkList";
import WorkPage from "./components/WorkPage";
import useTheme from "./hooks/useTheme";
import "./App.css";

// App - КОРНЕВОЙ компонент: страница целиком. Он собирает блоки и держит главные данные.
export default function App() {
  // ---------- СОСТОЯНИЕ (state) ----------
  const [theme, setTheme] = useTheme();               // "light" или "dark"
  const [works, setWorks] = useState([]);             // список работ с сервера
  const [status, setStatus] = useState("loading");    // "loading" | "ready" | "error"
  const [selectedWork, setSelectedWork] = useState(null); // открытая работа или null (главная)

  // ---------- ЗАГРУЗКА ДАННЫХ (effect) ----------
  useEffect(() => {
    const controller = new AbortController();
    fetchWorks(controller.signal)
      .then((data) => {
        setWorks(data);
        setStatus("ready");
      })
      .catch((err) => {
        if (err.name !== "AbortError") setStatus("error");
      });
    return () => controller.abort();
  }, []);

  // Сначала самые новые. [...works] делает копию: state нельзя менять напрямую.
  const newestFirst = [...works].reverse();

  const handleSelectWork = (work) => {
    setSelectedWork(work);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleBackToList = () => {
    setSelectedWork(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // ---------- ЧТО НАРИСОВАТЬ (JSX) ----------
  return (
    <>
      <Header theme={theme} onThemeChange={setTheme} />

      {selectedWork ? (
        <WorkPage
          workId={selectedWork.id}
          initialWork={selectedWork}
          onBack={handleBackToList}
        />
      ) : (
        <>
          <Hero />
          <LatestAndAbout
            works={works}
            onSelectWork={handleSelectWork}
          />
          <main className="page">
            <h2 className="section-title">
              <Flower2 size={26} aria-hidden="true" />
              Новые работы
            </h2>

            {status === "loading" && <p className="message">Загружаем работы…</p>}
            {status === "error" && (
              <p className="message message-error">
                Не удалось загрузить работы. Проверьте, что сервер запущен, и обновите страницу.
              </p>
            )}
            {status === "ready" && newestFirst.length === 0 && (
              <p className="message">Здесь пока нет работ.</p>
            )}
            {status === "ready" && newestFirst.length > 0 && (
              <WorkList works={newestFirst} onSelectWork={handleSelectWork} />
            )}
          </main>
        </>
      )}
    </>
  );
}