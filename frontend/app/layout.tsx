import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Layout/Sidebar";

export const metadata: Metadata = {
  title: "Book Recommendations",
  description: "Discover your next great read",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex">
        <Sidebar />
        <main className="flex-1 flex flex-col">{children}</main>
      </body>
    </html>
  );
}
