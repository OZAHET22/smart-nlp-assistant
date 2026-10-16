import { NextRequest, NextResponse } from "next/server";
import { runPipeline } from "@/lib/nlp/stage5-pipeline";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { text, engine } = body;

    if (!text || typeof text !== "string") {
      return NextResponse.json(
        { error: "Field 'text' must be a non-empty string" },
        { status: 400 }
      );
    }

    // Optional Python backend delegation if configured
    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL;
    if (engine === "python" && pythonBackendUrl) {
      try {
        const pyRes = await fetch(`${pythonBackendUrl}/process`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
        if (pyRes.ok) {
          const pyData = await pyRes.json();
          return NextResponse.json({ ...pyData, source: "python_backend" });
        }
      } catch (err) {
        console.warn("Python backend unreachable, falling back to native engine:", err);
      }
    }

    // High performance native Vercel Edge/Serverless pipeline execution
    const result = runPipeline(text);
    return NextResponse.json({
      ...result,
      source: "native_edge_engine",
      status: "success",
    });
  } catch (err: any) {
    console.error("Pipeline execution error:", err);
    return NextResponse.json(
      { error: "Internal processing error", message: err.message },
      { status: 500 }
    );
  }
}
