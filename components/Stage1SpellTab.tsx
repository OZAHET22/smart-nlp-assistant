"use client";

import React, { useState } from "react";
import { Grid, Sparkles, HelpCircle, ArrowRight, Table, Layers, MoveHorizontal } from "lucide-react";
import { PipelineResult, SpellCorrection, LevenshteinMatrixResult } from "@/lib/nlp/types";
import { getLevenshteinMatrix } from "@/lib/nlp/stage1-spellcheck";

interface Stage1SpellTabProps {
  result: PipelineResult | null;
}

export function Stage1SpellTab({ result }: Stage1SpellTabProps) {
  const [selectedWord1, setSelectedWord1] = useState<string>("assigment");
  const [selectedWord2, setSelectedWord2] = useState<string>("assignment");

  const matrixData: LevenshteinMatrixResult = getLevenshteinMatrix(selectedWord1, selectedWord2);

  const presets = [
    { w1: "assigment", w2: "assignment" },
    { w1: "recieve", w2: "receive" },
    { w1: "definately", w2: "definitely" },
    { w1: "thier", w2: "their" },
    { w1: "seperate", w2: "separate" },
  ];

  const handleSelectCorrection = (corr: SpellCorrection) => {
    setSelectedWord1(corr.original);
    setSelectedWord2(corr.corrected);
  };

  return (
    <div className="animate-fade-in">
      {/* Overview Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 280px), 1fr))", gap: "16px", marginBottom: "24px" }}>
        <div className="glass-panel" style={{ padding: "18px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
            <Sparkles size={16} style={{ color: "var(--accent-primary)" }} />
            <h4 style={{ fontSize: "0.95rem", fontWeight: "700" }}>Levenshtein DP Algorithm</h4>
          </div>
          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>
            Implemented from scratch using dynamic programming. Computes minimum cost over deletions, insertions, and substitutions with a rolling two-row O(min(n,m)) space array.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: "18px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
            <Layers size={16} style={{ color: "var(--accent-cyan)" }} />
            <h4 style={{ fontSize: "0.95rem", fontWeight: "700" }}>Brown Corpus N-Gram Context</h4>
          </div>
          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: "1.5" }}>
            Bigram context scoring breaks ties for in-vocabulary confusable pairs like <em>there/their/they're</em> and <em>to/too</em> where pure edit distance is ambiguous.
          </p>
        </div>
      </div>

      {/* Corrections Table */}
      <div className="glass-panel" style={{ marginBottom: "24px" }}>
        <div className="panel-header">
          <h3 className="panel-title">
            <Table size={16} style={{ color: "var(--accent-primary)" }} />
            Detected Spelling Corrections ({result?.corrections.length || 0})
          </h3>
          <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
            Tap any row to inspect its dynamic programming cost grid
          </span>
        </div>

        {result && result.corrections.length > 0 ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Original Token</th>
                  <th>Suggested Correction</th>
                  <th>Levenshtein Dist</th>
                  <th>Disambiguation Reason</th>
                  <th>Scoring Metric</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {result.corrections.map((corr, idx) => (
                  <tr
                    key={idx}
                    style={{
                      cursor: "pointer",
                      background: selectedWord1.toLowerCase() === corr.original.toLowerCase() ? "rgba(99, 102, 241, 0.08)" : undefined,
                    }}
                    onClick={() => handleSelectCorrection(corr)}
                  >
                    <td>
                      <span className="diff-del">{corr.original}</span>
                    </td>
                    <td>
                      <span className="diff-ins">{corr.corrected}</span>
                    </td>
                    <td>
                      <span className="badge-pill" style={{ fontSize: "0.72rem" }}>
                        d = {corr.edit_distance}
                      </span>
                    </td>
                    <td>
                      <span style={{
                        color: corr.reason === "context_ngram" ? "var(--accent-cyan)" : "var(--accent-amber)",
                        fontWeight: "600",
                        fontSize: "0.78rem",
                      }}>
                        {corr.reason === "context_ngram" ? "Context N-Gram Probability" : "Minimum Edit Distance"}
                      </span>
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                      {corr.score.toFixed(4)}
                    </td>
                    <td>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectCorrection(corr);
                        }}
                        className="btn btn-secondary btn-sm"
                        style={{ fontSize: "0.72rem", padding: "4px 8px" }}
                      >
                        Inspect DP Grid
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: "var(--text-muted)", fontSize: "0.88rem" }}>
            {result ? "No spelling corrections required for this text." : "Please process text first."}
          </p>
        )}
      </div>

      {/* Interactive 2D Levenshtein Dynamic Programming Cost Matrix */}
      <div className="glass-panel">
        <div className="panel-header">
          <h3 className="panel-title">
            <Grid size={16} style={{ color: "var(--accent-emerald)" }} />
            Interactive Levenshtein DP Matrix Explorer
          </h3>
          <div style={{ display: "flex", gap: "8px", alignItems: "center", flexWrap: "wrap", width: "100%", maxWidth: "460px" }}>
            <input
              type="text"
              value={selectedWord1}
              onChange={(e) => setSelectedWord1(e.target.value)}
              placeholder="Word 1"
              aria-label="First word for Levenshtein comparison"
              style={{
                background: "var(--bg-input)",
                border: "1px solid var(--border-medium)",
                color: "var(--text-primary)",
                padding: "6px 10px",
                borderRadius: "var(--radius-sm)",
                fontSize: "0.82rem",
                flex: "1 1 110px",
              }}
            />
            <span style={{ color: "var(--text-muted)", fontSize: "0.82rem" }}>vs</span>
            <input
              type="text"
              value={selectedWord2}
              onChange={(e) => setSelectedWord2(e.target.value)}
              placeholder="Word 2"
              aria-label="Second word for Levenshtein comparison"
              style={{
                background: "var(--bg-input)",
                border: "1px solid var(--border-medium)",
                color: "var(--text-primary)",
                padding: "6px 10px",
                borderRadius: "var(--radius-sm)",
                fontSize: "0.82rem",
                flex: "1 1 110px",
              }}
            />
          </div>
        </div>

        {/* Quick presets */}
        <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "12px", alignItems: "center" }}>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: "600" }}>Quick Presets:</span>
          {presets.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setSelectedWord1(p.w1);
                setSelectedWord2(p.w2);
              }}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "0.72rem", padding: "3px 8px" }}
            >
              {p.w1} → {p.w2}
            </button>
          ))}
        </div>

        <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "14px" }}>
          Cost table between <strong>"{selectedWord1}"</strong> and <strong>"{selectedWord2}"</strong>. Total minimum edit distance: <strong>{matrixData.distance}</strong> operations.
        </p>

        {/* Mobile Swipe Hint */}
        <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--accent-cyan)", fontSize: "0.74rem", marginBottom: "8px" }}>
          <MoveHorizontal size={14} />
          <span>Swipe horizontally on mobile/tablet to explore entire cost matrix</span>
        </div>

        {/* Matrix Render */}
        <div className="table-responsive" style={{ padding: "8px 4px", border: "1px solid var(--border-subtle)" }}>
          <table style={{ borderCollapse: "separate", borderSpacing: "4px", margin: "0 auto" }}>
            <thead>
              <tr>
                <th className="matrix-cell header">Ø</th>
                <th className="matrix-cell header">ε</th>
                {selectedWord2.split("").map((char, cIdx) => (
                  <th key={cIdx} className="matrix-cell header">
                    {char}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {/* Row 0 (empty string) */}
              <tr>
                <td className="matrix-cell header">ε</td>
                {matrixData.matrix[0]?.map((val, colIdx) => (
                  <td key={colIdx} className={`matrix-cell ${colIdx === 0 ? "highlight" : ""}`}>
                    {val}
                  </td>
                ))}
              </tr>

              {/* Rows 1..m */}
              {selectedWord1.split("").map((char1, rowIdx) => (
                <tr key={rowIdx}>
                  <td className="matrix-cell header">{char1}</td>
                  {matrixData.matrix[rowIdx + 1]?.map((val, colIdx) => {
                    const isLast = rowIdx + 1 === selectedWord1.length && colIdx === selectedWord2.length;
                    return (
                      <td
                        key={colIdx}
                        className={`matrix-cell ${isLast ? "highlight" : ""}`}
                        title={`Cost at (${rowIdx + 1}, ${colIdx}): ${val}`}
                      >
                        {val}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Backtrace Operations Flow */}
        <div style={{ marginTop: "16px", paddingTop: "14px", borderTop: "1px solid var(--border-subtle)" }}>
          <div style={{ fontSize: "0.78rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "8px" }}>
            Sequence of Edit Operations ({matrixData.operations.length}):
          </div>
          <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", alignItems: "center" }}>
            {matrixData.operations.map((op, idx) => (
              <span
                key={idx}
                style={{
                  fontSize: "0.75rem",
                  padding: "4px 8px",
                  borderRadius: "4px",
                  background: op.type === "match" ? "rgba(16, 185, 129, 0.1)" : op.type === "substitute" ? "rgba(245, 158, 11, 0.1)" : "rgba(244, 63, 94, 0.1)",
                  border: `1px solid ${op.type === "match" ? "rgba(16, 185, 129, 0.3)" : op.type === "substitute" ? "rgba(245, 158, 11, 0.3)" : "rgba(244, 63, 94, 0.3)"}`,
                  color: op.type === "match" ? "var(--accent-emerald)" : op.type === "substitute" ? "var(--accent-amber)" : "var(--accent-rose)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {op.type}: {op.char1 || "ε"} → {op.char2 || "ε"} (cost: {op.cost})
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
