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
                try {
                    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/token`, {
                        method: 'POST',
                        body: new URLSearchParams(credentials),
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
                    });

                    const user = await res.json();

                    if (res.ok && user) {
                        return user;
                    } else {
                        console.error('Authorization failed');
                        return null;
                    }
                } catch (error) {
                    console.error(error);
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
            try {
                if (user) {
                    token.accessToken = user.access_token;
                    token.username = user.username;
                }
                return token;
            } catch (error) {
                console.error(error);
                return token;
            }
        },
        async session({ session, token }) {
            try {
                if (session?.user) {
                    session.accessToken = token.accessToken;
                    session.user.name = token.username;
                }
                return session;
            } catch (error) {
                console.error(error);
                return session;
            }
        }
    }
})
