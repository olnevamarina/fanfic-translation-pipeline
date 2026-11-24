import Placeholder from "./Placeholder";
import "./Hero.css";

export default function Hero() {
  return (
    <section className="hero" aria-label="Приветствие">
      <div className="hero-inner">

        {/* Центральный блок из макета: баннер или видео */}
        <Placeholder label="баннер / видео" className="hero-banner" />
        {/* Декоративная вертикальная надпись, скрыта от скринридеров */}
      </div>
    </section>
  );
}
