"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, Moon, Sun, Github, Cpu, CheckCircle } from "lucide-react";

interface HeaderProps {
  engine: "native" | "python";
  setEngine: (engine: "native" | "python") => void;
}

export function Header({ engine, setEngine }: HeaderProps) {
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    const savedTheme = localStorage.getItem("nlp_theme") as "dark" | "light" || "dark";
    setTheme(savedTheme);
    document.documentElement.setAttribute("data-theme", savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    localStorage.setItem("nlp_theme", newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
  };

  return (
    <header className="app-header">
      <div className="container header-content">
        <div className="logo-group">
          <div className="logo-icon">
            <Sparkles size={20} />
          </div>
          <div>
            <h1 className="logo-title">Smart NLP Studio</h1>
            <div className="logo-subtitle">Reading & Writing Assistant • Next.js Edition</div>
          </div>
        </div>

        <div className="header-actions">
          {/* Engine indicator */}
          <div className="badge-pill" style={{ cursor: "pointer" }} onClick={() => setEngine(engine === "native" ? "python" : "native")} title="Click to toggle engine">
            <Cpu size={14} style={{ color: "var(--accent-emerald)" }} />
            <span>Engine: {engine === "native" ? "Vercel Edge (Native)" : "Python Backend"}</span>
            <span style={{ fontSize: "0.68rem", opacity: 0.7 }}>(Toggle)</span>
          </div>

          {/* Vercel Ready Pill */}
          <div className="badge-pill" style={{ background: "rgba(16, 185, 129, 0.1)", borderColor: "rgba(16, 185, 129, 0.3)", color: "#34d399" }}>
            <CheckCircle size={14} />
            <span>Vercel Deploy Ready</span>
          </div>

          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="btn btn-secondary btn-sm"
            aria-label="Toggle Theme"
            style={{ padding: "6px 10px" }}
          >
            {theme === "dark" ? <Sun size={15} /> : <Moon size={15} />}
          </button>

          {/* GitHub Link */}
          <a
            href="https://github.com/OZAHET22/smart-nlp-assistant"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary btn-sm"
            style={{ textDecoration: "none" }}
          >
            <Github size={15} />
            <span>GitHub</span>
          </a>
        </div>
      </div>
    </header>
  );
}
