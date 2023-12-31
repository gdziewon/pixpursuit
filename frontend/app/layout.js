import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/app/components/Navbar";
import AlbumsPage from "@/app/albums/page";
import NextAuthProvider from "@/app/components/NextAuthProvider";
import router from "next/navigation";
const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "PixPursuit",
  description: "Image gallery app",
};

export default function RootLayout({ children, session }) {
  return (
      <NextAuthProvider session={session}>
    <html lang="en">
      <body className={`${inter.className} bg-gray-900 text-white`}>
        <main className="max-w-6xl mx-auto">
          <Navbar router={router} />
          {children}
        </main>
      </body>
    </html>
      </NextAuthProvider>
  );
}
