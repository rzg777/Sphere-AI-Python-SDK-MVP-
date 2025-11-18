import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./globals.css";
import SecurityHeaders from "./components/SecurityHeaders";

// Initialize security headers component
const root = createRoot(document.getElementById("root")!);
root.render(
  <>
    <SecurityHeaders />
    <App />
  </>
);