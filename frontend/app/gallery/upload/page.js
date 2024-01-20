'use client'

import React, { useState, useRef } from 'react';
import { useSession } from 'next-auth/react';
import axios from 'axios';
import Image from 'next/image';
import Loading from '@/app/loading';
import { DocumentDuplicateIcon,  CloudArrowUpIcon} from '@heroicons/react/24/outline';
import { toBlob } from 'html-to-image';

const UploadForm = () => {
    const [images, setImages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const { data: session } = useSession();
    const fileInputRef = useRef(null);
    const [resizeValues, setResizeValues] = useState({});
    const [showResizeFields, setShowResizeFields] = useState({})

    const handleButtonClick = () => {
        fileInputRef.current.click();
    };

    const handleImageChange = (e) => {
        setImages([...images, ...Array.from(e.target.files)]);
    };

    const handleRemoveImage = (index) => {
        setImages(images.filter((_, i) => i !== index));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        const formData = new FormData();
        images.forEach((img) => formData.append('images', img));

        try {
            const response = await axios.post('http://localhost:8000/process-images', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${session.accessToken}`,
                },
            });
            alert(response.status === 200 ? "Images uploaded successfully" : "Upload failed");
        } catch (error) {
            alert("Upload failed");
        } finally {
            setIsLoading(false);
            setImages([]);
        }
    };

    const handleResizeImage = async (img, index) => {
        const newWidth = resizeValues[index]?.width;
        const newHeight = resizeValues[index]?.height;

        if (!newWidth || !newHeight) {
            alert('Please enter width and height');
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
    };

    const handleResizeInputChange = (index, dimension, value) => {
        setResizeValues({
            ...resizeValues,
            [index]: { ...resizeValues[index], [dimension]: value },
        });
    };

    const handleResizeButtonClick = async (img, index) => {
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
    };

    return (
        <section className="fa-upload">
            {isLoading && <Loading />}
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

export default UploadForm;
