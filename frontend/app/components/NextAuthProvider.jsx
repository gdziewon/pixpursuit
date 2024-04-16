"use client";
import { SessionProvider } from "next-auth/react";

/**
 * NextAuth provider component.
 *
 * @param {Object} props - The props.
 * @param {React.ReactNode} props.children - The children to be rendered.
 * @param {Object} props.pageProps - The page props.
 * @returns {JSX.Element} - The rendered JSX element.
 */
const NextAuthProvider = ({ children, pageProps }) => {
    try {
        /**
         * Provides the session to the children.
         */
        return <SessionProvider session={pageProps?.session}>{children}</SessionProvider>;
    } catch (error) {
        console.error("Error occurred while providing the session: ", error);
        /**
         * Returns an error message if an error occurred.
         */
        return <div>An error occurred. Please try again later.</div>;
    }
};

export default NextAuthProvider;
