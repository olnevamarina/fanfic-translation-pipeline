// Запросы идут на тот же адрес, откуда открыт сайт, по пути /api:
// - в разработке их перенаправляет прокси Vite (см. vite.config.js),
// - в Docker/на Render сайт и API живут в одном сервере.
const API_URL = import.meta.env.VITE_API_URL ?? "/api";

export async function fetchWorks(signal) {
  const res = await fetch(`${API_URL}/works`, { signal });
  if (!res.ok) throw new Error(`Ошибка сервера: ${res.status}`);
  return res.json();
}
export async function fetchWork(workId, signal) {
  const res = await fetch(`${API_URL}/works/${workId}`, { signal });
  if (!res.ok) throw new Error(`Ошибка сервера: ${res.status}`);
  return res.json();
}

export async function fetchChapters(workId, signal) {
  const res = await fetch(`${API_URL}/works/${workId}/chapters`, { signal });
  if (!res.ok) throw new Error(`Ошибка сервера: ${res.status}`);
  return res.json();
}