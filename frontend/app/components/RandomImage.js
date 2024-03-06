"use client";

import { useState, useEffect } from "react";
import Image from "next/legacy/image";
import Loading from "@/app/loading";
import { Suspense } from "react";
import ErrorWindow from '@/utils/ErrorWindow';
import { getImages } from "@/utils/getImages";

export default function RandomImage() {
  const [images, setImages] = useState(Array(10).fill(null));
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    fetchImages();
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 10000);

    return () => clearInterval(timer);
  }, [images]);

  const fetchImages = async () => {
    try {
      const data = await getImages({ limit: 10, sort: "mostPopular", page: 1, query: "" });
      setImages(data);
    } catch (error) {
      console.error("Error fetching images:", error);
      setErrorMessage('Error fetching images');
    }
  };

  return (
      <div className="bg-indigo-400 bg-opacity-25 p-8 shadow-lg rounded-2xl">
        {errorMessage && <ErrorWindow message={errorMessage} clearMessage={() => setErrorMessage(null)} />}
        <div className="container mx-auto flex items-center space-x-8">
          {Array.isArray(images) ? (
              <div className={`w-full ${isLoading ? "opacity-0" : "opacity-100"}`}>
                {[0, 1, 2, 3, 4].map((offset, i) => {
                  const index = (currentImageIndex + offset) % images.length;
                  return images[index] ? (
                      <Suspense fallback={<Loading/>}>
                        <Image
                            key={index}
                            src={images[index].image_url}
                            alt={images[index].description}
                            width={i === 2 ? 450 : i === 1 || i ===3 ? 200 : 100}
                            height={i === 2 ? 500 : i === 1 || i ===3 ? 495 : 490}
                            objectFit="cover"
                            onLoad={() => setIsLoading(false)}
                            className={i === 0 ? 'image-0' : i === 1 ? 'image-1' : i === 2 ? 'image-2' : i === 3 ? 'image-3' : i === 4 ? 'image-4' : ''}
                            style={{
                              position: 'absolute',
                              zIndex: 5 - Math.abs(i - 2),
                              transform: i === 0 || i === 1 ? 'translateX(0.5%) translateY(-3px)' : i === 3 || i === 4 ? 'translateX(-0.5%) translateY(-3px)' : 'none',
                              borderRadius: '10px',
                            }}
                        />
                      </Suspense>
                  ) : (
                      <div key={index} className="h-400px bg-gray-200 rounded-lg"></div>
                  );
                })}
              </div>
          ) : (
              <p>Error: Images is not an array.</p>
          )}
        </div>
      </div>
  );
}