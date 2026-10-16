import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart Reading & Writing Assistant — Enterprise NLP Studio",
  description: "Advanced NLP pipeline featuring Levenshtein edit distance, Brown corpus n-grams, CYK chart parsing, Lesk WSD, coreference resolution, and discourse pragmatics.",
  keywords: ["NLP", "Grammarly", "Spellchecker", "Levenshtein", "CYK Parser", "Word Sense Disambiguation", "Next.js", "Vercel"],
  authors: [{ name: "NLP Studio Team" }],
  openGraph: {
    title: "Smart NLP Assistant — Next.js Enterprise Studio",
    description: "Full-stage continuous NLP assistant with explainable AI visualizations.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-theme="dark">
      <body>
        {children}
      </body>
    </html>
  );
}
