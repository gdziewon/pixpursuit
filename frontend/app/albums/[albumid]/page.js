'use client';

import React, { useEffect, useState, useContext } from 'react';
import { useRouter } from 'next/navigation';
import "/styles/album_layout_styles.css"
import ImageSelection from '/utils/ImageSelection';
import axios from "axios";
import { SelectedItemsContext } from '/utils/SelectedItemsContext';
import download from 'downloadjs';
import {useSession} from "next-auth/react";
import Loading from "@/app/loading";
import {AlbumButtons} from "@/utils/AlbumButtons";
import SuccessWindow from '@/utils/SuccessWindow';
import ErrorWindow from '@/utils/ErrorWindow';

/**
 * SubAlbumPage component.
 *
 * @param {Object} params - The parameters passed to the component.
 * @returns {JSX.Element} - The rendered JSX element.
 */
export default function SubAlbumPage({ params}) {
    const [albumData, setAlbumData] = useState(null);
    const albumId = params.albumid;
    const {selectedImageIds, selectedAlbumIds} = useContext(SelectedItemsContext);
    const [downloadProgress, setDownloadProgress] = useState(null);
    const {setSelectedImageIds, setSelectedAlbumIds} = useContext(SelectedItemsContext);
    const {setIsAllItemsDeselected} = useContext(SelectedItemsContext);
    const {data: session} = useSession();
    const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);
    const [isTagModalOpen, setIsTagModalOpen] = useState(false);
    const [tagInput, setTagInput] = useState('');
    const [errorMessage, setErrorMessage] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);
    const [isActionsOpen, setIsActionsOpen] = useState(false);
    const [isUploadOpen, setIsUploadOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();


    /**
     * Handles the click on the Actions button.
     *
     * @returns {void}
     */
    const handleActionsClick = () => {
        setIsActionsOpen(!isActionsOpen);
    };

    /**
     * Handles the click on the Upload button.
     *
     * @returns {void}
     */
    const handleUploadClick = () => {
        setIsUploadOpen(!isUploadOpen);
    };

    /**
     * Fetches album data and sets the state.
     *
     * @returns {void}
     */
    useEffect(() => {
        const fetchData = async () => {
            try {
                const endpoint = `/api/albums/${albumId}`;
                const response = await fetch(endpoint);
                if (response.ok) {
                    const data = await response.json();
                    setAlbumData(data);
                    if (data.parentAlbumId === null || data.parentAlbumId === undefined) {
                        router.push('/albums');

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


    const parentLinkHref = albumData?.parentIsRoot ? '/albums' : `/albums/${albumData?.parentAlbumId}`;

    useEffect(() => {
        if (selectedImageIds.length === 0 && selectedAlbumIds.length === 0) {
            setIsActionsOpen(false);
        }
    }, [selectedImageIds, selectedAlbumIds]);

    if (isLoading) {
        return <Loading/>;
    }

    /**
     * Handles the download action.
     *
     * @returns {Promise<void>}
     */
    const handleDownload = async () => {
        if (selectedImageIds.length === 1 && selectedAlbumIds.length === 0) {
            const image = albumData.images.find(image => image._id.toString() === selectedImageIds[0]);
            const url = image.image_url; // Use image_url instead of url
            const filename = image.filename;
            try {
                setDownloadProgress('Downloading...');
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/download-image?url=${encodeURIComponent(url)}`);
                if (response.ok) {
                    const blob = await response.blob();
                    download(blob, filename, response.headers.get('Content-Type'));
                    setDownloadProgress(null);
                    setSuccessMessage('Download successful');
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
                    let fileName = 'download.zip'; // Default file name

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
        setSelectedAlbumIds([]);
        setIsAllItemsDeselected(true);
    };


    /**
     * Handles the delete action.
     *
     * @returns {Promise<void>}
     */
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
                const response = await axios.delete(`${process.env.NEXT_PUBLIC_API_URL}/delete-images`, {
                    data: {image_ids},
                    headers
                });
                if (response.status === 200) {
                    console.log(response.data.message);
                    setAlbumData(prevState => ({
                        ...prevState,
                        images: prevState.images.filter(image => !image_ids.includes(image._id))
                    }));
                    setSelectedImageIds([]);
                    setSuccessMessage('Delete successful');
                } else {
                    console.error('Failed to delete images');
                    setErrorMessage('Failed to delete images');
                }
            } catch (error) {
                console.error(`Error in handleDelete: ${error.message}`);
                setErrorMessage(`Error in handleDelete`);
            }
        }

        if (album_ids.length > 0) {
            try {
                const response = await axios.delete(`${process.env.NEXT_PUBLIC_API_URL}/delete-albums`, {
                    data: {album_ids},
                    headers
                });
                if (response.status === 200) {
                    console.log(response.data.message);
                    setAlbumData(prevState => ({
                        ...prevState,
                        sons: prevState.sons.filter(album => !album_ids.includes(album._id))
                    }));
                    setSelectedAlbumIds([]);
                    setSuccessMessage('Delete successful');
                } else {
                    setErrorMessage('Failed to delete albums');
                    console.error('Failed to delete albums');
                }
            } catch (error) {
                console.error(`Error in handleDelete: ${error.message}`);
                setErrorMessage(`Error in handleDelete`);
            }
        }
        setIsAllItemsDeselected(true);
    };


    /**
     * Handles the tag submission action.
     *
     * @returns {Promise<void>}
     */
    const handleTagSubmit = async () => {
        if (!tagInput) {
            setErrorMessage('No tags entered');
            return;
        }

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
            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/add-tags-to-selected`, data, {headers});
            if (response.status === 200) {
                console.log(response.data);
                setSuccessMessage('Tags added successfully');
            } else {
                console.error('Failed to add tags');
                setErrorMessage('Failed to add tags');
            }
        } catch (error) {
            console.error(`Error in handleTagSubmit: ${error.message}`);
            setErrorMessage(`Error in handleTagSubmit: ${error.message}`);
        }

        setTagInput('');
        setIsTagModalOpen(false);
        setSelectedImageIds([]);
        setSelectedAlbumIds([]);
        setIsAllItemsDeselected(true);
    };

    /**
     * Handles the Add Tags action.
     *
     * @returns {void}
     */
    const handleAddTags = () => {
        setIsTagModalOpen(true);
    };

    /**
     * Handles the cancel action in the Tag Modal.
     *
     * @returns {void}
     */
    const handleTagModalCancel = () => {
        setTagInput('');
        setIsTagModalOpen(false);
    };

    /**
     * Handles the change in the Tag Input field.
     *
     * @param {Object} e - The event object.
     * @returns {void}
     */
    const handleTagInputChange = (e) => {
        setTagInput(e.target.value);
    };
    if (!albumData) {
        return <Loading/>;
    }

    if ((!albumData.sons.length && !albumData.images.length)) {
        const parentLinkHref = albumData?.parentIsRoot ? '/albums' : `/albums/${albumData?.parentAlbumId}`;
        return <div>
            <AlbumButtons albumId={albumId} parentLinkHref={parentLinkHref} session={session}
                          selectedImageIds={selectedImageIds}
                          selectedAlbumIds={selectedAlbumIds} isActionsOpen={isActionsOpen}
                          handleActionsClick={handleActionsClick} handleAddTags={handleAddTags}
                          handleDownload={handleDownload} handleTagSubmit={handleTagSubmit}
                          handleTagModalCancel={handleTagModalCancel} tagInput={tagInput}
                          handleTagInputChange={handleTagInputChange} downloadProgress={downloadProgress}
                          isConfirmDialogOpen={isConfirmDialogOpen} setIsConfirmDialogOpen={setIsConfirmDialogOpen}
                          handleDelete={handleDelete} isTagModalOpen={isTagModalOpen}
                          setIsTagModalOpen={setIsTagModalOpen}
                          handleUploadClick={handleUploadClick} isUploadOpen={isUploadOpen}/>
            <h2 style={{fontSize: '2em', fontWeight: 'bold', marginTop: '-40px'}}> {albumData.name}:</h2>
            No albums or images found.</div>;
    }

    const albumItems = albumData.sons.map((album, index) => (
        <ImageSelection key={index} item={album} isAlbum={true}/>
    ));
    const imageItems = albumData.images.map((image, idx) => (
        <ImageSelection key={idx} item={image} isAlbum={false}/>
    ));

    /**
     * Renders the SubAlbumPage component.
     *
     * @returns {JSX.Element} - The rendered JSX element.
     */
    return (
        <div className="container">
            {errorMessage && <ErrorWindow message={errorMessage} clearMessage={() => setErrorMessage(null)} />}
            {successMessage && <SuccessWindow message={successMessage} clearMessage={() => setSuccessMessage(null)} />}
            <AlbumButtons albumId={albumId} parentLinkHref={parentLinkHref} session={session}
                          selectedImageIds={selectedImageIds} selectedAlbumIds={selectedAlbumIds}
                          isActionsOpen={isActionsOpen} handleActionsClick={handleActionsClick}
                          isUploadOpen={isUploadOpen} handleUploadClick={handleUploadClick}
                          handleAddTags={handleAddTags} handleDownload={handleDownload}
                          handleTagSubmit={handleTagSubmit} handleTagModalCancel={handleTagModalCancel}
                          tagInput={tagInput} handleTagInputChange={handleTagInputChange}
                          downloadProgress={downloadProgress} isConfirmDialogOpen={isConfirmDialogOpen}
                          setIsConfirmDialogOpen={setIsConfirmDialogOpen} handleDelete={handleDelete}
                          isTagModalOpen={isTagModalOpen} setIsTagModalOpen={setIsTagModalOpen}/>
            <h2 style={{fontSize: '2em', fontWeight: 'bold', marginTop: '-40px'}}> {albumData.name}:</h2>
            <div className="album-container grid-layout">
                {albumItems}
                {imageItems}
            </div>
        </div>
    );
}
