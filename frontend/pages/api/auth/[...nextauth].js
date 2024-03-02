import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"

async function refreshAccessToken(token) {
    try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/refresh`, {
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": `Bearer ${token.refreshToken}`,
            },
            method: "POST",
        })

        const refreshedTokens = await response.json()

        if (!response.ok) {
            throw refreshedTokens
        }

        return {
            ...token,
            accessToken: refreshedTokens.access_token,
            accessTokenExpires: Date.now() + 60 * 60 * 4 * 1000,
            refreshToken: refreshedTokens.refresh_token,
        }
    } catch (error) {
        console.log(error)

        return {
            ...token,
            error: "RefreshAccessTokenError",
        }
    }
}

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
                    return {
                        accessToken: user.access_token,
                        accessTokenExpires: Date.now() + 60 * 60 * 4 * 1000,
                        refreshToken: user.refresh_token,
                        username: user.username,
                    }
                }

                if (Date.now() < token.accessTokenExpires) {
                    return token
                }

                return refreshAccessToken(token)
            }
            catch (error) {
                console.error(error);
                return token;
            }
        },
        async session({ session, token }) {
            try {
                if (session?.user) {
                    session.accessToken = token.accessToken;
                    session.user.name = token.username;
                    session.expires = token.accessTokenExpires;
                    session.error = token.error;
                }
                return session;
            } catch (error) {
                console.error(error);
                return session;
            }
        }
    }
})
