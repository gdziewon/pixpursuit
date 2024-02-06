"use client";

import React, {useState, useEffect, useContext} from 'react';
import ImageSelection from '/utils/ImageSelection';
import axios from "axios";
import { useSession } from 'next-auth/react';
import { SelectedItemsContext } from '/utils/SelectedItemsContext';
import download from 'downloadjs';

export default function LikedImagesPage() {
    const [likedImages, setLikedImages] = useState([]);
    const { data: session } = useSession();
    const { selectedImageIds, setSelectedImageIds, setIsAllItemsDeselected,  } = useContext(SelectedItemsContext);
    const [downloadProgress, setDownloadProgress] = useState(null);

    useEffect(() => {
        const fetchLikedImages = async () => {
            if (session && session.user) {
                const response = await axios.get(`/api/liked/${session.user.name}`);
                setLikedImages(response.data);
            }
        };

        fetchLikedImages();
    }, [session]);

    const imageItems = likedImages.map((image, idx) => {
        return <ImageSelection key={idx} item={image} isAlbum={false} />
    });

    const handleDownload = async () => {
        if (selectedImageIds.length === 1) {
            const image = likedImages.images.find(image => image._id.toString() === selectedImageIds[0]);
            const url = image.image_url;
            const filename = image.filename;
            try {
                setDownloadProgress('Preparing download...');
                const response = await fetch(`http://localhost:8000/download-image?url=${encodeURIComponent(url)}`);
                if (response.ok) {
                    const blob = await response.blob();
                    download(blob, filename, response.headers.get('Content-Type'));
                    setDownloadProgress(null);
                } else {
                    alert('Download failed');
                    setDownloadProgress(null);
                }
            } catch (error) {
                alert('Download failed');
            }
        } else {
            const data = {
                image_ids: selectedImageIds
            };
            try {
                setDownloadProgress('Preparing download...');
                const response = await axios.post('http://localhost:8000/download-zip', data, {
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
                } else {
                    alert('Download failed');
                    setDownloadProgress(null);
                }
            } catch (error) {
                console.error(error);
                alert('Download failed');
                setDownloadProgress(null);
            }
        }
        setSelectedImageIds([]);
        setIsAllItemsDeselected(true);
    };

    return (
        <div className="container">
            <div className="flex justify-between items-center mb-4">
                <h1 className="text-3xl font-bold">Liked Images</h1>
                {selectedImageIds.length > 0 && (
                    <div>
                        {downloadProgress ? (
                            <div>{downloadProgress}</div>
                        ) : (
                            <button onClick={handleDownload} className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
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