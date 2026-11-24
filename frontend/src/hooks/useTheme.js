import { useEffect, useState } from "react";

const KEY = "theme";

function initialTheme() {
  try {
    const saved = localStorage.getItem(KEY);
    if (saved === "light" || saved === "dark") return saved;
  } catch {
    // localStorage может быть недоступен: тогда просто берём тему по умолчанию
  }
  return "light"; // по умолчанию светлая, как в макете
}

export default function useTheme() {
  const [theme, setTheme] = useState(initialTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme; // CSS смотрит на этот атрибут
    try {
      localStorage.setItem(KEY, theme);
    } catch {
      // не страшно
    }
  }, [theme]);

  return [theme, setTheme];
}
