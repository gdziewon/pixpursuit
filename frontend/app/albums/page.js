"use client";

import React, { useState, useEffect, useContext } from 'react';
import Link from 'next/link';
import "/styles/album_layout_styles.css"
import {FolderArrowDownIcon, FolderPlusIcon} from "@heroicons/react/24/outline";
import ImageSelection from '/utils/ImageSelection';
import {SelectedItemsContext} from '/utils/SelectedItemsContext';
import axios from "axios";
import download from 'downloadjs';
import {useSession} from "next-auth/react";
import Image from 'next/image';
import DropdownMenu from '@/utils/DropdownMenu';
import {
    ChevronUpIcon,
    ChevronDownIcon,
} from "@heroicons/react/24/solid";
import Loading from "@/app/loading";

export default function AlbumsPage() {
    const [albumData, setAlbumData] = useState(null);
    const { selectedImageIds, selectedAlbumIds } = useContext(SelectedItemsContext);
    const [downloadProgress, setDownloadProgress] = useState(null);
    const albumId = 'root';
    const { setSelectedImageIds, setSelectedAlbumIds } = useContext(SelectedItemsContext);
    const { setIsAllItemsDeselected } = useContext(SelectedItemsContext);
    const { data: session } = useSession();
    const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);
    const [isTagModalOpen, setIsTagModalOpen] = useState(false);
    const [tagInput, setTagInput] = useState('');
    const [isActionsOpen, setIsActionsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    const handleActionsClick = () => {
        setIsActionsOpen(!isActionsOpen);
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const endpoint = `/api/albums/${albumId}`;
                const response = await fetch(endpoint);
                console.log(`Response status: ${response.status}`);
                if (response.ok) {
                    const data = await response.json();
                    setAlbumData(data);
                    setIsLoading(false);
                } else {
                    console.error(`Error fetching data: ${response.statusText}`);
                }
            } catch (error) {
                console.error(`Error fetching data: ${error.message}`);
            }
        };

        try {
            fetchData();
        } catch (error) {
            console.error(`Error in fetchData: ${error.message}`);
        }

        setSelectedImageIds([]);
        setSelectedAlbumIds([]);
    }, [albumId, setSelectedImageIds, setSelectedAlbumIds]);

    useEffect(() => {
        if (selectedImageIds.length === 0 && selectedAlbumIds.length === 0) {
            setIsActionsOpen(false);
        }
    }, [selectedImageIds, selectedAlbumIds]);

    if (isLoading) {
        return <Loading />;
    }

    const handleDownload = async () => {
        if (selectedImageIds.length === 1 && selectedAlbumIds.length === 0) {
            const image = albumData.images.find(image => image._id.toString() === selectedImageIds[0]);
            const url = image.image_url;
            const filename = image.filename;
            try {
                setDownloadProgress('Downloading...');
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/download-image?url=${encodeURIComponent(url)}`);
                if (response.ok) {
                    const blob = await response.blob();
                    download(blob, filename, response.headers.get('Content-Type'));
                    setDownloadProgress(null);
                } else {
                    alert('Download failed');
                    setDownloadProgress(null);
                }
            } catch (error) {
                console.error(`Error in handleDownload: ${error.message}`);
                alert(`Error in handleDownload: ${error.message}`);
                setDownloadProgress(null);
            }
        } else {
            const data = {
                album_ids: selectedAlbumIds,
                image_ids: selectedImageIds
            };
            try {
                setDownloadProgress('Downloading...');
                const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/download-zip`, data, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    responseType: 'blob',
                });

                if (response.status === 200) {
                    const contentDisposition = response.headers['content-disposition'];
                    let fileName = 'download.zip';

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
                console.error(`Error in handleDownload: ${error.message}`);
                alert(`Error in handleDownload: ${error.message}`);
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
                const response = await axios.delete(`${process.env.NEXT_PUBLIC_API_URL}/delete-images`, { data: { image_ids }, headers });
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
                console.error(`Error in handleDelete: ${error.message}`);
                alert(`Error in handleDelete: ${error.message}`);
            }
        }

        if (album_ids.length > 0) {
            try {
                const response = await axios.delete(`${process.env.NEXT_PUBLIC_API_URL}/delete-albums`, { data: { album_ids }, headers });
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
                console.error(`Error in handleDelete: ${error.message}`);
                alert(`Error in handleDelete: ${error.message}`);
            }
        }
        setIsAllItemsDeselected(true);
    };

    const handleTagSubmit = async () => {
        const headers = {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${session.accessToken}`,
        };

        const data = {
            image_ids: selectedImageIds ? selectedImageIds : [],
            album_ids: selectedAlbumIds ? selectedAlbumIds : [],
            tags: tagInput.split(',').map(tag => tag.trim()),
        };

        try {
            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/add-tags-to-selected`, data, { headers });
            console.log(response.data);
        } catch (error) {
            console.error(`Error in handleTagSubmit: ${error.message}`);
        }

        setTagInput('');
        setIsTagModalOpen(false);
        setSelectedImageIds([]);
        setSelectedAlbumIds([]);
        setIsAllItemsDeselected(true);
    };


    const handleAddTags = () => {
        setIsTagModalOpen(true);
    };

    const handleTagModalCancel = () => {
        setTagInput('');
        setIsTagModalOpen(false);
    };

    const handleTagInputChange = (e) => {
        setTagInput(e.target.value);
    };

    if (!albumData || (!albumData.sons.length && !albumData.images.length)) {
        return <div>No albums or images found.</div>;
    }

    const albumItems = albumData.sons.map((album, index) => (
        <ImageSelection key={index} item={album} isAlbum={true} />
    ));

    const imageItems = albumData.images.map((image, idx) => {
        return <ImageSelection key={idx} item={image} isAlbum={false} />
    });

    return (
        <div className="container">
            <div className="mb-12 flex items-center justify-between gap-x-16">
                <div>
                </div>
                <div>
                </div>
                <div className="flex space-x-3">
                    <div className="relative">
                        {selectedImageIds.length + selectedAlbumIds.length > 0 && (
                            <>
                                <button
                                    onClick={handleActionsClick}
                                    className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-800 flex items-center"
                                >
                                    Actions
                                    {isActionsOpen ? <ChevronUpIcon className="h-5 w-5 ml-2"/> :
                                        <ChevronDownIcon className="h-5 w-5 ml-2"/>}
                                </button>
                                <DropdownMenu
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
                                />
                            </>
                        )}
                    </div>
                    {session && (
                        <div className="flex space-x-3">
                            <Link href={`/gallery/upload/galeria_pk`} passHref>
                                <button className="rounded border bg-gray-100 px-2 py-1 text-xs text-gray-800 flex items-center">
                                    <FolderArrowDownIcon className="h-5 w-5 mr-2"/>
                                    Upload from GaleriaPK
                                </button>
                            </Link>
                            <Link href={`/gallery/upload/zip/`} passHref>
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
                {session && (
                    <Link href={`/albums/liked/`} passHref>
                        <div className="album-item">
                            <Image src="/liked.png" alt="Liked Images" width={200} height={200}/>
                            <span>Liked Images</span>
                        </div>
                    </Link>
                )}
                {albumItems}
                {imageItems}
            </div>
        </div>
    );
}