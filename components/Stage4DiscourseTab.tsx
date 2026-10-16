"use client";

import React from "react";
import { MessageSquareShare, Users, Shuffle, HelpCircle, ArrowRight } from "lucide-react";
import { PipelineResult } from "@/lib/nlp/types";

interface Stage4DiscourseTabProps {
  result: PipelineResult | null;
}

export function Stage4DiscourseTab({ result }: Stage4DiscourseTabProps) {
  if (!result) {
    return (
      <div className="glass-panel">
        <p style={{ color: "var(--text-muted)", fontSize: "0.88rem" }}>
          No discourse or pragmatic data available. Please process text first.
        </p>
      </div>
    );
  }

  const getRelationColor = (relation: string) => {
    switch (relation) {
      case "contrast": return "var(--accent-rose)";
      case "cause": return "var(--accent-amber)";
      case "cause_effect": return "var(--accent-cyan)";
      case "elaboration": return "var(--accent-primary)";
      case "temporal": return "var(--accent-violet)";
      case "condition": return "var(--accent-emerald)";
      default: return "var(--text-primary)";
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Top Grid: Coreference Chains & Pragmatic Speech Acts */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px", marginBottom: "24px" }}>
        {/* Coreference Chains */}
        <div className="glass-panel">
          <div className="panel-header">
            <h4 style={{ fontSize: "1rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
              <Users size={16} style={{ color: "var(--accent-primary)" }} />
              Coreference Resolution Chains ({result.coref_chains.length})
            </h4>
          </div>

          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "12px" }}>
            Links pronouns to their nearest grammatical antecedent using gender and number agreement rules.
          </p>

          {result.coref_chains.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {result.coref_chains.map((chain, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "10px 14px",
                    background: "var(--bg-secondary)",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--border-subtle)",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    flexWrap: "wrap",
                  }}
                >
                  <span
                    className="badge-pill"
                    style={{ fontSize: "0.7rem", padding: "2px 8px" }}
                  >
                    {chain.entity_type} {chain.gender_agreement ? `(${chain.gender_agreement})` : ""}
                  </span>

                  {chain.mentions.map((mention, mIdx) => (
                    <React.Fragment key={mIdx}>
                      <span style={{ fontWeight: "700", color: mIdx === 0 ? "var(--accent-primary)" : "var(--text-primary)" }}>
                        {mention}
                      </span>
                      {mIdx < chain.mentions.length - 1 && (
                        <ArrowRight size={12} style={{ color: "var(--text-muted)" }} />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
              No coreference pronoun chains detected in this sample.
            </p>
          )}
        </div>

        {/* Pragmatic Speech Acts & Indirect Requests */}
        <div className="glass-panel">
          <div className="panel-header">
            <h4 style={{ fontSize: "1rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
              <HelpCircle size={16} style={{ color: "var(--accent-emerald)" }} />
              Indirect Speech Act Detection ({result.pragmatic_notes.length})
            </h4>
          </div>

          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "12px" }}>
            Detects polite requests phrased as questions (e.g. <em>"Could you send us the rubric again?"</em>) and extracts the implied action.
          </p>

          {result.pragmatic_notes.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {result.pragmatic_notes.map((note, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "12px",
                    background: "var(--bg-secondary)",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--border-subtle)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                    <span
                      style={{
                        fontSize: "0.72rem",
                        fontWeight: "800",
                        textTransform: "uppercase",
                        color: "var(--accent-emerald)",
                        background: "rgba(16, 185, 129, 0.15)",
                        padding: "2px 6px",
                        borderRadius: "4px",
                      }}
                    >
                      {note.inferred_act}
                    </span>
                    <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                      Politeness Pattern
                    </span>
                  </div>

                  <div style={{ fontSize: "0.85rem", color: "var(--text-primary)", marginBottom: "6px" }}>
                    <strong>Surface Form:</strong> "{note.surface_form}"
                  </div>

                  <div style={{ fontSize: "0.82rem", color: "var(--accent-cyan)" }}>
                    <strong>Implied Action:</strong> "{note.paraphrase}"
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
              No indirect questions or polite request speech acts detected.
            </p>
          )}
        </div>
      </div>

      {/* Discourse Relations Table */}
      <div className="glass-panel">
        <div className="panel-header">
          <h4 style={{ fontSize: "1.05rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
            <Shuffle size={16} style={{ color: "var(--accent-amber)" }} />
            Discourse Connectives & Coherence Relations ({result.discourse_relations.length})
          </h4>
        </div>

        {result.discourse_relations.length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Connective Word</th>
                  <th>Relation Type</th>
                  <th>Sentence Span</th>
                  <th>Context Snippet</th>
                </tr>
              </thead>
              <tbody>
                {result.discourse_relations.map((rel, idx) => (
                  <tr key={idx}>
                    <td>
                      <span
                        style={{
                          fontWeight: "800",
                          fontFamily: "var(--font-mono)",
                          fontSize: "0.85rem",
                          color: "var(--text-primary)",
                          background: "var(--bg-secondary)",
                          padding: "2px 8px",
                          borderRadius: "4px",
                          border: "1px solid var(--border-subtle)",
                        }}
                      >
                        {rel.connective}
                      </span>
                    </td>
                    <td>
                      <span
                        className="badge-pill"
                        style={{
                          color: getRelationColor(rel.relation),
                          borderColor: getRelationColor(rel.relation),
                          fontSize: "0.72rem",
                        }}
                      >
                        {rel.relation}
                      </span>
                    </td>
                    <td style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                      Sentence {rel.sentence_a + 1} → Sentence {rel.sentence_b + 1}
                    </td>
                    <td style={{ fontSize: "0.82rem", color: "var(--text-primary)" }}>
                      "{rel.context_snippet}"
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
            No discourse connectives (however, because, therefore, also) detected in this text.
          </p>
        )}
      </div>
    </div>
  );
}
