"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { PlusIcon } from "@heroicons/react/24/solid";
import getSingleImage from "@/utils/getSingleImage";

export default function ImagePage({ params }) {
  const [image, setImage] = useState(null);
  const id = params.id;

  useEffect(() => {
    const fetchImage = async () => {
      const imageData = await getSingleImage(id);
      setImage(imageData);
    };

    fetchImage();
  }, [id]);

  if (!image) {
    return <div>Loading...</div>;
  }

  return (
    <main className="flex p-6">
      <div className="w-1/2">
        <div className="flex justify-center">
          <Image
            src={image.image_url}
            alt={image.description}
            width={800}
            height={800}
            quality={100}
            className="rounded-lg"
          />
        </div>
      </div>
      <div className="w-1/2 pl-6">
        <h1 className="text-3xl font-bold text-teal-100 dark:text-white mb-4">
          Photo description:
        </h1>
        <h1 className="text-2xl text-gray-900 dark:text-white mb-4">
          {image.description}
        </h1>
        <h1 className="text-3xl font-bold text-teal-100 dark:text-white mb-4">
          Tags:
        </h1>

        <div className="flex flex-wrap gap-2 mb-4">
          {image &&
            Array.isArray(image.auto_tags) &&
            image.auto_tags.map((tag, index) => (
              <span
                key={index}
                className="inline-block bg-blue-200 rounded-full px-3 py-1 text-sm font-semibold text-blue-700 mr-2"
              >
                {tag}
              </span>
            ))}
        </div>
        <div className="flex flex-wrap gap-2">
          {image &&
            Array.isArray(image.user_tags) &&
            image.user_tags.map((tag, index) => (
              <span
                key={index}
                className="inline-block bg-green-200 rounded-full px-3 py-1 text-sm font-semibold text-green-700 mr-2"
              >
                {tag}
              </span>
            ))}
        </div>
        <button
          className="inline-flex items-center bg-blue-200 rounded-full px-3 py-1 text-sm font-semibold text-blue-700 mr-2"
          onClick={() => {
            alert("Feature coming soon!");
          }}
        >
          <PlusIcon className="h-5 w-5" />
        </button>
      </div>
    </main>
  );
}
