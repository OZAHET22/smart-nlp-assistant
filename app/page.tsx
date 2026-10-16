"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { HeroBanner } from "@/components/HeroBanner";
import { EditorSection } from "@/components/EditorSection";
import { Stage1SpellTab } from "@/components/Stage1SpellTab";
import { Stage2SyntaxTab } from "@/components/Stage2SyntaxTab";
import { Stage3SemanticsTab } from "@/components/Stage3SemanticsTab";
import { Stage4DiscourseTab } from "@/components/Stage4DiscourseTab";
import { Stage5ExportTab } from "@/components/Stage5ExportTab";
import { BenchmarkStudioTab } from "@/components/BenchmarkStudioTab";
import { PipelineResult } from "@/lib/nlp/types";
import { runPipeline } from "@/lib/nlp/stage5-pipeline";
import { TEST_SAMPLES } from "@/lib/nlp/samples-data";
import { SpellCheck, GitBranch, Binary, MessageSquareShare, FileSpreadsheet, Activity, Sparkles } from "lucide-react";

export default function Home() {
  const initialSample = TEST_SAMPLES[0];
  const [inputText, setInputText] = useState<string>(initialSample.text);
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>("editor");
  const [engine, setEngine] = useState<"native" | "python">("native");

  // Run pipeline initially so page is pre-populated with rich data (no placeholders)
  useEffect(() => {
    const initialResult = runPipeline(initialSample.text);
    setResult(initialResult);
  }, []);

  const handleProcess = async () => {
    if (!inputText.trim()) return;
    setLoading(true);

    try {
      const response = await fetch("/api/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText, engine }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        // Fallback to client-side native execution
        const clientResult = runPipeline(inputText);
        setResult(clientResult);
      }
    } catch (err) {
      // Direct client fallback
      const clientResult = runPipeline(inputText);
      setResult(clientResult);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyCorrection = (original: string, corrected: string) => {
    const regex = new RegExp(`\\b${original}\\b`, "i");
    const updated = inputText.replace(regex, corrected);
    setInputText(updated);

    // Re-run pipeline on updated text
    const updatedResult = runPipeline(updated);
    setResult(updatedResult);
  };

  const handleApplyAll = () => {
    if (!result) return;
    let text = inputText;
    for (const corr of result.corrections) {
      const regex = new RegExp(`\\b${corr.original}\\b`, "gi");
      text = text.replace(regex, corr.corrected);
    }
    setInputText(text);
    const updatedResult = runPipeline(text);
    setResult(updatedResult);
  };

  const tabs = [
    { id: "editor", label: "Smart Editor & Diff", icon: Sparkles },
    { id: "stage1", label: "Stage 1: Spell & Levenshtein", icon: SpellCheck, count: result?.corrections.length },
    { id: "stage2", label: "Stage 2: Syntax & CYK Parser", icon: GitBranch, count: result?.sentence_parses.length },
    { id: "stage3", label: "Stage 3: Semantics & WSD", icon: Binary, count: result?.semantic_frames.length },
    { id: "stage4", label: "Stage 4: Discourse & Pragmatics", icon: MessageSquareShare, count: result?.discourse_relations.length },
    { id: "stage5", label: "Stage 5: Export Studio", icon: FileSpreadsheet },
    { id: "benchmarks", label: "Benchmarks Suite", icon: Activity, count: "10" },
  ];

  return (
    <div>
      <Header engine={engine} setEngine={setEngine} />

      <main className="container">
        <HeroBanner activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Navigation Tabs */}
        <div className="tabs-nav">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-btn ${isActive ? "active" : ""}`}
              >
                <Icon size={15} />
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span
                    style={{
                      fontSize: "0.68rem",
                      background: isActive ? "var(--accent-primary)" : "var(--bg-tertiary)",
                      color: isActive ? "#ffffff" : "var(--text-secondary)",
                      padding: "1px 6px",
                      borderRadius: "10px",
                    }}
                  >
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Tab Contents */}
        {activeTab === "editor" && (
          <EditorSection
            inputText={inputText}
            setInputText={setInputText}
            result={result}
            onProcess={handleProcess}
            loading={loading}
            onApplyCorrection={handleApplyCorrection}
            onApplyAll={handleApplyAll}
          />
        )}

        {activeTab === "stage1" && <Stage1SpellTab result={result} />}
        {activeTab === "stage2" && <Stage2SyntaxTab result={result} />}
        {activeTab === "stage3" && <Stage3SemanticsTab result={result} />}
        {activeTab === "stage4" && <Stage4DiscourseTab result={result} />}
        {activeTab === "stage5" && <Stage5ExportTab result={result} rawText={inputText} />}
        {activeTab === "benchmarks" && <BenchmarkStudioTab />}

        {/* Footer */}
        <footer style={{ margin: "60px 0 40px", borderTop: "1px solid var(--border-subtle)", paddingTop: "24px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px", color: "var(--text-muted)", fontSize: "0.8rem" }}>
          <div>
            <strong>Smart Reading & Writing Assistant</strong> • Enterprise NLP Pipeline
          </div>
          <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
            <span>Next.js 14 App Router</span>
            <span>•</span>
            <span>Zero-Dependency Vercel Deployment</span>
            <span>•</span>
            <a
              href="https://vercel.com"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "var(--accent-cyan)", textDecoration: "none" }}
            >
              Deploy on Vercel ▲
            </a>
          </div>
        </footer>
      </main>
    </div>
  );
}
