"use client";

import Link from "next/link";
import "@fortawesome/fontawesome-svg-core/styles.css";
import { config } from "@fortawesome/fontawesome-svg-core";

config.autoAddCss = false;

export default function Navbar() {
  return (
    <nav className="bg-gray-900 p-6">
      <ul className="flex justify-center items-center">
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
      </ul>
    </nav>
  );
}
