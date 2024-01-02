"use client";

import React, { useState } from 'react';
import { useSession } from 'next-auth/react';
import axios from 'axios';
import Image from 'next/image'

const UploadForm = () => {
    const [image, setImage] = useState(null);
    const { data: session } = useSession();

    const handleImageChange = (e) => {
        if (e.target.files) {
            setImage(Array.from(e.target.files));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        image.forEach((img) => formData.append('images', img));

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
                    alert("Upload failed")
                }
            } catch (error) {
                alert("Upload failed")
            }

    };

    return (
        <section className="fa-upload">
            <form onSubmit={handleSubmit}>
                <input type="file" onChange={handleImageChange} multiple/>
                <button type="submit">Upload Images</button>
            </form>
            <div>
                {image && image.map((img, index) => (
                    <Image key={index} src={URL.createObjectURL(img)} alt={`image-${index}`} width="600" height="600"/>
                ))}
            </div>
        </section>
    );
};

export default UploadForm;
