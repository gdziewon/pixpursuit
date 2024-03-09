"use client";

import { useState, useEffect } from "react";
import Image from "next/legacy/image";
import Loading from "@/app/loading";
import { Suspense } from "react";
import ErrorWindow from '@/utils/ErrorWindow';
import { getImages } from "@/utils/getImages";
import { IoIosArrowBack, IoIosArrowForward } from 'react-icons/io';

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
      const data = await getImages({ limit: 5, sort: "mostPopular", page: 1, query: "" });
      setImages(data);
    } catch (error) {
      console.error("Error fetching images:", error);
      setErrorMessage('Error fetching images');
    }
  };

  const handlePrev = () => {
    setCurrentImageIndex((prevIndex) => (prevIndex - 1 + images.length) % images.length);
  };

  const handleNext = () => {
    setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
  };

  const handleCircleClick = (index) => {
    setCurrentImageIndex(index);
  };

  return (
      <>
        <h1 className="text-3xl font-bold mb-4">PixPursuit</h1>
        <div className="bg-indigo-400 bg-opacity-25 p-8 shadow-lg rounded-2xl">
          {errorMessage && <ErrorWindow message={errorMessage} clearMessage={() => setErrorMessage(null)} />}
          <div className="container mx-auto">
            {Array.isArray(images) ? (
                <div>
                  <div className={`w-full image-container ${isLoading ? "opacity-0" : "opacity-100"}`}>
                    {[0, 1, 2, 3, 4].map((offset, i) => {
                      const index = (currentImageIndex + offset) % images.length;
                      const imageW = i === 0 || i === 4 ? '200%' : i === 1 || i === 3 ? '250%' : '340%';
                      const imageH = i === 0 || i === 4 ? '290%' : i === 1 || i === 3 ? '295%' : '300%';
                      const imagePosition = i === 0 ? '0%' : i === 1  ? '15%' : i === 2 ? '35%' : i === 3  ? '60%' : '80%';
                      return images[index] ? (
                          <div key={index} style={{ position: 'absolute', left: imagePosition }}>
                            <Suspense fallback={<Loading/>}>
                              <Image
                                  src={images[index].image_url}
                                  alt={images[index].description}
                                  width={imageW}
                                  height={imageH}
                                  objectFit="cover"
                                  onLoad={() => setIsLoading(false)}
                                  className={`overlap-image ${i === 0 ? 'image-0' : i === 1 ? 'image-1' : i === 2 ? 'image-2' : i === 3 ? 'image-3' : i === 4 ? 'image-4' : ''}`}
                              />
                            </Suspense>
                          </div>
                      ) : (
                          <div key={index} className="h-400px bg-gray-200 rounded-lg"></div>
                      );
                    })}
                  </div>
                  <div className="circle-container">
                    <IoIosArrowBack className="arrow-icon" onClick={handlePrev} />
                    {[0, 1, 2, 3, 4].map((i) => (
                        <div key={i} className={`circle ${currentImageIndex === i ? 'active' : ''}`} onClick={() => handleCircleClick(i)}></div>
                    ))}
                    <IoIosArrowForward className="arrow-icon" onClick={handleNext} />
                  </div>
                </div>
            ) : (
                <p>Error: Images is not an array.</p>
            )}
          </div>
        </div>
        </>
  );
}