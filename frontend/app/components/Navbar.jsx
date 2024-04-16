"use client";

import Link from "next/link";
import "@fortawesome/fontawesome-svg-core/styles.css";
import { config } from "@fortawesome/fontawesome-svg-core";
import { useSession, signIn, signOut } from 'next-auth/react';
import React, { useState, useEffect } from 'react';
import ErrorWindow from '@/utils/ErrorWindow';

config.autoAddCss = false;

/**
 * Navbar component.
 *
 * @returns {JSX.Element} - The rendered JSX element.
 */
function Navbar() {
    const { data: session } = useSession();
    const [errorMessage, setErrorMessage] = useState(null);

    /**
     * Checks if there was an error refreshing the access token and signs out if there was.
     */
    useEffect(() => {
        if (session?.error === "RefreshAccessTokenError") {
            signOut();
        }
    }, [session]);

    /**
     * Handles the sign-in process.
     *
     * @returns {Promise<void>}
     */
    const handleSignIn = async () => {
        try {
            await signIn();
        } catch (error) {
            console.error('Error signing in:', error);
            setErrorMessage('Error signing in');
        }
    };

    /**
     * Handles the sign-out process.
     *
     * @returns {Promise<void>}
     */
    const handleSignOut = async () => {
        try {
            await signOut();
        } catch (error) {
            console.error('Error signing out:', error);
            setErrorMessage('Error signing out');
        }
    };

    return (
        <nav className="bg-gray-900 p-6">
            {errorMessage && <ErrorWindow message={errorMessage} clearMessage={() => setErrorMessage(null)} />}
            {session?.user && (
                <div className="text-gray-300 text-sm font-normal px-4 mt-[-10px]">
                    Signed in as <span className="font-bold">{session.user.name}</span>
                </div>
            )}
            <ul className="flex justify-center items-center">
                <div className="flex justify-center items-center">
                    <li>
                        <Link href="/">
                            <div className="text-white text-lg hover:text-gray-300 px-4">
                                Home
                            </div>
                        </Link>
                    </li>
                    <li>
                        <Link href="/gallery?page=1">
                            <div className="text-white text-lg hover:text-gray-300 px-4">
                                Gallery
                            </div>
                        </Link>
                    </li>
                    <li>
                        <Link href="/albums">
                            <div className="text-white text-lg hover:text-gray-300 px-4">
                                Albums
                            </div>
                        </Link>
                    </li>
                    <div className="login-section">
                        {session?.user ? (
                            <div className="text-white text-lg hover:text-gray-300 px-4">
                                <button onClick={handleSignOut}>Log out</button>
                            </div>
                        ) : (
                            <>
                                <div className="text-white text-lg hover:text-gray-300 px-4">
                                    <button onClick={handleSignIn}>Log in</button>
                                    <span className="text-gray-500 mx-2">or</span>
                                </div>
                                <li>
                                    <Link href="/register">
                                        <div className="text-white text-lg hover:text-gray-300 px-4">
                                            Register
                                        </div>
                                    </Link>
                                </li>
                            </>
                        )}
                    </div>
                </div>
            </ul>
        </nav>
    );
}

export default Navbar;