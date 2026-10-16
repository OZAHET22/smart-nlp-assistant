"use client";

import React from "react";
import { ArrowRight, SpellCheck, GitBranch, Binary, MessageSquareShare, FileSpreadsheet } from "lucide-react";

interface HeroBannerProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export function HeroBanner({ activeTab, setActiveTab }: HeroBannerProps) {
  const stages = [
    { id: "editor", label: "Smart Editor", icon: SpellCheck },
    { id: "stage1", label: "1. Spell & N-Gram", icon: SpellCheck },
    { id: "stage2", label: "2. Syntax & CYK", icon: GitBranch },
    { id: "stage3", label: "3. Semantics & WSD", icon: Binary },
    { id: "stage4", label: "4. Discourse & Pragmatics", icon: MessageSquareShare },
    { id: "stage5", label: "5. Assembly & Export", icon: FileSpreadsheet },
  ];

  return (
    <div className="hero-card">
      <div className="badge-pill" style={{ marginBottom: "14px" }}>
        <span>Enterprise NLP Pipeline</span>
        <span>•</span>
        <span>Grammarly-Style Intelligence</span>
      </div>

      <h2 className="hero-headline">Deep Natural Language Pipeline & Writing Assistant</h2>
      <p className="hero-lead">
        Processes raw, noisy student writing through classical NLP stages with full explainability: Levenshtein edit distance,
        context-aware Brown n-grams, CYK chart parsing over CFG, WordNet Lesk WSD, coreference resolution, and pragmatic speech acts.
      </p>

      <div className="pipeline-stepper">
        {stages.map((stage, idx) => {
          const Icon = stage.icon;
          const isActive = activeTab === stage.id;
          return (
            <React.Fragment key={stage.id}>
              <div
                className={`step-chip ${isActive ? "active" : ""}`}
                style={{ cursor: "pointer" }}
                onClick={() => setActiveTab(stage.id)}
              >
                {isActive && <div className="step-dot" />}
                <Icon size={14} />
                <span>{stage.label}</span>
              </div>
              {idx < stages.length - 1 && <span className="step-arrow"><ArrowRight size={12} /></span>}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
