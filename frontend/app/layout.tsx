import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Geist } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";
import { TopNav } from "@/components/dashboard/TopNav";
import { SystemStatusFooter } from "@/components/dashboard/SystemStatusFooter";
import { PageContainer } from "@/components/ui/PageContainer";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
});

export const metadata: Metadata = {
  title: "WEBMORPH",
  description: "A reliability layer for web data.",
};

import { DemoProvider } from "@/components/demo/DemoContext";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={cn(inter.variable, jetbrainsMono.variable, "font-sans")}>
      <body className="min-h-screen bg-[#F8FAFC] flex flex-col font-sans text-[#111827]">
        <DemoProvider>
          <TopNav />
          <main className="flex-1 w-full flex flex-col">
            <PageContainer className="flex-1 flex flex-col">
              {children}
            </PageContainer>
          </main>
          <SystemStatusFooter />
        </DemoProvider>
      </body>
    </html>
  );
}
