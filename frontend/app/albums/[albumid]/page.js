'use client';

import React, { useEffect, useState, useContext } from 'react';
import Link from 'next/link';
import "/styles/album_layout_styles.css"
import { ArrowLeftStartOnRectangleIcon, FolderArrowDownIcon, FolderPlusIcon, ArrowDownTrayIcon } from "@heroicons/react/24/outline";
import ImageSelection from '/utils/ImageSelection';
import axios from "axios";
import { SelectedItemsContext } from '/utils/SelectedItemsContext';
import download from 'downloadjs';
import {useSession} from "next-auth/react";

export default function SubAlbumPage({ params}) {
    const [albumData, setAlbumData] = useState(null);
    const albumId = params.albumid;
    const { selectedImageIds, selectedAlbumIds } = useContext(SelectedItemsContext);
    const [downloadProgress, setDownloadProgress] = useState(null);
    const { setSelectedImageIds, setSelectedAlbumIds } = useContext(SelectedItemsContext);
    const { setIsAllItemsDeselected } = useContext(SelectedItemsContext);
    const { data: session } = useSession();
    const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);

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
        setSelectedImageIds([]);
        setSelectedAlbumIds([]);
    }, [albumId, setSelectedImageIds, setSelectedAlbumIds]);

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
        setSelectedImageIds([]);
        setSelectedAlbumIds([]);
        setIsAllItemsDeselected(true);
    };


    const handleDelete = async () => {
        const image_ids = selectedImageIds;
        const album_ids = selectedAlbumIds;
        const headers = {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${session.accessToken}`,
        };

        setIsConfirmDialogOpen(true);

        if (image_ids.length > 0) {
            try {
                const response = await axios.delete('http://localhost:8000/delete-images', { data: { image_ids }, headers });
                if (response.status === 200) {
                    console.log(response.data.message);
                    setAlbumData(prevState => ({
                        ...prevState,
                        images: prevState.images.filter(image => !image_ids.includes(image._id))
                    }));
                    setSelectedImageIds([]);
                } else {
                    console.error('Failed to delete images');
                }
            } catch (error) {
                console.error('Error deleting images:', error);
            }
        }

        if (album_ids.length > 0) {
            try {
                const response = await axios.delete('http://localhost:8000/delete-albums', { data: { album_ids }, headers });
                if (response.status === 200) {
                    console.log(response.data.message);
                    setAlbumData(prevState => ({
                        ...prevState,
                        sons: prevState.sons.filter(album => !album_ids.includes(album._id))
                    }));
                    setSelectedAlbumIds([]);
                } else {
                    console.error('Failed to delete albums');
                }
            } catch (error) {
                console.error('Error deleting albums:', error);
            }
        }
        setIsAllItemsDeselected(true);
    };

    const ConfirmDialog = ({ isOpen, onConfirm, onCancel }) => {
        if (!isOpen) {
            return null;
        }

        return (
            <div className="fixed z-10 inset-0 overflow-y-auto">
                <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                    <div className="fixed inset-0 transition-opacity" aria-hidden="true">
                        <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
                    </div>
                    <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                    <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                        <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                            <div className="sm:flex sm:items-start">
                                <div className="mt-3 text-center sm:mt-0 sm:text-center">
                                    <h3 className="text-lg leading-6 font-medium text-gray-900 text-center" id="modal-title">
                                        Are you sure you want to delete the selected items?
                                    </h3>
                                </div>
                            </div>
                        </div>
                        <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                            <button type="button" className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm" onClick={onConfirm}>
                                Delete
                            </button>
                            <button type="button" className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm" onClick={onCancel}>
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
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
                            <>
                                {session && (
                                    <button
                                        onClick={() => setIsConfirmDialogOpen(true)}
                                        className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center"
                                    >
                                        Delete selected
                                    </button>
                                )}
                                <ConfirmDialog
                                    isOpen={isConfirmDialogOpen}
                                    onConfirm={() => {
                                        handleDelete();
                                        setIsConfirmDialogOpen(false);
                                    }}
                                    onCancel={() => setIsConfirmDialogOpen(false)}
                                />
                                <button
                                    onClick={handleDownload}
                                    className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center"
                                >
                                    <ArrowDownTrayIcon className="h-5 w-5 mr-2"/>
                                    Download selected
                                </button>
                            </>
                        ) : (
                            <div>
                                {downloadProgress}
                            </div>
                        )
                    )}
                    {session && (
                        <div className="flex space-x-6">
                            <Link href={`/gallery/upload/galeria_pk/${albumId}`} passHref>
                                <button className="rounded border bg-gray-100 px-2 py-1 text-xs text-gray-800 flex items-center">
                                    <FolderArrowDownIcon className="h-5 w-5 mr-2"/>
                                    Upload from GaleriaPK
                                </button>
                            </Link>
                            <Link href={`/gallery/upload/zip/${albumId}`} passHref>
                                <button
                                    className="rounded border bg-gray-100 px-2 py-1 text-xs text-gray-800 flex items-center">
                                    <FolderArrowDownIcon className="h-5 w-5 mr-2"/>
                                    Upload zip here
                                </button>
                            </Link>
                            <Link href={`/gallery/upload/${albumId}`} passHref>
                                <button
                                    className="rounded border bg-gray-100 px-2 py-1 text-xs text-gray-800 flex items-center">
                                    <FolderArrowDownIcon className="h-5 w-5 mr-2"/>
                                    Upload images here
                                </button>
                            </Link>
                            <Link href={`/albums/add/${albumId}`} passHref>
                                <button
                                    className="rounded border bg-gray-100 px-2 py-1 text-xs text-gray-800 flex items-center">
                                    <FolderPlusIcon className="h-5 w-5 mr-2"/>
                                    Add album
                                </button>
                            </Link>
                        </div>
                    )}
                </div>
            </div>
            <div className="album-container grid-layout">
                {albumItems}
                {imageItems}
            </div>
        </div>
    );
}