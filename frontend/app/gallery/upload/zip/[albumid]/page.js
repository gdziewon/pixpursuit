"use client";

import React, { useState, useRef } from 'react';
import { useSession } from 'next-auth/react';
import axios from 'axios';
import { CloudArrowUpIcon } from '@heroicons/react/24/outline';
import Image from "next/image";
import Loading from '@/app/loading';

const UploadZipForm = ({params}) => {
    const { data: session } = useSession();
    const fileInputRef = useRef(null);
    const [successMessage, setSuccessMessage] = useState('');
    const albumId = params.albumid;
    const [uploadedFile, setUploadedFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');

    const handleButtonClick = () => {
        fileInputRef.current.click();
    };

    const handleImageChange = (e) => {
        setUploadedFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('file', fileInputRef.current.files[0]);
        formData.append('parent_id', albumId.toString());

        setIsLoading(true);

        try {
            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/upload-zip`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${session.accessToken}`,
                },
            });
            setSuccessMessage('Zip file uploaded successfully!');
            console.log(response.data);
        } catch (error) {
            console.error(error);
            setErrorMessage(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <section className="fa-upload">
            {isLoading ? <Loading /> : (
                <>
                    {successMessage && <div className="alert alert-success">{successMessage}</div>}
                    {errorMessage && <div className="alert alert-danger">{errorMessage}</div>}
                    <form onSubmit={handleSubmit} className="flex items-center">
                        <input
                            type="file"
                            ref={fileInputRef}
                            accept=".zip"
                            style={{display: 'none'}}
                            onChange={handleImageChange}
                        />
                        <button
                            type="button"
                            onClick={handleButtonClick}
                            className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center"
                        >
                            <CloudArrowUpIcon className="h-5 w-5 mr-2"/>
                            Select Zip
                        </button>
                        <button
                            type="submit"
                            className="rounded border bg-blue-500 px-3 py-1 text-sm text-white flex items-center ml-3"
                        >
                            <CloudArrowUpIcon className="h-5 w-5 mr-2"/>
                            Upload
                        </button>
                    </form>
                    {uploadedFile && (
                        <div>
                            <Image src="/zip.png" alt="zip icon" width="400" height="400"/>
                            <p>{uploadedFile.name}</p>
                        </div>
                    )}
                </>
            )}
        </section>
    );
};

export default UploadZipForm;