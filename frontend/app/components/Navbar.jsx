"use client";

import Link from "next/link";
import "@fortawesome/fontawesome-svg-core/styles.css";
import { config } from "@fortawesome/fontawesome-svg-core";
import { useSession, signIn, signOut } from 'next-auth/react';
import React from 'react';

config.autoAddCss = false;

export default function Navbar() {
  const { data: session } = useSession();

  return (
      <nav className="bg-gray-900 p-6">
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
              <Link href="/gallery">
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
                  <button onClick={() => signOut()}>Log out</button>
                </div>
            ) : (
                <div className="text-white text-lg hover:text-gray-300 px-4">
                  <button onClick={() => signIn()}>Log in</button>
                </div>
            )}
          </div>
          </div>
        </ul>
      </nav>
  );
}
