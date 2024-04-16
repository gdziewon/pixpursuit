import { MagnifyingGlassIcon } from "@heroicons/react/24/solid";
import { useState } from "react";
import { useRouter } from "next/navigation";
import ErrorWindow from "@/utils/ErrorWindow";

/**
 * Searcher component.
 *
 * @param {Object} props - The props.
 * @param {string} props.search - The initial search text.
 * @returns {JSX.Element} - The rendered JSX element.
 */
export default function Searcher({ search }) {
  const router = useRouter();
  const [text, setText] = useState(search);
  const [suggestions, setSuggestions] = useState([]);
  const [errorMessage, setErrorMessage] = useState(null);


  const fetchSuggestions = async (input) => {
    try {
      const response = await fetch(`/api/searchSuggestions?query=${input}`);
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data);
      } else {
        setErrorMessage("Failed to fetch search suggestions");
      }
    } catch (error) {
      setErrorMessage("Error fetching search suggestions");
    }
  };


  const handleInput = (e) => {
    setText(e.target.value);
    fetchSuggestions(e.target.value);
    if (e.key === "Enter") {
      if (!e.target.value.trim()) {
        router.push(`/gallery`);
      } else {
        const params = new URLSearchParams({
          page: 1,
          search: e.target.value,
        });
        router.push(`/gallery?${params.toString()}`);
      }
    }
  };


  const handleSuggestionClick = (suggestion) => {
    setText(suggestion);
    setSuggestions([]);
    const params = new URLSearchParams({
      page: 1,
      search: suggestion,
    });
    router.push(`/gallery?${params.toString()}`);
  };


  const handleInputBlur = () => {
    setTimeout(() => {
      setSuggestions([]);
    }, 200);
  };

  return (
    <div className="bg-black relative rounded-md shadow-sm">
      {errorMessage && (
        <ErrorWindow
          message={errorMessage}
          clearMessage={() => setErrorMessage(null)}
        />
      )}
      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
        <MagnifyingGlassIcon
          className="h-5 w-5 text-white"
          aria-hidden="true"
        />
      </div>
      <input
        value={text}
        placeholder="Search for tags, description..."
        onChange={handleInput}
        onKeyDown={handleInput}
        onBlur={handleInputBlur}
        className="bg-gray-800 block w-full rounded-md border-0 py-1.5 pl-10 text-white ring-1 ring-inset ring-white placeholder:text-white focus:ring-2 focus:ring-inset focus:ring-white sm:text-sm sm:leading-6"
      />
      {suggestions.length > 0 && (
        <ul className="absolute left-0 mt-2 w-full bg-gray-800 rounded-md shadow-lg z-10">
          {suggestions.map((suggestion, index) => (
            <li
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="cursor-pointer px-4 py-2 text-white hover:bg-gray-700"
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
