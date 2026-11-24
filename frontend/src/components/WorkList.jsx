import WorkItem from "./WorkItem";
import "./WorkList.css";

export default function WorkList({ works, onSelectWork }) {
  return (
    <ul className="work-list">
      {works.map((work) => (
        <li key={work.id}>
          <WorkItem work={work} onSelectWork={onSelectWork} />
        </li>
      ))}
    </ul>
  );
}