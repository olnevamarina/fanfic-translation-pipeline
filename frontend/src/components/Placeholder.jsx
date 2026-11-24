import "./Placeholder.css";

// Заглушка вместо картинки. Когда будет картинка, замените <Placeholder ... />
// на <img src="..." alt="..." />.
// className - необязательный аргумент: позволяет задать размер снаружи.
export default function Placeholder({ label, className = "" }) {
  return (
    <div className={`placeholder ${className}`} aria-hidden="true">
      <span>{label}</span>
    </div>
  );
}
