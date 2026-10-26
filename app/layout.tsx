import type { Metadata, Viewport } from "next";
import "./globals.css";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f8fafc" },
    { media: "(prefers-color-scheme: dark)", color: "#07090e" },
  ],
};

export const metadata: Metadata = {
  title: "Smart Reading & Writing Assistant — Enterprise NLP Studio",
  description: "Advanced continuous NLP pipeline featuring Levenshtein edit distance, Brown corpus n-grams, CYK chart parsing, Lesk WSD, coreference resolution, and discourse pragmatics.",
  keywords: ["NLP", "Grammarly", "Spellchecker", "Levenshtein", "CYK Parser", "Word Sense Disambiguation", "Next.js", "Vercel", "Mobile Responsive"],
  authors: [{ name: "NLP Studio Team" }],
  applicationName: "Smart NLP Studio",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "Smart NLP Studio",
  },
  formatDetection: {
    telephone: false,
  },
  openGraph: {
    title: "Smart NLP Assistant — Next.js Enterprise Studio",
    description: "Full-stage continuous NLP assistant with explainable AI visualizations across all devices.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="mobile-web-app-capable" content="yes" />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
