"use client";

import { useState, useEffect } from "react";
import Image from "next/legacy/image";
import Loading from "@/app/loading";
import { Suspense } from "react";

export default function RandomImage() {
  const [currentImage, setCurrentImage] = useState(null);
  const [nextImage, setNextImage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const getRandomLyric = () => {
    const taylorSwiftLyrics = [
      "Karma is the guy on the screen coming straight home to me",
      "Lord, what will become of me / Once I've lost my novelty?",
      "You call me up again just to break me like a promise / So casually cruel in the name of being honest",
      "I'm captivated by you, baby, like a fireworks show",
      "You made a rebel of a careless man's careful daughter / You are the best thing that's ever been mine",
    ];

    const randomIndex = Math.floor(Math.random() * taylorSwiftLyrics.length);
    return taylorSwiftLyrics[randomIndex];
  };

  useEffect(() => {
    fetchRandomImage();
  }, []);

  useEffect(() => {
    if (nextImage) {
      const timer = setTimeout(() => {
        setCurrentImage(nextImage);
        fetchRandomImage();
      }, 8000);

      return () => clearTimeout(timer);
    }
  }, [nextImage]);

  const fetchRandomImage = async () => {
    try {
      const response = await fetch("/api/randomImages");
      if (response.ok) {
        const data = await response.json();
        setNextImage(data); // Store the next image
      } else {
        console.error("Failed to fetch random image");
      }
    } catch (error) {
      console.error("Error fetching random image:", error);
      setError(error.message);
    }
  };

  return (
      <div className="bg-indigo-400 bg-opacity-25 p-8 shadow-lg rounded-2xl">
        {error ? (
                <div>Error: {error}</div>
            ) : (
        <div className="container mx-auto flex items-center space-x-8">
          {currentImage ? (
              <div className={`w-1/2 ${isLoading ? "opacity-0" : "opacity-100"}`}>
                <Suspense fallback={<Loading />}>
                  <Image
                      src={currentImage.image_url}
                      alt={currentImage.description}
                      width={400}
                      height={400}
                      layout={"responsive"}
                      className={`rounded-lg transition-opacity duration-500 ${
                          isLoading ? "" : "ease-in"
                      }`}
                      onLoad={() => setIsLoading(false)}
                  />
                </Suspense>
              </div>
          ) : (
              <div className="w-1/2 h-400px bg-gray-200 rounded-lg"></div>
          )}
          <div className="w-1/2">
            <p className="text-2xl font-semibold mb-4">
              {currentImage ? currentImage.description || getRandomLyric() : "Loading..."}
            </p>
          </div>
        </div>
        )}
      </div>
  );
}
