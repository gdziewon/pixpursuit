'use client'

import React, { useState, useRef } from 'react';
import { useSession } from 'next-auth/react';
import axios from 'axios';
import Image from 'next/image';
import Loading from '@/app/loading';
import { DocumentDuplicateIcon, CloudArrowUpIcon } from '@heroicons/react/24/outline';
import { signIn } from 'next-auth/react';

const UploadToAlbumForm = ({ params }) => {
    const [images, setImages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const { data: session } = useSession();
    const albumId = params.albumid;
    const fileInputRef = useRef(null);
    const [resizeValues, setResizeValues] = useState({});
    const [showResizeFields, setShowResizeFields] = useState({})
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null)

    const handleImageChange = (e) => {
        try {
            setImages([...Array.from(e.target.files)]);
            setError(null);
        } catch (error) {
            setError("An error occurred while changing the image: " + error.message);
        }
    };

    const handleButtonClick = () => {
        try {
            fileInputRef.current.click();
        } catch (error) {
            setError("An error occurred while handling the button click: " + error.message);
        }
    };

    const handleRemoveImage = (index) => {
        try {
            setImages(images.filter((_, i) => i !== index));
        } catch (error) {
            setError("An error occurred while removing the image: " + error.message);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (images.length === 0) {
            setError('You have not selected images to upload');
            return;
        }

        setIsLoading(true);
        const formData = new FormData();
        images.forEach((img) => formData.append('images', img));
        formData.append('album_id', albumId.toString());

        try {
            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/process-images`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${session.accessToken}`,
                },
            });
            if (response.status === 200) {
                setSuccess("Images uploaded successfully");
            } else {
                setError("Upload failed");
            }
        } catch (error) {
            if (error.response && error.response.status === 401) {
                signIn();
            } else {
                setError("Upload failed");
            }
        } finally {
            setIsLoading(false);
            setImages([]);
        }
    };

    const handleResizeImage = async (img, index) => {
        try {
            const newWidth = resizeValues[index]?.width;
            const newHeight = resizeValues[index]?.height;

            if (!newWidth || !newHeight) {
                setError('Please enter width and height');
                return;
            }
            const image = new window.Image();
            image.src = URL.createObjectURL(img);
            await new Promise((resolve) => {
                image.onload = resolve;
            });

            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = newWidth;
            canvas.height = newHeight;
            ctx.drawImage(image, 0, 0, newWidth, newHeight);

            canvas.toBlob((blob) => {
                setImages(images.map((img, i) => (i === index ? blob : img)));
                setResizeValues({
                    ...resizeValues,
                    [index]: { width: newWidth, height: newHeight },
                });
                setShowResizeFields({ ...showResizeFields, [index]: false });
            }, 'image/jpeg');
        } catch (error) {
            setError("Image resize failed due to an error: " + error.message);
        }
    };

    const handleResizeInputChange = (index, dimension, value) => {
        try {
            setResizeValues({
                ...resizeValues,
                [index]: { ...resizeValues[index], [dimension]: value },
            });
        } catch (error) {
            setError("An error occurred while resizing the image input change: " + error.message);
        }
    };

    const handleResizeButtonClick = async (img, index) => {
        try {
            if (showResizeFields[index]) {
                await handleResizeImage(img, index);
            } else {
                const image = new window.Image();
                image.src = URL.createObjectURL(img);
                image.onload = () => {
                    setResizeValues({
                        ...resizeValues,
                        [index]: { width: image.naturalWidth, height: image.naturalHeight },
                    });
                };
            }
            setShowResizeFields({ ...showResizeFields, [index]: !showResizeFields[index] });
        } catch (error) {
            setError("An error occurred while resizing the image: " + error.message);
        }
    };

    return (
        <section className="fa-upload">
            {isLoading && <Loading />}
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            <form onSubmit={handleSubmit} className="flex items-center">
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleImageChange}
                    multiple
                    accept=".png, .jpg, .jpeg"
                    style={{ display: 'none' }}
                />
                <button
                    type="button"
                    onClick={handleButtonClick}
                    className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center"
                >
                    <DocumentDuplicateIcon className="h-5 w-5 mr-2" />
                    Browse...
                </button>
                <span className="mx-3">
                    {images.length > 0 ? `Files chosen: ${images.length}` : 'No files chosen'}
                </span>
                <button
                    type="submit"
                    className="rounded border bg-blue-500 px-3 py-1 text-sm text-white flex items-center"
                >
                    <CloudArrowUpIcon className="h-5 w-5 mr-2" />
                    Upload
                </button>
            </form>
            <div style={{display: 'flex', flexWrap: 'wrap'}}>
                {images.map((img, index) => (
                    <div key={index} style={{margin: '5px', width: '200px', height: '200px'}}>
                        <Image src={URL.createObjectURL(img)} alt={`image-${index}`} width="200" height="200"/>
                        <div style={{
                            width: '100%',
                            display: 'flex',
                            justifyContent: 'space-between'
                        }}>
                            <button onClick={() => handleRemoveImage(index)}>Remove</button>
                            <button onClick={() => handleResizeButtonClick(img, index)}>Resize</button>
                        </div>
                        {showResizeFields[index] && (
                            <div>
                                <label>
                                    W:
                                    <input
                                        type="number"
                                        value={resizeValues[index]?.width || ''}
                                        onChange={(e) => handleResizeInputChange(index, 'width', e.target.value)}
                                        style={{width: '70px', color: 'black'}}
                                    />
                                </label>
                                <label>
                                    H:
                                    <input
                                        type="number"
                                        value={resizeValues[index]?.height || ''}
                                        onChange={(e) => handleResizeInputChange(index, 'height', e.target.value)}
                                        style={{width: '70px', color: 'black'}}
                                    />
                                </label>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </section>
    );
};

export default UploadToAlbumForm;
