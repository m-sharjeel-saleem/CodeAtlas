import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";

import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "CodeAtlas — Agentic Codebase Intelligence",
  description:
    "Point CodeAtlas at any repository. A team of AI agents indexes it, then lets you chat with the code, map its architecture, and run a verified multi-agent review.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable} dark`}>
      <body className="min-h-screen bg-bg font-sans antialiased">
        <div className="bg-mesh pointer-events-none fixed inset-0 -z-10" />
        <div className="bg-grid pointer-events-none fixed inset-0 -z-10 opacity-40" />
        {children}
      </body>
    </html>
  );
}
