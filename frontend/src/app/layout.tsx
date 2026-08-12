import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
// next/font/google's Jua wrapper only exposes a "latin" subset (no Hangul),
// and Google's CDN CSS splits Korean glyphs into many unicode-range chunks
// that don't reliably repaint once loaded. @fontsource ships single,
// unrestricted-range files instead, so Korean headings render immediately.
import "@fontsource/jua/latin-400.css";
import "@fontsource/jua/korean-400.css";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Payment Copilot",
  description: "결제 직전, 가장 유리한 카드와 간편결제를 추천합니다.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>{children}</body>
    </html>
  );
}
