"use client";

import React, { useState } from "react";
import { Play, Sparkles, RotateCcw, Check, ArrowRight, Wand2, BookOpen, Clock, Activity, FileText, Copy, Columns, Edit3, CheckCircle2 } from "lucide-react";
import confetti from "canvas-confetti";
import { PipelineResult, TestSample } from "@/lib/nlp/types";
import { TEST_SAMPLES } from "@/lib/nlp/samples-data";

interface EditorSectionProps {
  inputText: string;
  setInputText: (text: string) => void;
  result: PipelineResult | null;
  onProcess: () => void;
  loading: boolean;
  onApplyCorrection: (original: string, corrected: string) => void;
  onApplyAll: () => void;
}

export function EditorSection({
  inputText,
  setInputText,
  result,
  onProcess,
  loading,
  onApplyCorrection,
  onApplyAll,
}: EditorSectionProps) {
  const [selectedSampleId, setSelectedSampleId] = useState<string>("sample_01");
  const [mobileView, setMobileView] = useState<"split" | "input" | "output">("split");
  const [copied, setCopied] = useState<boolean>(false);

  const handleSelectSample = (sampleId: string) => {
    setSelectedSampleId(sampleId);
    const sample = TEST_SAMPLES.find((s) => s.id === sampleId);
    if (sample) {
      setInputText(sample.text);
    }
  };

  const handleTriggerConfetti = () => {
    onApplyAll();
    try {
      confetti({
        particleCount: 80,
        spread: 60,
        origin: { y: 0.6 },
      });
    } catch (e) {
      // safe fallback
    }
  };

  const handleCopyOutput = () => {
    if (!result) return;
    navigator.clipboard.writeText(result.corrected_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const currentSample = TEST_SAMPLES.find((s) => s.id === selectedSampleId);

  return (
    <div className="glass-panel" style={{ marginBottom: "24px" }}>
      {/* Top Controls: Preset selector & Action buttons */}
      <div className="panel-header">
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap", width: "100%", maxWidth: "700px" }}>
          <span style={{ fontSize: "0.82rem", fontWeight: "700", color: "var(--text-secondary)", whiteSpace: "nowrap" }}>
            Sample Presets:
          </span>
          <select
            value={selectedSampleId}
            onChange={(e) => handleSelectSample(e.target.value)}
            style={{
              background: "var(--bg-secondary)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-medium)",
              borderRadius: "var(--radius-sm)",
              padding: "7px 12px",
              fontSize: "0.85rem",
              fontWeight: "600",
              outline: "none",
              cursor: "pointer",
              maxWidth: "100%",
              flex: "1 1 200px",
            }}
          >
            {TEST_SAMPLES.map((s) => (
              <option key={s.id} value={s.id}>
                {s.filename}: {s.title}
              </option>
            ))}
          </select>

          {currentSample && (
            <span className="hide-on-mobile" style={{ fontSize: "0.78rem", color: "var(--text-muted)", maxWidth: "340px" }}>
              {currentSample.description}
            </span>
          )}
        </div>

        <div style={{ display: "flex", gap: "8px", alignItems: "center", width: "100%", justifyContent: "flex-end" }}>
          <button
            onClick={() => setInputText("")}
            className="btn btn-secondary btn-sm"
            title="Clear editor"
            type="button"
          >
            Clear
          </button>

          <button
            onClick={onProcess}
            disabled={loading || !inputText.trim()}
            className="btn btn-primary"
            style={{ padding: "8px 18px" }}
            type="button"
          >
            {loading ? <RotateCcw size={15} className="animate-spin" /> : <Play size={15} />}
            <span>{loading ? "Analyzing..." : "Process Text"}</span>
          </button>
        </div>
      </div>

      {/* Mobile-Only View Switcher (Input vs Polished vs Split) */}
      <div className="show-on-mobile" style={{ marginBottom: "12px" }}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "4px",
            background: "var(--bg-secondary)",
            padding: "3px",
            borderRadius: "var(--radius-sm)",
            border: "1px solid var(--border-subtle)",
          }}
        >
          <button
            type="button"
            onClick={() => setMobileView("split")}
            className={`btn btn-sm ${mobileView === "split" ? "btn-primary" : "btn-secondary"}`}
            style={{ padding: "6px 8px", fontSize: "0.74rem", border: "none" }}
          >
            <Columns size={12} />
            <span>Split</span>
          </button>

          <button
            type="button"
            onClick={() => setMobileView("input")}
            className={`btn btn-sm ${mobileView === "input" ? "btn-primary" : "btn-secondary"}`}
            style={{ padding: "6px 8px", fontSize: "0.74rem", border: "none" }}
          >
            <Edit3 size={12} />
            <span>Input</span>
          </button>

          <button
            type="button"
            onClick={() => setMobileView("output")}
            className={`btn btn-sm ${mobileView === "output" ? "btn-primary" : "btn-secondary"}`}
            style={{ padding: "6px 8px", fontSize: "0.74rem", border: "none" }}
          >
            <Sparkles size={12} />
            <span>Output ({result?.corrections.length || 0})</span>
          </button>
        </div>
      </div>

      {/* Editor & Side-by-side Diff View */}
      <div className="editor-wrapper">
        {/* Left: Input Text Box */}
        {(mobileView === "split" || mobileView === "input") && (
          <div className="editor-box">
            <div className="editor-header">
              <span>Raw Student Input</span>
              <span>{inputText.length} chars</span>
            </div>
            <textarea
              className="textarea-clean"
              placeholder="Type or paste messy student text here..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              aria-label="Student input text"
            />
          </div>
        )}

        {/* Right: Live Correction & Diff View */}
        {(mobileView === "split" || mobileView === "output") && (
          <div className="editor-box">
            <div className="editor-header">
              <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <Sparkles size={14} style={{ color: "var(--accent-primary)" }} />
                Corrected & Polished Output
              </span>
              <div style={{ display: "flex", gap: "6px" }}>
                {result && (
                  <button
                    onClick={handleCopyOutput}
                    className="btn btn-secondary btn-sm"
                    style={{ fontSize: "0.72rem", padding: "3px 8px" }}
                    title="Copy corrected text"
                    type="button"
                  >
                    {copied ? <Check size={12} style={{ color: "var(--accent-emerald)" }} /> : <Copy size={12} />}
                    <span>{copied ? "Copied" : "Copy"}</span>
                  </button>
                )}
                {result && result.corrections.length > 0 && (
                  <button
                    onClick={handleTriggerConfetti}
                    className="btn btn-secondary btn-sm"
                    style={{
                      fontSize: "0.72rem",
                      padding: "3px 8px",
                      borderColor: "rgba(16, 185, 129, 0.4)",
                      color: "var(--accent-emerald)",
                    }}
                    type="button"
                  >
                    <Check size={12} /> Apply All ({result.corrections.length})
                  </button>
                )}
              </div>
            </div>

            {result ? (
              <div className="diff-display">
                {result.corrected_text}
              </div>
            ) : (
              <div style={{ minHeight: "220px", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", fontSize: "0.88rem" }}>
                Click "Process Text" to run the 5-stage NLP pipeline.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Quick Corrections Pill Bar */}
      {result && result.corrections.length > 0 && (
        <div style={{ marginTop: "18px", paddingTop: "14px", borderTop: "1px solid var(--border-subtle)" }}>
          <div style={{ fontSize: "0.78rem", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-muted)", marginBottom: "10px" }}>
            Detected Corrections ({result.corrections.length}):
          </div>
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            {result.corrections.map((corr, idx) => (
              <div
                key={idx}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  background: "var(--bg-secondary)",
                  border: "1px solid var(--border-medium)",
                  borderRadius: "var(--radius-full)",
                  padding: "4px 10px",
                  fontSize: "0.8rem",
                }}
              >
                <span style={{ textDecoration: "line-through", color: "var(--diff-del-text)" }}>
                  {corr.original}
                </span>
                <ArrowRight size={11} style={{ opacity: 0.5 }} />
                <span style={{ fontWeight: "700", color: "var(--diff-ins-text)" }}>
                  {corr.corrected}
                </span>
                <span style={{ fontSize: "0.68rem", opacity: 0.6, background: "rgba(255,255,255,0.06)", padding: "1px 5px", borderRadius: "4px" }}>
                  {corr.reason === "context_ngram" ? "n-gram" : `d=${corr.edit_distance}`}
                </span>
                <button
                  type="button"
                  onClick={() => onApplyCorrection(corr.original, corr.corrected)}
                  style={{
                    background: "transparent",
                    border: "none",
                    cursor: "pointer",
                    color: "var(--accent-emerald)",
                    display: "flex",
                    alignItems: "center",
                    padding: "2px",
                  }}
                  title={`Apply "${corr.corrected}"`}
                  aria-label={`Apply correction: replace ${corr.original} with ${corr.corrected}`}
                >
                  <Check size={13} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metrics Bar */}
      {result && (
        <div className="metrics-grid">
          <div className="metric-card">
            <span className="metric-label">Reading Ease</span>
            <span className="metric-value" style={{ color: result.metrics.flesch_reading_ease >= 60 ? "var(--accent-emerald)" : "var(--accent-amber)" }}>
              {result.metrics.flesch_reading_ease}
            </span>
            <span className="metric-sub">{result.metrics.reading_level}</span>
          </div>

          <div className="metric-card">
            <span className="metric-label">Grade Level</span>
            <span className="metric-value">Grade {result.metrics.flesch_kincaid_grade}</span>
            <span className="metric-sub">Flesch-Kincaid</span>
          </div>

          <div className="metric-card">
            <span className="metric-label">Tone & Style</span>
            <span className="metric-value" style={{ fontSize: "0.95rem" }}>{result.metrics.sentiment_tone}</span>
            <span className="metric-sub">Communication style</span>
          </div>

          <div className="metric-card">
            <span className="metric-label">Word Count</span>
            <span className="metric-value">{result.metrics.word_count}</span>
            <span className="metric-sub">{result.metrics.sentence_count} sentences</span>
          </div>

          <div className="metric-card">
            <span className="metric-label">Reading Time</span>
            <span className="metric-value">~{result.metrics.reading_time_seconds}s</span>
            <span className="metric-sub">at 220 wpm</span>
          </div>

          <div className="metric-card">
            <span className="metric-label">Pipeline Latency</span>
            <span className="metric-value" style={{ color: "var(--accent-cyan)" }}>
              {result.processing_time_ms.total}ms
            </span>
            <span className="metric-sub">5 stages end-to-end</span>
          </div>
        </div>
      )}
    </div>
  );
}
