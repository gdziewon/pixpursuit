"use client";

import { useState, useEffect } from "react";
import Image from "next/legacy/image";
import Loading from "@/app/loading";
import { Suspense } from "react";
import ErrorWindow from "@/utils/ErrorWindow";
import { getImages } from "@/utils/getImages";
import { IoIosArrowBack, IoIosArrowForward } from "react-icons/io";
import Link from "next/link";
import "@/styles/design_styles.css";

export default function RandomImage() {
  const [images, setImages] = useState(Array(10).fill(null));
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);
  const [newestAlbums, setNewestAlbums] = useState([]);

  useEffect(() => {
    fetchImages();
    getNewestAlbums();
  }, []);

  /**
   * Sets up a timer to change the current image index every 10 seconds.
   */
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 10000);

    return () => clearInterval(timer);
  }, [images]);

  /**
   * Fetches images from the API.
   */
  const fetchImages = async () => {
    try {
      const data = await getImages({
        limit: 5,
        sort: "mostPopular",
        page: 1,
        query: "",
      });
      setImages(data);
    } catch (error) {
      console.error("Error fetching images:", error);
      setErrorMessage("Error fetching images");
    }
  };

  /**
   * Handles the previous image button click.
   */
  const handlePrev = () => {
    setCurrentImageIndex(
      (prevIndex) => (prevIndex - 1 + images.length) % images.length
    );
  };

  /**
   * Handles the next image button click.
   */
  const handleNext = () => {
    setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
  };

  /**
   * Handles the circle button click.
   *
   * @param {number} index - The index of the circle button.
   */
  const handleCircleClick = (index) => {
    setCurrentImageIndex(index);
  };

  /**
   * Fetches the newest albums from the API.
   */
  const getNewestAlbums = async () => {
    setIsLoading(true);
    try {
      const endpoint = `/api/albums/root?page=1&limit=6`;
      const response = await fetch(endpoint);
      if (response.ok) {
        const data = await response.json();
        setNewestAlbums(data.sons);
        setIsLoading(false);
      } else {
        console.error(`Error fetching data: ${response.statusText}`);
        setErrorMessage(`Error fetching data`);
      }
    } catch (error) {
      console.error(`Error fetching data: ${error.message}`);
      setErrorMessage(`Error fetching data`);
    }
  };

  return (
    <>
      <h1 className="text-3xl font-bold mb-4">PixPursuit</h1>
      <div className="bg-indigo-400 bg-opacity-25 p-8 shadow-lg rounded-2xl">
        {errorMessage && (
          <ErrorWindow
            message={errorMessage}
            clearMessage={() => setErrorMessage(null)}
          />
        )}
        <div className="container mx-auto">
          {Array.isArray(images) ? (
            <div>
              <div
                className={`w-full image-container ${
                  isLoading ? "opacity-0" : "opacity-100"
                }`}
              >
                {[0, 1, 2, 3, 4].map((offset, i) => {
                  const index = (currentImageIndex + offset) % images.length;
                  const imageW =
                    i === 0 || i === 4
                      ? "200%"
                      : i === 1 || i === 3
                      ? "250%"
                      : "340%";
                  const imageH =
                    i === 0 || i === 4
                      ? "290%"
                      : i === 1 || i === 3
                      ? "295%"
                      : "300%";
                  const imagePosition =
                    i === 0
                      ? "0%"
                      : i === 1
                      ? "15%"
                      : i === 2
                      ? "35%"
                      : i === 3
                      ? "60%"
                      : "80%";
                  return images[index] ? (
                    <div
                      key={index}
                      style={{ position: "absolute", left: imagePosition }}
                    >
                      <Suspense fallback={<Loading />}>
                        <Image
                          src={images[index].image_url}
                          alt={images[index].description}
                          width={imageW}
                          height={imageH}
                          objectFit="cover"
                          onLoad={() => setIsLoading(false)}
                          className={`overlap-image ${
                            i === 0
                              ? "image-0"
                              : i === 1
                              ? "image-1"
                              : i === 2
                              ? "image-2"
                              : i === 3
                              ? "image-3"
                              : i === 4
                              ? "image-4"
                              : ""
                          }`}
                        />
                      </Suspense>
                    </div>
                  ) : (
                    <div
                      key={index}
                      className="h-400px bg-gray-200 rounded-lg"
                    ></div>
                  );
                })}
              </div>
              <div className="circle-container">
                <IoIosArrowBack
                  className="arrow-icon cursor-pointer"
                  onClick={handlePrev}
                />
                {[0, 1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className={`circle ${
                      currentImageIndex === i ? "active" : ""
                    }`}
                    onClick={() => handleCircleClick(i)}
                  ></div>
                ))}
                <IoIosArrowForward
                  className="arrow-icon cursor-pointer"
                  onClick={handleNext}
                />
              </div>
            </div>
          ) : (
            <p>Error: Images is not an array.</p>
          )}
        </div>
      </div>
      <div className="bg-gray-800 bg-opacity-25 p-8 shadow-lg rounded-2xl mt-4">
        <h2 className="text-2xl font-bold mb-4">Newest Albums</h2>
        <div className="newest-albums flex flex-wrap">
          {newestAlbums.slice(0, 6).map((album, index) => (
            <div key={index} className="album w-1/3">
              <Link href={`/albums/${album._id}`}>
                <div className="bg-gray-700 bg-opacity-25 p-2 shadow-lg mt-4 flex items-center album-pair">
                  <Image
                    src="/dir.png"
                    alt="dir icon"
                    width={40}
                    height={40}
                    layout="fixed"
                  />
                  <h2 className="ml-2 album-name">{album.name}</h2>
                </div>
                {}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
