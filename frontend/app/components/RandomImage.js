"use client";

import { useState, useEffect } from "react";
import Image from "next/legacy/image";
import { Suspense } from "react";
import Loading from "@/app/loading";

function RandomImage() {
  const [image, setImage] = useState(null);

  useEffect(() => {
    const fetchRandomImage = async () => {
      try {
        const response = await fetch("/api/randomImages");
        if (response.ok) {
          const data = await response.json();
          setImage(data);
        } else {
          console.error("Failed to fetch random image");
        }
      } catch (error) {
        console.error("Error fetching random image:", error);
      }
    };

    fetchRandomImage();
  }, []);

  useEffect(() => {
    // Auto-swap image after 10 seconds
    const timer = setInterval(fetchRandomImage, 100000);

    return () => {
      clearInterval(timer);
    };
  }, []);

  const fetchRandomImage = async () => {
    try {
      const response = await fetch("/api/randomImages");
      if (response.ok) {
        const data = await response.json();
        setImage(data);
      } else {
        console.error("Failed to fetch random image");
      }
    } catch (error) {
      console.error("Error fetching random image:", error);
    }
  };
  return (
    <div className="bg-indigo-800 bg-opacity-25 p-8 shadow-lg rounded-2xl">
      <div className="container mx-auto flex items-center space-x-8">
        {image ? (
          <div className="w-1/2">
            <Suspense fallback={<Loading />}>
              <Image
                src={image.image_url}
                alt={image.description}
                width={400}
                height={400}
                layout={"responsive"}
                className="rounded-lg"
              />
            </Suspense>
          </div>
        ) : (
          <div className="w-1/2 h-400px bg-gray-200 rounded-lg"></div>
        )}
        <div className="w-1/2">
          <p className="text-2xl font-semibold mb-4">
            {image ? image.description : "Loading..."}
          </p>
          <p className="text-gray-600">
            {image
              ? "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus gravida purus ac ex volutpat, eu posuere libero congue."
              : ""}
          </p>
        </div>
      </div>
    </div>
  );
}

export default RandomImage;
