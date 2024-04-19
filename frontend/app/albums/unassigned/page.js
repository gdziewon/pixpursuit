"use client";

// Importing necessary libraries and components
import React, { useState, useEffect, useContext } from "react";
import ImageSelection from "/utils/ImageSelection";
import axios from "axios";
import { SelectedItemsContext } from "/utils/SelectedItemsContext";
import download from "downloadjs";
import SuccessWindow from "@/utils/SuccessWindow";
import ErrorWindow from "@/utils/ErrorWindow";

/**
 * UnassignedImagesPage component
 * This component is responsible for displaying the images that are not assigned to any album.
 * It also provides the functionality to download these unassigned images.
 */
export default function UnassignedImagesPage() {
  // State variables
  const [unassignedImages, setUnassignedImages] = useState([]); // The unassigned images
  const { selectedImageIds, setSelectedImageIds, setIsAllItemsDeselected } =
    useContext(SelectedItemsContext); // Context for selected images
  const [downloadProgress, setDownloadProgress] = useState(null); // Progress of the download
  const [errorMessage, setErrorMessage] = useState(null); // Error message
  const [successMessage, setSuccessMessage] = useState(null); // Success message

  // Fetching unassigned images on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`/api/albums/unassigned`);
        setUnassignedImages(Array.isArray(response.data) ? response.data : []);
      } catch (error) {
        setErrorMessage("Failed to fetch unassigned images");
      }
    };

    fetchData();
  }, []);

  // Mapping over unassigned images to create image items
  const imageItems = unassignedImages.map((image, idx) => {
    return <ImageSelection key={idx} item={image} isAlbum={false} />;
  });

  /**
   * handleDownload function
   * This function is responsible for handling the download of unassigned images.
   * It checks if only one image is selected, then downloads that image.
   * If more than one image is selected, it downloads them as a zip file.
   */

  const handleDownload = async () => {
    if (selectedImageIds.length === 1) {
      const image = unassignedImages.find(
        (image) => image._id.toString() === selectedImageIds[0]
      );
      const url = image.image_url;
      const filename = image.filename;
      try {
        setDownloadProgress("Preparing download...");
        const response = await fetch(
          `${
            process.env.NEXT_PUBLIC_API_URL
          }/download-image?url=${encodeURIComponent(url)}`
        );
        if (response.ok) {
          const blob = await response.blob();
          download(blob, filename, response.headers.get("Content-Type"));
          setDownloadProgress(null);
          setSuccessMessage("Download successful");
        } else {
          setErrorMessage("Download failed");
          setDownloadProgress(null);
        }
      } catch (error) {
        console.error(`Error in handleDownload: ${error.message}`);
        setDownloadProgress(null);
        setErrorMessage(`Error in handleDownload`);
      }
    } else {
      const data = {
        image_ids: selectedImageIds,
      };
      try {
        setDownloadProgress("Preparing download...");
        const response = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/download-zip`,
          data,
          {
            headers: {
              "Content-Type": "application/json",
            },
            responseType: "blob",
          }
        );

        if (response.status === 200) {
          const contentDisposition = response.headers["content-disposition"];
          let fileName = "favourites.zip";

          if (contentDisposition) {
            const fileNameMatch = contentDisposition.match(
              /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
            );
            if (fileNameMatch && fileNameMatch[1]) {
              fileName = fileNameMatch[1].replace(/['"]/g, "");
            }
          }
          download(response.data, fileName, "application/zip");
          setDownloadProgress(null);
          setSuccessMessage("Download successful");
        } else {
          setErrorMessage("Download failed");
          setDownloadProgress(null);
        }
      } catch (error) {
        console.error(`Error in handleDownload: ${error.message}`);
        setErrorMessage(`Error in handleDownload`);
        setDownloadProgress(null);
      }
    }
    setSelectedImageIds([]);
    setIsAllItemsDeselected(true);
  };

  return (
    <div className="container">
      {errorMessage && (
        <ErrorWindow
          message={errorMessage}
          clearMessage={() => setErrorMessage(null)}
        />
      )}
      {successMessage && (
        <SuccessWindow
          message={successMessage}
          clearMessage={() => setSuccessMessage(null)}
        />
      )}
      <div className="flex justify-between items-center mb-4">
        <meta
          httpEquiv="Content-Security-Policy"
          content="upgrade-insecure-requests"
        />
        <h1 className="text-3xl font-bold">Unassigned Images</h1>
        {selectedImageIds.length > 0 && (
          <div>
            {downloadProgress ? (
              <div>{downloadProgress}</div>
            ) : (
              <button
                onClick={handleDownload}
                className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800"
              >
                Download Selected
              </button>
            )}
          </div>
        )}
      </div>
      <div className="album-container grid-layout">{imageItems}</div>
    </div>
  );
}
