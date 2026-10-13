import { createRoot } from "react-dom/client";
import { App } from "./workspace/App";
import { ReviewEntry } from "./workspace/ReviewWorkspace";
import "./style.css";

createRoot(document.getElementById("root")!).render(
  <ReviewEntry>
    <App />
  </ReviewEntry>,
);
