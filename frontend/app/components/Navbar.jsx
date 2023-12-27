import Link from "next/link";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUpload } from "@fortawesome/free-solid-svg-icons";
import "@fortawesome/fontawesome-svg-core/styles.css";
import { config } from "@fortawesome/fontawesome-svg-core";

config.autoAddCss = false; // Prevent FontAwesome from adding its styles automatically

export default function Navbar() {
  return (
    <nav className="bg-gray-900 p-6">
      <ul className="flex justify-between items-center">
        <li>
          <Link href="/">
            <div className="text-white text-lg hover:text-gray-300">Home</div>
          </Link>
        </li>
        <li>
          <Link href="/gallery">
            <div className="text-white text-lg hover:text-gray-300">
              Gallery
            </div>
          </Link>
        </li>
        <li className="flex items-center">
          <input
            type="text"
            placeholder="Search..."
            className="mr-6 pl-2 py-1 rounded-md"
          />
          <button className="bg-black hover:bg-gray-600 text-white font-bold py-2 px-4 rounded flex items-center">
            <FontAwesomeIcon icon={faUpload} className="text-white mr-2" />
            Upload
          </button>
        </li>
      </ul>
    </nav>
  );
}
