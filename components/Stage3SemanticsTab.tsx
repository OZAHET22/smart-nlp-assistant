"use client";

import React from "react";
import { Binary, Tag, UserCheck, BookOpen, Layers, ArrowRight, ArrowDown } from "lucide-react";
import { PipelineResult, SemanticFrame } from "@/lib/nlp/types";

interface Stage3SemanticsTabProps {
  result: PipelineResult | null;
}

export function Stage3SemanticsTab({ result }: Stage3SemanticsTabProps) {
  if (!result || result.semantic_frames.length === 0) {
    return (
      <div className="glass-panel">
        <p style={{ color: "var(--text-muted)", fontSize: "0.88rem" }}>
          No semantic frames available. Please process text first.
        </p>
      </div>
    );
  }

  // Aggregate all entities across frames
  const allEntities = result.semantic_frames.flatMap((f) => f.entities);

  // Collect all WSD disambiguated words
  const allWsdWords = result.semantic_frames.flatMap((f) =>
    f.word_senses_details ? Object.entries(f.word_senses_details) : []
  );

  return (
    <div className="animate-fade-in">
      {/* Top Section: Named Entity Recognition & WSD summary */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 300px), 1fr))", gap: "20px", marginBottom: "24px" }}>
        {/* Named Entities Card */}
        <div className="glass-panel">
          <div className="panel-header">
            <h4 style={{ fontSize: "1rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
              <Tag size={16} style={{ color: "var(--accent-primary)" }} />
              Named Entities Detected ({allEntities.length})
            </h4>
          </div>

          {allEntities.length > 0 ? (
            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
              {allEntities.map((ent, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "4px 10px",
                    background: "var(--bg-secondary)",
                    border: "1px solid var(--border-medium)",
                    borderRadius: "var(--radius-full)",
                    fontSize: "0.8rem",
                  }}
                >
                  <span style={{ fontWeight: "700" }}>{ent.text}</span>
                  <span
                    style={{
                      fontSize: "0.68rem",
                      fontWeight: "800",
                      padding: "2px 6px",
                      borderRadius: "4px",
                      background: ent.label === "PERSON" ? "rgba(99, 102, 241, 0.2)" : ent.label === "DATE" ? "rgba(16, 185, 129, 0.2)" : "rgba(245, 158, 11, 0.2)",
                      color: ent.label === "PERSON" ? "var(--accent-primary)" : ent.label === "DATE" ? "var(--accent-emerald)" : "var(--accent-amber)",
                    }}
                  >
                    {ent.label}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
              No formal named entities (PERSON, ORG, DATE) identified in this text.
            </p>
          )}
        </div>

        {/* Word Sense Disambiguation Card */}
        <div className="glass-panel">
          <div className="panel-header">
            <h4 style={{ fontSize: "1rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
              <BookOpen size={16} style={{ color: "var(--accent-cyan)" }} />
              Word Sense Disambiguation (Lesk Algorithm)
            </h4>
          </div>

          {allWsdWords.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {allWsdWords.map(([word, details], idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "10px 14px",
                    background: "var(--bg-secondary)",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--border-subtle)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px", flexWrap: "wrap", gap: "6px" }}>
                    <span style={{ fontWeight: "800", fontSize: "0.9rem", color: "var(--accent-cyan)" }}>
                      Target: "{word}"
                    </span>
                    <span className="badge-pill" style={{ fontSize: "0.72rem" }}>
                      Sense: {details.synset}
                    </span>
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-primary)", marginBottom: "4px" }}>
                    <strong>Definition:</strong> {details.definition}
                  </div>
                  <div style={{ fontSize: "0.74rem", color: "var(--text-muted)" }}>
                    <strong>Overlap Score:</strong> {details.overlap_score} token match ({details.overlap_words.join(", ") || "context fit"})
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
              No polysemous target words (bank, bat, light, plant, spring, crane, match, ring) found in this text.
            </p>
          )}
        </div>
      </div>

      {/* Semantic Role Labeling (SRL) Frames */}
      <div className="glass-panel">
        <div className="panel-header">
          <h4 style={{ fontSize: "1.05rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
            <UserCheck size={16} style={{ color: "var(--accent-emerald)" }} />
            Semantic Role Frames (Agent → Action → Patient)
          </h4>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          {result.semantic_frames.map((frame, idx) => (
            <div
              key={idx}
              style={{
                padding: "16px",
                background: "var(--bg-secondary)",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--border-subtle)",
              }}
            >
              <div style={{ fontSize: "0.85rem", fontWeight: "600", marginBottom: "12px", color: "var(--text-primary)" }}>
                Sentence {idx + 1}: <em>"{frame.sentence}"</em>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 160px), 1fr))", gap: "10px" }}>
                {/* Agent */}
                <div style={{ padding: "10px", background: "var(--bg-input)", borderRadius: "6px", borderLeft: "3px solid var(--accent-primary)" }}>
                  <div style={{ fontSize: "0.68rem", textTransform: "uppercase", color: "var(--text-muted)", fontWeight: "700", marginBottom: "2px" }}>
                    Agent (Actor)
                  </div>
                  <div style={{ fontSize: "0.88rem", fontWeight: "700", color: frame.agent ? "var(--text-primary)" : "var(--text-muted)" }}>
                    {frame.agent || "(none)"}
                  </div>
                </div>

                {/* Action */}
                <div style={{ padding: "10px", background: "var(--bg-input)", borderRadius: "6px", borderLeft: "3px solid var(--accent-emerald)" }}>
                  <div style={{ fontSize: "0.68rem", textTransform: "uppercase", color: "var(--text-muted)", fontWeight: "700", marginBottom: "2px" }}>
                    Action (Verb)
                  </div>
                  <div style={{ fontSize: "0.88rem", fontWeight: "700", color: frame.action ? "var(--accent-emerald)" : "var(--text-muted)" }}>
                    {frame.action || "(none)"}
                  </div>
                </div>

                {/* Patient */}
                <div style={{ padding: "10px", background: "var(--bg-input)", borderRadius: "6px", borderLeft: "3px solid var(--accent-cyan)" }}>
                  <div style={{ fontSize: "0.68rem", textTransform: "uppercase", color: "var(--text-muted)", fontWeight: "700", marginBottom: "2px" }}>
                    Patient (Recipient / Object)
                  </div>
                  <div style={{ fontSize: "0.88rem", fontWeight: "700", color: frame.patient ? "var(--text-primary)" : "var(--text-muted)" }}>
                    {frame.patient || "(none)"}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
