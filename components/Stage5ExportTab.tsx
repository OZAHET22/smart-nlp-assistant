"use client";

import React, { useState } from "react";
import { Download, Copy, Check, FileText, Code2, Printer } from "lucide-react";
import { PipelineResult } from "@/lib/nlp/types";
import { generateMarkdownReport } from "@/lib/nlp/stage5-pipeline";

interface Stage5ExportTabProps {
  result: PipelineResult | null;
  rawText: string;
}

export function Stage5ExportTab({ result, rawText }: Stage5ExportTabProps) {
  const [copiedType, setCopiedType] = useState<string | null>(null);

  if (!result) {
    return (
      <div className="glass-panel">
        <p style={{ color: "var(--text-muted)", fontSize: "0.88rem" }}>
          Please process text first to view exportable outputs.
        </p>
      </div>
    );
  }

  const markdownContent = generateMarkdownReport(result, rawText);
  const jsonContent = JSON.stringify(result, null, 2);

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopiedType(type);
    setTimeout(() => setCopiedType(null), 2000);
  };

  const downloadFile = (content: string, filename: string, mime: string) => {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handlePrintReport = () => {
    if (typeof window !== "undefined") {
      window.print();
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Top Banner with Quick Print Action */}
      <div className="glass-panel" style={{ marginBottom: "20px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <h3 style={{ fontSize: "1.05rem", fontWeight: "700" }}>Continuous Pipeline Report & Export Studio</h3>
          <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "2px" }}>
            Export the complete linguistic analysis across all 5 stages in Markdown, JSON, or print-ready PDF format.
          </p>
        </div>
        <button
          type="button"
          onClick={handlePrintReport}
          className="btn btn-secondary btn-sm"
          title="Print or Save as PDF"
        >
          <Printer size={14} style={{ color: "var(--accent-primary)" }} />
          <span>Print / PDF Report</span>
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 340px), 1fr))", gap: "20px" }}>
        {/* Executive Markdown Report */}
        <div className="glass-panel">
          <div className="panel-header">
            <h4 style={{ fontSize: "1rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
              <FileText size={16} style={{ color: "var(--accent-primary)" }} />
              Executive Markdown Report
            </h4>
            <div style={{ display: "flex", gap: "6px" }}>
              <button
                type="button"
                onClick={() => copyToClipboard(markdownContent, "md")}
                className="btn btn-secondary btn-sm"
              >
                {copiedType === "md" ? <Check size={13} style={{ color: "var(--accent-emerald)" }} /> : <Copy size={13} />}
                <span>{copiedType === "md" ? "Copied" : "Copy"}</span>
              </button>
              <button
                type="button"
                onClick={() => downloadFile(markdownContent, "nlp_analysis_report.md", "text/markdown")}
                className="btn btn-secondary btn-sm"
              >
                <Download size={13} />
                <span>.md</span>
              </button>
            </div>
          </div>

          <div
            className="code-block"
            style={{ maxHeight: "420px", overflowY: "auto", fontSize: "0.8rem" }}
          >
            {markdownContent}
          </div>
        </div>

        {/* Structured JSON Output */}
        <div className="glass-panel">
          <div className="panel-header">
            <h4 style={{ fontSize: "1rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
              <Code2 size={16} style={{ color: "var(--accent-cyan)" }} />
              Structured JSON Result (PipelineResult)
            </h4>
            <div style={{ display: "flex", gap: "6px" }}>
              <button
                type="button"
                onClick={() => copyToClipboard(jsonContent, "json")}
                className="btn btn-secondary btn-sm"
              >
                {copiedType === "json" ? <Check size={13} style={{ color: "var(--accent-emerald)" }} /> : <Copy size={13} />}
                <span>{copiedType === "json" ? "Copied" : "Copy"}</span>
              </button>
              <button
                type="button"
                onClick={() => downloadFile(jsonContent, "pipeline_result.json", "application/json")}
                className="btn btn-secondary btn-sm"
              >
                <Download size={13} />
                <span>.json</span>
              </button>
            </div>
          </div>

          <div
            className="code-block"
            style={{ maxHeight: "420px", overflowY: "auto", fontSize: "0.8rem" }}
          >
            {jsonContent}
          </div>
        </div>
      </div>
    </div>
  );
}
