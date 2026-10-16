import { NextRequest, NextResponse } from "next/server";
import { getLevenshteinMatrix } from "@/lib/nlp/stage1-spellcheck";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const { word1, word2 } = await req.json();

    if (!word1 || !word2) {
      return NextResponse.json(
        { error: "Parameters 'word1' and 'word2' are required" },
        { status: 400 }
      );
    }

    const matrixData = getLevenshteinMatrix(String(word1), String(word2));
    return NextResponse.json(matrixData);
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
