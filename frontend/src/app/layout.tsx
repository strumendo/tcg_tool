import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";
import { QueryProvider } from "@/providers/QueryProvider";

export const metadata: Metadata = {
  title: "TCG Tool - Pokemon Deck Analyzer",
  description:
    "Pokemon Trading Card Game deck analysis platform with AI-powered insights",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt">
      <body className="min-h-screen bg-gray-50">
        <QueryProvider>
          <Navbar />
          <main className="container mx-auto px-4 py-6">{children}</main>
        </QueryProvider>
      </body>
    </html>
  );
}
