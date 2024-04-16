import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/app/components/Navbar";
import NextAuthProvider from "@/app/components/NextAuthProvider";
import { SelectedItemsProvider } from '/utils/SelectedItemsContext';
import router from "next/navigation";
const inter = Inter({ subsets: ["latin"] });


export const metadata = {
  title: "PixPursuit",
  description: "Image gallery app",
};

/**
 * Root layout component.
 *
 * @param {Object} props - The props.
 * @param {React.ReactNode} props.children - The children to be rendered.
 * @param {Object} props.session - The session object.
 * @returns {JSX.Element} - The rendered JSX element.
 */
export default function RootLayout({ children, session }) {
  try {
    /**
     * Wraps the children with the NextAuth provider and the SelectedItems provider.
     * Renders the Navbar and the children.
     */
    return (
        <NextAuthProvider session={session}>
          <SelectedItemsProvider>
            <html lang="en">
            <body className={`${inter.className} bg-gray-900 text-white`}>
            <main className="max-w-6xl mx-auto">
              <Navbar router={router} />
              {children}
            </main>
            </body>
            </html>
          </SelectedItemsProvider>
        </NextAuthProvider>
    );
  } catch (error) {
    console.error("Error rendering RootLayout:", error);
    return <div>Error occurred while rendering. Please try again.</div>;
  }
}
