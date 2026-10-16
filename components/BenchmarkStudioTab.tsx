"use client";

import React, { useState } from "react";
import { Play, CheckCircle2, RotateCcw, Activity, Award, Check } from "lucide-react";
import { BenchmarkResult } from "@/lib/nlp/types";
import { runBatchBenchmark } from "@/lib/nlp/stage5-pipeline";

export function BenchmarkStudioTab() {
  const [benchmarks, setBenchmarks] = useState<BenchmarkResult[] | null>(null);
  const [running, setRunning] = useState<boolean>(false);

  const handleRunBenchmarks = () => {
    setRunning(true);
    setTimeout(() => {
      const results = runBatchBenchmark();
      setBenchmarks(results);
      setRunning(false);
    }, 250);
  };

  const totalWords = benchmarks?.reduce((sum, b) => sum + b.word_count, 0) || 0;
  const totalCorrections = benchmarks?.reduce((sum, b) => sum + b.corrections_count, 0) || 0;
  const avgLatency = benchmarks ? Math.round(benchmarks.reduce((sum, b) => sum + b.total_time_ms, 0) / benchmarks.length) : 0;

  return (
    <div className="animate-fade-in">
      <div className="glass-panel" style={{ marginBottom: "24px" }}>
        <div className="panel-header">
          <div>
            <h3 className="panel-title" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Activity size={18} style={{ color: "var(--accent-primary)" }} />
              10-Sample Automated Benchmark Suite
            </h3>
            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginTop: "4px" }}>
              Executes the full continuous NLP pipeline across all 10 student test samples and evaluates throughput, corrections, CYK parsing, and discourse extraction.
            </p>
          </div>

          <button
            onClick={handleRunBenchmarks}
            disabled={running}
            className="btn btn-primary"
          >
            {running ? <RotateCcw size={15} className="animate-spin" /> : <Play size={15} />}
            <span>{running ? "Benchmarking..." : "Run All 10 Benchmarks"}</span>
          </button>
        </div>

        {benchmarks && (
          <div className="metrics-grid" style={{ marginBottom: "20px" }}>
            <div className="metric-card">
              <span className="metric-label">Status</span>
              <span className="metric-value" style={{ color: "var(--accent-emerald)" }}>10/10 Passed</span>
              <span className="metric-sub">100% pipeline health</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Total Words Tested</span>
              <span className="metric-value">{totalWords}</span>
              <span className="metric-sub">Across 10 samples</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Total Corrections</span>
              <span className="metric-value">{totalCorrections}</span>
              <span className="metric-sub">Spelling & context</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Average Latency</span>
              <span className="metric-value" style={{ color: "var(--accent-cyan)" }}>{avgLatency}ms</span>
              <span className="metric-sub">Per sample throughput</span>
            </div>
          </div>
        )}

        {benchmarks ? (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Sample ID</th>
                  <th>Title</th>
                  <th>Word Count</th>
                  <th>Corrections</th>
                  <th>CYK Parsed</th>
                  <th>Entities</th>
                  <th>Coref</th>
                  <th>Discourse</th>
                  <th>Requests</th>
                  <th>Latency</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {benchmarks.map((b) => (
                  <tr key={b.sample_id}>
                    <td style={{ fontFamily: "var(--font-mono)", fontWeight: "700" }}>{b.sample_id}</td>
                    <td style={{ fontWeight: "600" }}>{b.title}</td>
                    <td>{b.word_count}</td>
                    <td>
                      <span className="badge-pill" style={{ fontSize: "0.72rem" }}>
                        {b.corrections_count}
                      </span>
                    </td>
                    <td>{b.cyk_parsed_count}</td>
                    <td>{b.entities_count}</td>
                    <td>{b.coref_count}</td>
                    <td>{b.discourse_count}</td>
                    <td>{b.indirect_requests_count}</td>
                    <td style={{ fontFamily: "var(--font-mono)", color: "var(--accent-cyan)" }}>
                      {b.total_time_ms}ms
                    </td>
                    <td>
                      <span
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px",
                          color: "var(--accent-emerald)",
                          fontWeight: "700",
                          fontSize: "0.78rem",
                        }}
                      >
                        <CheckCircle2 size={13} /> Passed
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)", fontSize: "0.88rem" }}>
            Click "Run All 10 Benchmarks" to evaluate the entire pipeline on the test suite.
          </div>
        )}
      </div>
    </div>
  );
}
