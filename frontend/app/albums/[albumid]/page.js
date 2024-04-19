"use client";

// Importing necessary libraries and components
import React, { useEffect, useState, useContext } from "react";
import { useRouter } from "next/navigation";
import "/styles/album_layout_styles.css";
import ImageSelection from "/utils/ImageSelection";
import axios from "axios";
import { SelectedItemsContext } from "/utils/SelectedItemsContext";
import download from "downloadjs";
import { useSession } from "next-auth/react";
import Loading from "@/app/loading";
import { AlbumButtons } from "@/utils/AlbumButtons";
import SuccessWindow from "@/utils/SuccessWindow";
import ErrorWindow from "@/utils/ErrorWindow";

// SubAlbumPage component
export default function SubAlbumPage({ params }) {
  // Extracting albumId from params
  const albumId = params.albumid;

  // Using context to get and set selected images and albums
  const {
    selectedImageIds,
    selectedAlbumIds,
    setSelectedImageIds,
    setSelectedAlbumIds,
    setIsAllItemsDeselected,
  } = useContext(SelectedItemsContext);

  // State variables
  const [albumData, setAlbumData] = useState(null);
  const [downloadProgress, setDownloadProgress] = useState(null);
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);
  const [isTagModalOpen, setIsTagModalOpen] = useState(false);
  const [tagInput, setTagInput] = useState("");
  const [errorMessage, setErrorMessage] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [isActionsOpen, setIsActionsOpen] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Router and session data
  const router = useRouter();
  const { data: session } = useSession();

  // Function to handle actions click
  const handleActionsClick = () => {
    setIsActionsOpen(!isActionsOpen);
  };

  // Function to handle upload click
  const handleUploadClick = () => {
    setIsUploadOpen(!isUploadOpen);
  };

  // Fetching album data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const endpoint = `/api/albums/${albumId}`;
        const response = await fetch(endpoint);
        if (response.ok) {
          const data = await response.json();
          setAlbumData(data);
          if (data.parentAlbumId === null || data.parentAlbumId === undefined) {
            router.push("/albums");
          }
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

    fetchData();
    setSelectedImageIds([]);
    setSelectedAlbumIds([]);
  }, [albumId, setSelectedImageIds, setSelectedAlbumIds, router]);

  // Setting parent link href based on whether parent is root or not
  const parentLinkHref = albumData?.parentIsRoot
    ? "/albums"
    : `/albums/${albumData?.parentAlbumId}`;

  // Closing actions if no images or albums are selected
  useEffect(() => {
    if (selectedImageIds.length === 0 && selectedAlbumIds.length === 0) {
      setIsActionsOpen(false);
    }
  }, [selectedImageIds, selectedAlbumIds]);

  // Loading state
  if (isLoading) {
    return <Loading />;
  }

  // Function to handle download of images or albums
  const handleDownload = async () => {
    if (selectedImageIds.length === 1 && selectedAlbumIds.length === 0) {
      const image = albumData.images.find(
        (image) => image._id.toString() === selectedImageIds[0]
      );
      const url = image.image_url; // Use image_url instead of url
      const filename = image.filename;
      try {
        setDownloadProgress("Downloading...");
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
          setErrorMessage(`Error in handleDownload`);
          setDownloadProgress(null);
        }
      } catch (error) {
        console.error(`Error in handleDownload: ${error.message}`);
        setDownloadProgress(null);
        setErrorMessage(`Error in handleDownload`);
      }
    } else {
      const data = {
        album_ids: selectedAlbumIds,
        image_ids: selectedImageIds,
      };
      try {
        setDownloadProgress("Downloading...");
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
          let fileName = "download.zip"; // Default file name

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
    setSelectedAlbumIds([]);
    setIsAllItemsDeselected(true);
  };

  // Function to handle deletion of images or albums
  const handleDelete = async () => {
    const image_ids = selectedImageIds;
    const album_ids = selectedAlbumIds;
    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.accessToken}`,
    };

    setIsConfirmDialogOpen(true);

    if (image_ids.length > 0) {
      try {
        const response = await axios.delete(
          `${process.env.NEXT_PUBLIC_API_URL}/delete-images`,
          {
            data: { image_ids },
            headers,
          }
        );
        if (response.status === 200) {
          console.log(response.data.message);
          setAlbumData((prevState) => ({
            ...prevState,
            images: prevState.images.filter(
              (image) => !image_ids.includes(image._id)
            ),
          }));
          setSelectedImageIds([]);
          setSuccessMessage("Delete successful");
        } else {
          console.error("Failed to delete images");
          setErrorMessage("Failed to delete images");
        }
      } catch (error) {
        console.error(`Error in handleDelete: ${error.message}`);
        setErrorMessage(`Error in handleDelete`);
      }
    }

    if (album_ids.length > 0) {
      try {
        const response = await axios.delete(
          `${process.env.NEXT_PUBLIC_API_URL}/delete-albums`,
          {
            data: { album_ids },
            headers,
          }
        );
        if (response.status === 200) {
          console.log(response.data.message);
          setAlbumData((prevState) => ({
            ...prevState,
            sons: prevState.sons.filter(
              (album) => !album_ids.includes(album._id)
            ),
          }));
          setSelectedAlbumIds([]);
          setSuccessMessage("Delete successful");
        } else {
          setErrorMessage("Failed to delete albums");
          console.error("Failed to delete albums");
        }
      } catch (error) {
        console.error(`Error in handleDelete: ${error.message}`);
        setErrorMessage(`Error in handleDelete`);
      }
    }
    setIsAllItemsDeselected(true);
  };

  const handleTagSubmit = async () => {
    if (!tagInput) {
      setErrorMessage("No tags entered");
      return;
    }

    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.accessToken}`,
    };

    const data = {
      image_ids: selectedImageIds ? selectedImageIds : [],
      album_ids: selectedAlbumIds ? selectedAlbumIds : [],
      tags: tagInput.split(",").map((tag) => tag.trim()),
    };

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/add-tags-to-selected`,
        data,
        { headers }
      );
      if (response.status === 200) {
        console.log(response.data);
        setSuccessMessage("Tags added successfully");
      } else {
        console.error("Failed to add tags");
        setErrorMessage("Failed to add tags");
      }
    } catch (error) {
      console.error(`Error in handleTagSubmit: ${error.message}`);
      setErrorMessage(`Error in handleTagSubmit: ${error.message}`);
    }

    setTagInput("");
    setIsTagModalOpen(false);
    setSelectedImageIds([]);
    setSelectedAlbumIds([]);
    setIsAllItemsDeselected(true);
  };

  const handleAddTags = () => {
    setIsTagModalOpen(true);
  };

  const handleTagModalCancel = () => {
    setTagInput("");
    setIsTagModalOpen(false);
  };

  const handleTagInputChange = (e) => {
    setTagInput(e.target.value);
  };
  if (!albumData) {
    return <Loading />;
  }

  // If no albums or images, return specific UI
  if (!albumData.sons.length && !albumData.images.length) {
    const parentLinkHref = albumData?.parentIsRoot
      ? "/albums"
      : `/albums/${albumData?.parentAlbumId}`;
    return (
      <div>
        <AlbumButtons
          albumId={albumId}
          parentLinkHref={parentLinkHref}
          session={session}
          selectedImageIds={selectedImageIds}
          selectedAlbumIds={selectedAlbumIds}
          isActionsOpen={isActionsOpen}
          handleActionsClick={handleActionsClick}
          handleAddTags={handleAddTags}
          handleDownload={handleDownload}
          handleTagSubmit={handleTagSubmit}
          handleTagModalCancel={handleTagModalCancel}
          tagInput={tagInput}
          handleTagInputChange={handleTagInputChange}
          downloadProgress={downloadProgress}
          isConfirmDialogOpen={isConfirmDialogOpen}
          setIsConfirmDialogOpen={setIsConfirmDialogOpen}
          handleDelete={handleDelete}
          isTagModalOpen={isTagModalOpen}
          setIsTagModalOpen={setIsTagModalOpen}
          handleUploadClick={handleUploadClick}
          isUploadOpen={isUploadOpen}
        />
        <h2 style={{ fontSize: "2em", fontWeight: "bold", marginTop: "-40px" }}>
          {" "}
          {albumData.name}:
        </h2>
        No albums or images found.
      </div>
    );
  }

  const albumItems = albumData.sons.map((album, index) => (
    <ImageSelection key={index} item={album} isAlbum={true} />
  ));
  const imageItems = albumData.images.map((image, idx) => (
    <ImageSelection key={idx} item={image} isAlbum={false} />
  ));

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
      <AlbumButtons
        albumId={albumId}
        parentLinkHref={parentLinkHref}
        session={session}
        selectedImageIds={selectedImageIds}
        selectedAlbumIds={selectedAlbumIds}
        isActionsOpen={isActionsOpen}
        handleActionsClick={handleActionsClick}
        isUploadOpen={isUploadOpen}
        handleUploadClick={handleUploadClick}
        handleAddTags={handleAddTags}
        handleDownload={handleDownload}
        handleTagSubmit={handleTagSubmit}
        handleTagModalCancel={handleTagModalCancel}
        tagInput={tagInput}
        handleTagInputChange={handleTagInputChange}
        downloadProgress={downloadProgress}
        isConfirmDialogOpen={isConfirmDialogOpen}
        setIsConfirmDialogOpen={setIsConfirmDialogOpen}
        handleDelete={handleDelete}
        isTagModalOpen={isTagModalOpen}
        setIsTagModalOpen={setIsTagModalOpen}
      />
      <h2 style={{ fontSize: "2em", fontWeight: "bold", marginTop: "-40px" }}>
        {" "}
        {albumData.name}:
      </h2>
      <div className="album-container grid-layout">
        {albumItems}
        {imageItems}
      </div>
    </div>
  );
}
