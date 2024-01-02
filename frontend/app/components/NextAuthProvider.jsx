"use client";
import { SessionProvider } from "next-auth/react";

const NextAuthProvider = ({ children, pageProps }) => {
    return <SessionProvider session={pageProps?.session}>{children}</SessionProvider>;
};

export default NextAuthProvider;
