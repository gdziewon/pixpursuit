"use client";

import React, {useState, useEffect, useContext} from 'react';
import ImageSelection from '/utils/ImageSelection';
import axios from "axios";
import { useSession } from 'next-auth/react';
import { SelectedItemsContext } from '/utils/SelectedItemsContext';
import download from 'downloadjs';
import SuccessWindow from '@/utils/SuccessWindow';
import ErrorWindow from '@/utils/ErrorWindow';

/**
 * LikedImagesPage component.
 *
 * @returns {JSX.Element} - The rendered JSX element.
 */
export default function LikedImagesPage() {
    const [likedImages, setLikedImages] = useState([]);
    const { data: session } = useSession();
    const { selectedImageIds, setSelectedImageIds, setIsAllItemsDeselected,  } = useContext(SelectedItemsContext);
    const [downloadProgress, setDownloadProgress] = useState(null);
    const [errorMessage, setErrorMessage] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    /**
     * Fetches liked images and sets the state.
     *
     * @returns {void}
     */
    useEffect(() => {
        const fetchLikedImages = async () => {
            try {
                if (session && session.user) {
                    const response = await axios.get(`/api/liked/${session.user.name}`);
                    setLikedImages(response.data);
                }
            } catch (error) {
                setErrorMessage('Failed to fetch liked images');
            }
        };

        fetchLikedImages();
    }, [session]);

    const imageItems = likedImages.map((image, idx) => {
        return <ImageSelection key={idx} item={image} isAlbum={false} />
    });

    /**
     * Handles the download action.
     *
     * @returns {Promise<void>}
     */
    const handleDownload = async () => {
        if (selectedImageIds.length === 1) {
            const image = likedImages.find(image => image._id.toString() === selectedImageIds[0]);
            const url = image.image_url;
            const filename = image.filename;
            try {
                setDownloadProgress('Preparing download...');
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/download-image?url=${encodeURIComponent(url)}`);
                if (response.ok) {
                    const blob = await response.blob();
                    download(blob, filename, response.headers.get('Content-Type'));
                    setDownloadProgress(null);
                    setSuccessMessage('Download successful');
                } else {
                    setErrorMessage('Download failed');
                    setDownloadProgress(null);
                }
            } catch (error) {
                console.error(`Error in handleDownload: ${error.message}`);
                setDownloadProgress(null);
                setErrorMessage(`Error in handleDownload`);
            }
        } else {
            const data = {
                image_ids: selectedImageIds
            };
            try {
                setDownloadProgress('Preparing download...');
                const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/download-zip`, data, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    responseType: 'blob',
                });

                if (response.status === 200) {
                    const contentDisposition = response.headers['content-disposition'];
                    let fileName = 'favourites.zip';

                    if (contentDisposition) {
                        const fileNameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                        if (fileNameMatch && fileNameMatch[1]) {
                            fileName = fileNameMatch[1].replace(/['"]/g, '');
                        }
                    }
                    download(response.data, fileName, 'application/zip');
                    setDownloadProgress(null);
                    setSuccessMessage('Download successful');
                } else {
                    setErrorMessage('Download failed');
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

    /**
     * Renders the LikedImagesPage component.
     *
     * @returns {JSX.Element} - The rendered JSX element.
     */
    return (
        <div className="container">
            {errorMessage && <ErrorWindow message={errorMessage} clearMessage={() => setErrorMessage(null)} />}
            {successMessage && <SuccessWindow message={successMessage} clearMessage={() => setSuccessMessage(null)} />}
            <div className="flex justify-between items-center mb-4">
                <meta httpEquiv="Content-Security-Policy" content="upgrade-insecure-requests"/>
                <h1 className="text-3xl font-bold">Liked Images</h1>
                {selectedImageIds.length > 0 && (
                    <div>
                        {downloadProgress ? (
                            <div>{downloadProgress}</div>
                        ) : (
                            <button onClick={handleDownload}
                                    className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                                Download Selected
                            </button>
                        )}
                    </div>
                )}
            </div>
            <div className="album-container grid-layout">
                {imageItems}
            </div>
        </div>
    );
}