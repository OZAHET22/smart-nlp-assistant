"use client";

import React from "react";
import { ArrowRight, SpellCheck, GitBranch, Binary, MessageSquareShare, FileSpreadsheet, Sparkles } from "lucide-react";

interface HeroBannerProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export function HeroBanner({ activeTab, setActiveTab }: HeroBannerProps) {
  const stages = [
    { id: "editor", label: "Smart Editor", shortLabel: "Editor", icon: Sparkles },
    { id: "stage1", label: "1. Spell & DP Matrix", shortLabel: "1. Spell", icon: SpellCheck },
    { id: "stage2", label: "2. Syntax & CYK", shortLabel: "2. Syntax", icon: GitBranch },
    { id: "stage3", label: "3. Semantics & WSD", shortLabel: "3. Semantics", icon: Binary },
    { id: "stage4", label: "4. Discourse & Coref", shortLabel: "4. Discourse", icon: MessageSquareShare },
    { id: "stage5", label: "5. Export Studio", shortLabel: "5. Export", icon: FileSpreadsheet },
  ];

  return (
    <section className="hero-card" aria-label="Pipeline overview">
      <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap", marginBottom: "12px" }}>
        <div className="badge-pill">
          <span>Enterprise NLP Pipeline</span>
          <span>•</span>
          <span>Grammarly-Style Intelligence</span>
        </div>
        <div className="badge-pill hide-on-mobile" style={{ background: "rgba(6, 182, 212, 0.1)", borderColor: "rgba(6, 182, 212, 0.25)", color: "var(--accent-cyan)" }}>
          <span>Next.js 14 App Router</span>
        </div>
      </div>

      <h2 className="hero-headline">Deep Natural Language Pipeline & Writing Assistant</h2>
      <p className="hero-lead">
        Processes noisy student writing through classical NLP stages with explainable AI: Levenshtein DP edit distance,
        Brown n-grams, CYK chart parsing over CFG, WordNet Lesk WSD, coreference resolution, and pragmatic speech acts.
      </p>

      {/* Responsive Horizontal Stepper */}
      <div className="pipeline-stepper" role="tablist" aria-label="Pipeline Stages">
        {stages.map((stage, idx) => {
          const Icon = stage.icon;
          const isActive = activeTab === stage.id;
          return (
            <React.Fragment key={stage.id}>
              <button
                type="button"
                role="tab"
                aria-selected={isActive}
                className={`step-chip ${isActive ? "active" : ""}`}
                onClick={() => setActiveTab(stage.id)}
                title={`Go to ${stage.label}`}
              >
                {isActive && <span className="step-dot" />}
                <Icon size={14} />
                <span className="hide-on-mobile">{stage.label}</span>
                <span className="show-on-mobile">{stage.shortLabel}</span>
              </button>
              {idx < stages.length - 1 && (
                <span className="step-arrow hide-on-mobile" aria-hidden="true">
                  <ArrowRight size={12} />
                </span>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </section>
  );
}
