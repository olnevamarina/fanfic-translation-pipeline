import { Moon, Search, Sun } from "lucide-react";
import Placeholder from "./Placeholder";
import "./Header.css";
export default function Header({ theme, onThemeChange }) {
  return (
    <header className="header">
      <div className="header-inner">
        <a className="brand" href="/">
          <Placeholder label="лого" className="brand-logo" />
          <span className="brand-name">
            UraMayu
            <br />
            Archive
          </span>
        </a>

        <nav className="nav" aria-label="Основная навигация">
          <a className="nav-link nav-link-active" href="/" aria-current="page">Фанфики</a>
          {/* В макете здесь пустой пункт меню: переименуйте или удалите */}
          <a className="nav-link" href="#">Переводы</a>
          <a className="nav-link" href="#about">О проекте</a>
        </nav>

        {/* TODO: поиск пока ничего не делает */}
        <form className="search" role="search" onSubmit={(e) => e.preventDefault()}>
          <input type="search" placeholder="Поиск по фанфикам…" aria-label="Поиск по фанфикам" />
          <button type="submit" aria-label="Искать">
            <Search size={18} aria-hidden="true" />
          </button>
        </form>

        <div className="theme-switch" role="group" aria-label="Тема оформления">
          <button type="button" aria-label="Светлая тема" aria-pressed={theme === "light"}
                  onClick={() => onThemeChange("light")}>
            <Sun size={18} aria-hidden="true" />
          </button>
          <button type="button" aria-label="Тёмная тема" aria-pressed={theme === "dark"}
                  onClick={() => onThemeChange("dark")}>
            <Moon size={18} aria-hidden="true" />
          </button>
        </div>
      </div>
    </header>
  );
}
