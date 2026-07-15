import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "@/app/globals.css";
import { Providers } from "@/components/providers";

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" });

export const metadata: Metadata = {
  title: { default: "Signal SEO", template: "%s Â· Signal SEO" },
  description: "Shopify SEO intelligence with human-approved audits, agents, and growth monitoring.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geist.variable} grain min-h-screen font-sans`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

