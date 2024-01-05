"use client";

import React, { useState } from 'react';
import { useSession } from 'next-auth/react';
import axios from 'axios';
import Image from 'next/image';

const UploadToAlbumForm = ({params}) => {
    const [images, setImages] = useState(null);
    const { data: session } = useSession();
    const albumId = params.albumid;

    const handleImageChange = (e) => {
        if (e.target.files) {
            setImages(Array.from(e.target.files));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();

        images.forEach((img) => formData.append('images', img));
        formData.append('album_id', albumId.toString());

        try {
            const response = await axios.post('http://localhost:8000/process-images', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${session.accessToken}`,
                },
            });
            // Handle successful upload
            if (response.status === 200) {
                alert("Images uploaded successfully");
            } else {
                alert("Upload failed");
            }
        } catch (error) {
            console.error(error);
            alert("Upload failed");
        }
    };

    return (
        <section className="fa-upload">
            <form onSubmit={handleSubmit}>
                <input type="file" onChange={handleImageChange} multiple/>
                <button type="submit" className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                    Upload Images
                </button>
            </form>
            <div>
                {images && images.map((img, index) => (
                    <Image key={index} src={URL.createObjectURL(img)} alt={`image-${index}`} width="600" height="600"/>
                ))}
            </div>
        </section>
    );
};

export default UploadToAlbumForm;
