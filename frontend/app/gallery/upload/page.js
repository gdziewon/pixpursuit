'use client'

import React, { useState, useRef } from 'react';
import { useSession } from 'next-auth/react';
import axios from 'axios';
import Image from 'next/image';
import Loading from '@/app/loading';
import { DocumentDuplicateIcon,  CloudArrowUpIcon} from '@heroicons/react/24/outline';

const UploadForm = () => {
    const [images, setImages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const { data: session } = useSession();
    const fileInputRef = useRef(null);

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
            <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                {images.map((img, index) => (
                    <div key={index} style={{ margin: '5px' }}>
                        <Image src={URL.createObjectURL(img)} alt={`image-${index}`} width="200" height="200"/>
                        <button onClick={() => handleRemoveImage(index)}>Remove</button>
                    </div>
                ))}
            </div>
        </section>
    );
};

export default UploadForm;
