'use client';

import React, { useEffect, useState, useContext } from 'react';
import Link from 'next/link';
import "/styles/album_layout_styles.css"
import { ArrowLeftStartOnRectangleIcon, FolderArrowDownIcon, FolderPlusIcon, ArrowDownTrayIcon } from "@heroicons/react/24/outline";
import ImageSelection from '/utils/ImageSelection';
import axios from "axios";
import { SelectedItemsContext } from '/utils/SelectedItemsContext';
import download from 'downloadjs';

export default function SubAlbumPage({ params}) {
    const [albumData, setAlbumData] = useState(null);
    const albumId = params.albumid;
    const { selectedImageIds, selectedAlbumIds } = useContext(SelectedItemsContext);
    const [downloadProgress, setDownloadProgress] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const endpoint = `/api/albums/${albumId}`;
                const response = await fetch(endpoint);
                if (response.ok) {
                    const data = await response.json();
                    setAlbumData(data);
                } else {
                    console.error(`Error fetching data: ${response.statusText}`);
                }
            } catch (error) {
                console.error(`Error fetching data: ${error.message}`);
            }
        };

        fetchData();
    }, [albumId]);

    const parentLinkHref = albumData?.parentIsRoot ? '/albums' : `/albums/${albumData?.parentAlbumId}`;

    const handleDownload = async () => {
        if (selectedImageIds.length === 1 && selectedAlbumIds.length === 0) {
            console.log('selectedImageIds:', selectedImageIds);
            console.log('albumData.images:', albumData.images);
            const image = albumData.images.find(image => image._id.toString() === selectedImageIds[0]);
            console.log('image:', image);
            const url = image.image_url; // Use image_url instead of url
            console.log('url:', url);
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
                album_ids: selectedAlbumIds,
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
                    let fileName = 'download.zip'; // Default file name

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
    };

    if (!albumData || (!albumData.sons.length && !albumData.images.length)) {
        return <div>
            <div className="mb-12 flex items-center justify-between gap-x-16">
                <div className="flex space-x-6">
                    <Link href={parentLinkHref} passHref>
                        <button
                            className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center">
                            <ArrowLeftStartOnRectangleIcon className="h-5 w-5 mr-2"/>
                            Previous album
                        </button>
                    </Link>
                </div>
                <div>
                </div>
                <div className="flex space-x-6">
                    <Link href={`/gallery/upload/${albumId}`} passHref>
                        <button
                            className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center">
                            <FolderArrowDownIcon className="h-5 w-5 mr-2"/>
                            Upload images to this album
                        </button>
                    </Link>
                    <Link href={`/albums/add/${albumId}`} passHref>
                        <button
                            className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center">
                            <FolderPlusIcon className="h-5 w-5 mr-2"/>
                            Add album
                        </button>
                    </Link>
                </div>
            </div>
            No albums or images found.</div>;
    }

    const albumItems = albumData.sons.map((album, index) => (
        <ImageSelection key={index} item={album} isAlbum={true} />
    ));
    const imageItems = albumData.images.map((image, idx) => (
        <ImageSelection key={idx} item={image} isAlbum={false} />
    ));

    return (
        <div className="container">
            <div className="mb-12 flex items-center justify-between gap-x-16">
                <div className="flex space-x-6">
                    <Link href={parentLinkHref} passHref>
                        <button className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center">
                            <ArrowLeftStartOnRectangleIcon className="h-5 w-5 mr-2"/>
                            Previous album
                        </button>
                    </Link>
                </div>
                <div>
                </div>
                <div className="flex space-x-6">
                    {selectedImageIds.length + selectedAlbumIds.length > 0 && (
                        downloadProgress === null ? (
                            <button onClick={handleDownload} className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center">
                                <ArrowDownTrayIcon className="h-5 w-5 mr-2"/>
                                Download selected
                            </button>
                        ) : (
                            <div>
                                {downloadProgress}
                            </div>
                        )
                    )}
                    <Link href={`/gallery/upload/${albumId}`} passHref>
                        <button className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center">
                            <FolderArrowDownIcon className="h-5 w-5 mr-2"/>
                            Upload images to this album
                        </button>
                    </Link>
                    <Link href={`/albums/add/${albumId}`} passHref>
                        <button className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center">
                            <FolderPlusIcon className="h-5 w-5 mr-2"/>
                            Add album
                        </button>
                    </Link>
                </div>
            </div>
            <div className="album-container grid-layout">
                {albumItems}
                {imageItems}
            </div>
        </div>
    );
}