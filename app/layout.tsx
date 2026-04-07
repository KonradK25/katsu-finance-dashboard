import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Katsu Finance - AI-Powered Financial Dashboard",
  description: "Your personalized financial intelligence platform with real-time market data, news, and AI analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
