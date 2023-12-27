import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/app/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "PixPursuit",
  description: "Image gallery app",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-900`}>
        <main className="max-w-6xl mx-auto">
          <Navbar />
          {children}
        </main>
      </body>
    </html>
  );
}
