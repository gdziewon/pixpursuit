import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"

export default NextAuth({
    providers: [
        CredentialsProvider({
            name: 'Credentials',
            credentials: {
                username: { label: "Username", type: "text", placeholder: "jsmith" },
                password: { label: "Password", type: "password" }
            },
            authorize: async (credentials) => {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/token`, {
                    method: 'POST',
                    body: new URLSearchParams(credentials),
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
                });

                const user = await res.json();

                if (res.ok && user) {
                    return user;
                } else {
                    return null;
                }
            }
        })
    ],
    session: {
        strategy:"jwt"
    },
    callbacks: {
        async jwt({ token, user }) {

            if (user) {
                token.accessToken = user.access_token;
                token.username = user.username;
            }
            return token;
        }
        ,
        async session({ session, token }) {
            if (session?.user) {
                session.accessToken = token.accessToken;
                session.user.name = token.username;
            }
            return session;
        }
    }
})
