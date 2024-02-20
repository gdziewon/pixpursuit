"use client";
import { SessionProvider } from "next-auth/react";

const NextAuthProvider = ({ children, pageProps }) => {
    try {
        return <SessionProvider session={pageProps?.session}>{children}</SessionProvider>;
    } catch (error) {
        console.error("Error occurred while providing the session: ", error);
        return <div>An error occurred. Please try again later.</div>;
    }
};

export default NextAuthProvider;
