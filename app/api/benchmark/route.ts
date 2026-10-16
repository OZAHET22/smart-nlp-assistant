import { NextResponse } from "next/server";
import { runBatchBenchmark } from "@/lib/nlp/stage5-pipeline";

export const dynamic = "force-dynamic";

export async function GET() {
  const benchmarkResults = runBatchBenchmark();
  return NextResponse.json({
    total_tested: benchmarkResults.length,
    timestamp: new Date().toISOString(),
    results: benchmarkResults,
  });
}
