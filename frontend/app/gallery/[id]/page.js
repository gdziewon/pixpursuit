"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { PlusIcon } from "@heroicons/react/24/solid";
import getSingleImage from "@/utils/getSingleImage";
import Loading from "@/app/loading";

export default function ImagePage({ params }) {
  const [image, setImage] = useState(null);
  const [newTag, setNewTag] = useState(null);
  const id = params.id;

  useEffect(() => {
    const fetchImage = async () => {
      const imageData = await getSingleImage(id);
      setImage(imageData);
    };

    fetchImage();
  }, [id]);

  // Function to handle adding user-defined tags
  const handleAddTag = async () => {
    try {
      const requestBody = JSON.stringify({
        inserted_id: id,
        tags: [newTag], // Assuming you are adding a single tag at a time
      });

      // Make a POST request to your server endpoint (/add-user-tag)
      const response = await fetch("/api/add-user-tag", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: requestBody,
      });

      if (response.ok) {
        const responseData = await response.json();
        // Handle the response message as needed
        console.log(responseData.message);
        setImage(responseData.updatedImage); // Update the image data if necessary
        setNewTag(""); // Clear the input field
      } else {
        // Handle error response
        console.error("Failed to add tag:", response.statusText);
        // You can display an error message or handle the error in another way
      }
    } catch (error) {
      console.error("Error adding tag:", error);
    }
  };

  if (!image) {
    return <Loading />;
  }

  return (
    <main className="flex p-6">
      <div className="w-1/2">
        <div className="flex justify-center flex-col">
          <Image
            src={image.image_url}
            alt={image.description}
            width={800}
            height={800}
            quality={100}
            className="rounded-lg"
          />
          <p className="">Taken: {image.metadata.DateTime}</p>
          <p>Added by: {image.added_by}</p>
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
        <div className="flex flex-wrap gap-2 mb-4">
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
        <div className="flex items-center">
          <input
            type="text"
            className="rounded border bg-gray-900 text-white px-3 py-1 text-sm shadow-md"
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
          />
          <button
            className="inline-flex items-center bg-blue-200 rounded-full px-3 py-1 text-sm font-semibold text-blue-700 ml-2 hover:bg-blue-300 transition-colors duration-200 ease-in-out"
            onClick={handleAddTag}
          >
            <PlusIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    </main>
  );
}
