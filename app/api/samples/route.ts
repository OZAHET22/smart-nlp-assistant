import { NextResponse } from "next/server";
import { TEST_SAMPLES } from "@/lib/nlp/samples-data";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({
    total: TEST_SAMPLES.length,
    samples: TEST_SAMPLES,
  });
}
