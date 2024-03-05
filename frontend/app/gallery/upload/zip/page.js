"use client";

import React, { useState, useRef } from 'react';
import { useSession } from 'next-auth/react';
import axios from 'axios';
import { CloudArrowUpIcon } from '@heroicons/react/24/outline';
import Image from 'next/image';
import Loading from '@/app/loading';
import SuccessWindow from '@/utils/SuccessWindow';
import ErrorWindow from '@/utils/ErrorWindow';
import { signIn } from 'next-auth/react';

const UploadZipForm = () => {
    const { data: session } = useSession();
    const fileInputRef = useRef(null);
    const [successMessage, setSuccessMessage] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [uploadedFile, setUploadedFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleButtonClick = () => {
        fileInputRef.current.click();
    };

    const handleImageChange = (e) => {
        setUploadedFile(e.target.files[0]);
        setErrorMessage(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        const file = fileInputRef.current.files[0];

        setSuccessMessage('');
        setErrorMessage('');

        if (!file) {
            setErrorMessage('ZIP not selected');
            return;
        }
        formData.append('file', fileInputRef.current.files[0]);

        setIsLoading(true);

        try {
            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/upload-zip`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${session.accessToken}`,
                },
            });
            if (response.status === 200) {
                setSuccessMessage('ZIP uploaded successfully');
                console.log(response.data);
            }else if(response.status === 413){
                setErrorMessage('ZIP size too large');
            }else{
                setErrorMessage('Upload failed');
            }
        } catch (error) {
            if (error.code === 'ERR_NETWORK') {
                setErrorMessage("ZIP size too large");
            } else if (error.response && error.response.status === 401) {
                signIn();
            } else {
                setErrorMessage("Upload failed");
            }

            console.error(error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <section className="fa-upload">
            {isLoading ? <Loading /> : (
                <>
                    {errorMessage && <ErrorWindow message={errorMessage} clearMessage={() => setErrorMessage(null)} />}
                    {successMessage && <SuccessWindow message={successMessage} clearMessage={() => setSuccessMessage(null)} />}
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