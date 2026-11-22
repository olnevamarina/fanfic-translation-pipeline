import { useEffect, useState } from "react";
import { fetchWorks } from "./api";
import WorkCard from "./components/WorkCard";

export default function App() {
  const [works, setWorks] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | ready | error

  useEffect(() => {
    // AbortController отменяет запрос, если компонент исчез.
    // В режиме разработки React специально запускает эффект дважды, и это защищает от дублей.
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

  return (
    <>
      <header className="site-header">
        <h1 className="logo">Фанфики</h1>
      </header>

      <main className="wrap">
        {status === "loading" && <p className="message">Загружаем работы…</p>}

        {status === "error" && (
          <p className="message message-error">
            Не удалось загрузить работы. Проверьте, что сервер запущен, и обновите страницу.
          </p>
        )}

        {status === "ready" && works.length === 0 && (
          <p className="message">Здесь пока нет работ. Добавьте первую через /docs на сервере.</p>
        )}

        {status === "ready" && works.length > 0 && (
          <div className="grid">
            {works.map((work) => (
              <WorkCard key={work.id} work={work} />
            ))}
          </div>
        )}
      </main>
    </>
  );
}
