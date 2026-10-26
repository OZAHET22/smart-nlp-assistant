"use client";

import React, { useState } from "react";
import { GitBranch, Info, CheckCircle2, AlertCircle, FileCode2, Copy, Check } from "lucide-react";
import { PipelineResult, SentenceParse } from "@/lib/nlp/types";

interface Stage2SyntaxTabProps {
  result: PipelineResult | null;
}

export function Stage2SyntaxTab({ result }: Stage2SyntaxTabProps) {
  const [selectedSentIdx, setSelectedSentIdx] = useState<number>(0);
  const [copied, setCopied] = useState<boolean>(false);

  if (!result || result.sentence_parses.length === 0) {
    return (
      <div className="glass-panel">
        <p style={{ color: "var(--text-muted)", fontSize: "0.88rem" }}>
          No sentence parses available. Please enter text and process it.
        </p>
      </div>
    );
  }

  const currentParse = result.sentence_parses[selectedSentIdx] || result.sentence_parses[0];

  const handleCopyTree = () => {
    navigator.clipboard.writeText(currentParse.cyk_parse_string);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getPosBadgeClass = (category: string) => {
    switch (category) {
      case "Noun": return "badge-noun";
      case "Verb": return "badge-verb";
      case "Adjective": return "badge-adj";
      case "Pronoun": return "badge-prp";
      case "Determiner": return "badge-det";
      case "Preposition": return "badge-prep";
      default: return "";
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Sentence Navigation Chips */}
      <div className="glass-panel" style={{ marginBottom: "20px" }}>
        <div className="panel-header">
          <h3 className="panel-title">
            <GitBranch size={16} style={{ color: "var(--accent-primary)" }} />
            Select Sentence for Detailed Syntactic Analysis ({result.sentence_parses.length})
          </h3>
        </div>
        <div style={{ display: "flex", gap: "8px", overflowX: "auto", paddingBottom: "6px", WebkitOverflowScrolling: "touch" }}>
          {result.sentence_parses.map((sp, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setSelectedSentIdx(idx)}
              className={`btn ${selectedSentIdx === idx ? "btn-primary" : "btn-secondary"} btn-sm`}
              style={{ whiteSpace: "nowrap" }}
            >
              {sp.is_valid_cfg ? <CheckCircle2 size={13} style={{ color: "var(--accent-emerald)" }} /> : <Info size={13} />}
              <span className="hide-on-mobile">Sent {idx + 1}: "{sp.sentence.slice(0, 24)}..."</span>
              <span className="show-on-mobile">Sent {idx + 1}</span>
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "20px" }}>
        {/* Token-by-Token POS & Dependency Table */}
        <div className="glass-panel">
          <div className="panel-header">
            <div>
              <h4 style={{ fontSize: "1rem", fontWeight: "700" }}>
                Token Analysis & Dependency Relations (Sentence {selectedSentIdx + 1})
              </h4>
              <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "4px" }}>
                Full sentence: <em>"{currentParse.sentence}"</em>
              </p>
            </div>
          </div>

          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Index</th>
                  <th>Token Text</th>
                  <th>POS Tag</th>
                  <th>Grammatical Category</th>
                  <th>Dependency Label</th>
                  <th>Syntactic Head</th>
                </tr>
              </thead>
              <tbody>
                {currentParse.tokens.map((token, tIdx) => (
                  <tr key={tIdx}>
                    <td style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)", fontSize: "0.78rem" }}>
                      {tIdx}
                    </td>
                    <td style={{ fontWeight: "700" }}>{token.text}</td>
                    <td>
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem", background: "rgba(255,255,255,0.06)", padding: "2px 6px", borderRadius: "4px" }}>
                        {token.pos}
                      </span>
                    </td>
                    <td>
                      <span className={`badge-pill ${getPosBadgeClass(token.pos_category)}`} style={{ fontSize: "0.72rem" }}>
                        {token.pos_category}
                      </span>
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", color: token.dep === "ROOT" ? "var(--accent-emerald)" : "var(--accent-cyan)", fontWeight: token.dep === "ROOT" ? "800" : "500" }}>
                      {token.dep}
                    </td>
                    <td style={{ color: "var(--text-secondary)", fontStyle: token.head === "ROOT" ? "italic" : "normal" }}>
                      {token.head}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Custom CYK Parse Tree Display */}
        <div className="glass-panel">
          <div className="panel-header">
            <h4 style={{ fontSize: "1rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
              <FileCode2 size={16} style={{ color: "var(--accent-cyan)" }} />
              Custom CYK Chart Parser Tree (Cocke-Younger-Kasami)
            </h4>
            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
              <button
                type="button"
                onClick={handleCopyTree}
                className="btn btn-secondary btn-sm"
                style={{ fontSize: "0.74rem" }}
              >
                {copied ? <Check size={12} style={{ color: "var(--accent-emerald)" }} /> : <Copy size={12} />}
                <span>{copied ? "Copied" : "Copy Tree"}</span>
              </button>
              <span
                className="badge-pill"
                style={{
                  background: currentParse.is_valid_cfg ? "rgba(16, 185, 129, 0.15)" : "rgba(245, 158, 11, 0.15)",
                  borderColor: currentParse.is_valid_cfg ? "rgba(16, 185, 129, 0.3)" : "rgba(245, 158, 11, 0.3)",
                  color: currentParse.is_valid_cfg ? "var(--accent-emerald)" : "var(--accent-amber)",
                }}
              >
                {currentParse.is_valid_cfg ? "Valid CFG Tree" : "Outside CFG"}
              </span>
            </div>
          </div>

          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "14px" }}>
            The hand-built CYK parser uses a 15-rule Context-Free Grammar covering simple declarative sentences (<code>S → NP VP</code>, <code>NP → DT NN</code>, <code>VP → VBD NP PP</code>).
          </p>

          <div className="code-block" style={{ fontSize: "0.85rem" }}>
            {currentParse.cyk_parse_string}
          </div>

          {/* Grammar Rule Reference */}
          <div style={{ marginTop: "16px", padding: "12px", background: "var(--bg-secondary)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
            <span style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)", display: "block", marginBottom: "6px" }}>
              15-Rule CFG Productions:
            </span>
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", fontSize: "0.75rem", fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}>
              <span>S → NP VP</span>
              <span>•</span>
              <span>NP → DT NN | PRP | NNP | DT JJ NN</span>
              <span>•</span>
              <span>VP → VB NP | VBD NP | VB PP | MD VP</span>
              <span>•</span>
              <span>PP → IN NP</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
