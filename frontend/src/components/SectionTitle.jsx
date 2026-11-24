import { Flower2 } from "lucide-react";

// Заголовок раздела с цветком (в макете это иконка-цветок; потом можно заменить на свою)
export default function SectionTitle({ id, children }) {
  return (
    <h2 className="section-title" id={id}>
      <Flower2 size={26} aria-hidden="true" />
      {children}
    </h2>
  );
}
