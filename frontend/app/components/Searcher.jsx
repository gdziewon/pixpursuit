"use client";

import { MagnifyingGlassIcon } from "@heroicons/react/24/solid";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useDebounce } from "use-debounce";

export default function Searcher({ search }) {
  const router = useRouter();
  const [text, setText] = useState(search);
  const [query] = useDebounce(text, 500);
  const [suggestions, setSuggestions] = useState([]); // State for suggestions
  const [error, setError] = useState(null);

  const initialRender = useRef(true);

  useEffect(() => {
    if (initialRender.current) {
      initialRender.current = false;
      return;
    }
  });

  useEffect(() => {
    if (!query) {
      router.push(`/gallery`);
    } else {
      router.push(`/gallery?search=${query}`);
    }
  }, [query, router]);

  // Function to fetch search suggestions from the server
  const fetchSuggestions = async (input) => {
    try {
      const response = await fetch(`/api/searchSuggestions?query=${input}`);
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data);
      } else {
        console.error("Failed to fetch search suggestions");
        setSuggestions([]); // Clear suggestions on fetch failure
        setError("Failed to fetch search suggestions");
      }
    } catch (error) {
      console.error("Error fetching search suggestions:", error);
      setSuggestions([]); // Clear suggestions on error
      setError(error.toString());
    }
  };

  // Handle input change and fetch suggestions
  const handleInputChange = (e) => {
    setText(e.target.value);
    fetchSuggestions(e.target.value);
  };

  return (
    <div className="bg-black relative rounded-md shadow-sm">
      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
        <MagnifyingGlassIcon
          className="h-5 w-5 text-white"
          aria-hidden="true"
        />
      </div>
      <input
        value={text}
        placeholder="Search for tags, description..."
        onChange={handleInputChange}
        className="bg-gray-800 block w-full rounded-md border-0 py-1.5 pl-10 text-white ring-1 ring-inset ring-white placeholder:text-white focus:ring-2 focus:ring-inset focus:ring-white sm:text-sm sm:leading-6"
      />
      {suggestions.length > 0 && (
        <ul className="absolute left-0 mt-2 w-full bg-gray-800 rounded-md shadow-lg z-10">
          {suggestions.map((suggestion, index) => (
            <li
              key={index}
              onClick={() => {
                setText(suggestion);
                setSuggestions([]); // Clear suggestions when a suggestion is clicked
              }}
              className="cursor-pointer px-4 py-2 text-white hover:bg-gray-700"
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
      {error && <div className="text-red-500">{error}</div>}
    </div>
  );
}
