'use client'

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useSession } from "next-auth/react";
import Image from 'next/image';
import { FolderPlusIcon, ArrowLeftStartOnRectangleIcon } from '@heroicons/react/24/outline';
import SuccessWindow from '@/utils/SuccessWindow';
import ErrorWindow from '@/utils/ErrorWindow';

const AddAlbumForm = ({ params }) => {
    const [albumName, setAlbumName] = useState('');
    const parentAlbumId = params.parentid;
    const { data: session } = useSession();
    const [errorMessage, setErrorMessage] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    const handleAlbumNameChange = (e) => {
        setAlbumName(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!albumName) {
            setErrorMessage('Name not entered');
            return;
        }

        const albumData = {
            album_name: albumName,
            parent_id: parentAlbumId !== 'root' ? parentAlbumId : null,
        };

        try {
            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/create-album`, albumData, {
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${session.accessToken}`,
                },
            });

            if (response.status === 200) {
                window.location.href = `/albums/${parentAlbumId !== 'root' ? parentAlbumId : ""}`;
                localStorage.setItem('successMessage', "Album added successfully");
            } else {
                setErrorMessage("Failed to create album");
            }
        } catch (error) {
            console.error(`Error in handleSubmit: ${error.message}`);
            setErrorMessage("Failed to create album");
        }
    };

    useEffect(() => {
        const successMessage = localStorage.getItem('successMessage');
        if (successMessage) {
            setSuccessMessage(successMessage);
            localStorage.removeItem('successMessage');
        }
    }, []);

    return (
        <section className="add-album-form">
            {errorMessage && <ErrorWindow message={errorMessage} clearMessage={() => setErrorMessage(null)} />}
            {successMessage && <SuccessWindow message={successMessage} clearMessage={() => setSuccessMessage(null)} />}
            <div className="navigation-button">
                <Link href={`/albums/${parentAlbumId !== 'root' ? parentAlbumId : ""}`} passHref>
                    <button className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center">
                        <ArrowLeftStartOnRectangleIcon className="h-5 w-5 mr-2"/>
                        Go back
                    </button>
                </Link>
            </div>
            <form onSubmit={handleSubmit} className="album-form">
                <div className="input-group">
                    <input
                        type="text"
                        value={albumName}
                        onChange={handleAlbumNameChange}
                        placeholder="Album Name"
                        className="album-name-input rounded border px-3 py-2 text-sm text-black"
                    />
                    <button
                        type="submit"
                        className="create-album-button rounded border bg-blue-500 px-3 py-2 text-sm text-white flex items-center"
                    >
                        <FolderPlusIcon className="h-5 w-5 mr-2"/>
                        Create Album
                    </button>
                </div>
            </form>
            <div className="image-container" style={{marginTop: '20px'}}>
                <Image
                    src="/dir.png"
                    alt="Directory"
                    width={400}
                    height={400}
                    layout="fixed"
                />
            </div>
            <style jsx>{`
                .add-album-form {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 20px;
                }

                .navigation-button {
                    align-self: start;
                }

                .album-form {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                    width: 100%;
                }

                .input-group {
                    display: flex;
                    gap: 10px;
                }

                .album-name-input, .create-album-button {
                    flex: 1;
                }

                .create-album-button {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
            `}</style>
        </section>
    );
};

export default AddAlbumForm;
