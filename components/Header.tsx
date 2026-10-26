"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, Moon, Sun, Github, Cpu, CheckCircle } from "lucide-react";

interface HeaderProps {
  engine: "native" | "python";
  setEngine: (engine: "native" | "python") => void;
}

export function Header({ engine, setEngine }: HeaderProps) {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [mounted, setMounted] = useState<boolean>(false);

  useEffect(() => {
    setMounted(true);
    const savedTheme = (localStorage.getItem("nlp_theme") as "dark" | "light") || "dark";
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
        {/* Brand Logo & Title */}
        <div className="logo-group">
          <div className="logo-icon" aria-hidden="true">
            <Sparkles size={20} />
          </div>
          <div className="logo-text-block">
            <h1 className="logo-title">Smart NLP Studio</h1>
            <span className="logo-subtitle">Reading & Writing Assistant</span>
          </div>
        </div>

        {/* Adaptive Responsive Header Actions */}
        <div className="header-actions">
          {/* Engine indicator toggle chip */}
          <button
            type="button"
            className="badge-pill"
            style={{
              cursor: "pointer",
              border: "1px solid rgba(99, 102, 241, 0.35)",
              background: engine === "native" ? "rgba(99, 102, 241, 0.12)" : "rgba(245, 158, 11, 0.12)",
              color: engine === "native" ? "#a5b4fc" : "#fcd34d",
              fontFamily: "inherit",
            }}
            onClick={() => setEngine(engine === "native" ? "python" : "native")}
            title="Click to switch between Vercel Edge Native Engine and Python Backend"
          >
            <Cpu size={14} style={{ color: engine === "native" ? "var(--accent-emerald)" : "var(--accent-amber)" }} />
            <span className="hide-on-mobile">Engine: {engine === "native" ? "Vercel Edge" : "Python API"}</span>
            <span className="show-on-mobile">{engine === "native" ? "⚡ Edge" : "🐍 Python"}</span>
          </button>

          {/* Vercel Status Badge */}
          <div
            className="badge-pill"
            style={{
              background: "rgba(16, 185, 129, 0.1)",
              borderColor: "rgba(16, 185, 129, 0.3)",
              color: "#34d399",
            }}
            title="Production Ready on Vercel Edge Serverless Network"
          >
            <span className="pulse-dot" />
            <span className="badge-deploy-text">Vercel Ready</span>
          </div>

          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="btn btn-secondary btn-sm btn-icon"
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
            title={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
          >
            {mounted && theme === "dark" ? <Sun size={15} /> : <Moon size={15} />}
          </button>

          {/* GitHub link */}
          <a
            href="https://github.com/OZAHET22/smart-nlp-assistant"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary btn-sm"
            style={{ textDecoration: "none" }}
            aria-label="GitHub Repository"
            title="View Source on GitHub"
          >
            <Github size={15} />
            <span className="hide-on-mobile">GitHub</span>
          </a>
        </div>
      </div>
    </header>
  );
}
