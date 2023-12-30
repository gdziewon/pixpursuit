"use client";

import { MagnifyingGlassIcon } from "@heroicons/react/24/solid";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useDebounce } from "use-debounce";

export default function Searcher({ search }) {
  const router = useRouter();
  const [text, setText] = useState(search);
  const [query] = useDebounce(text, 500);

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
        onChange={(e) => setText(e.target.value)}
        className="bg-gray-800 block w-full rounded-md border-0 py-1.5 pl-10 text-white ring-1 ring-inset ring-white placeholder:text-white focus:ring-2 focus:ring-inset focus:ring-white sm:text-sm sm:leading-6"
      />
    </div>
  );
}
