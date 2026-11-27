import { useState, useRef, useCallback, useEffect } from "react";
import { generatePrompt, translateChapter } from "../api";

export function useTranslation(workId, chapters) {
  const [status, setStatus] = useState("idle"); // idle | loading | ready | error
  const [progress, setProgress] = useState({ done: 0, total: 0 });
  const [translations, setTranslations] = useState({}); // { chapterId: text }
  const [error, setError] = useState("");
  const abortRef = useRef(null);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setStatus("idle");
    setTranslations({});
    setError("");
  }, []);

  useEffect(() => () => abortRef.current?.abort(), []);

  const start = useCallback(
    async (language) => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setStatus("loading");
      setError("");
      setTranslations({});
      setProgress({ done: 0, total: chapters.length });

      try {
        await generatePrompt(workId, language, controller.signal);

        const result = {};
        for (const ch of chapters) {
          const r = await translateChapter(ch.id, language, controller.signal);
          result[ch.id] = r.text;
          setProgress((p) => ({ ...p, done: p.done + 1 }));
        }
        setTranslations(result);
        setStatus("ready");
      } catch (e) {
        if (e.name === "AbortError") return;
        setError(e.message);
        setStatus("error");
      }
    },
    [workId, chapters]
  );

  return { status, progress, translations, error, start, reset };
}