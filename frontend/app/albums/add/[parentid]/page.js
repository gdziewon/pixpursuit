'use client'

import React, { useState } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useSession } from "next-auth/react";
import Image from 'next/image';
import { FolderPlusIcon, ArrowLeftStartOnRectangleIcon } from '@heroicons/react/24/outline';

const AddAlbumForm = ({ params }) => {
    const [albumName, setAlbumName] = useState('');
    const parentAlbumId = params.parentid;
    const { data: session } = useSession();

    const handleAlbumNameChange = (e) => {
        setAlbumName(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const albumData = {
            album_name: albumName,
            parent_id: parentAlbumId,
            image_ids: [] // Ignoring image IDs for now
        };

        try {
            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/create-album`, albumData, {
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${session.accessToken}`,
                },
            });

            if (response.status === 200) {
                alert("Album created successfully");
                window.location.href = `/albums/${parentAlbumId}`;
            } else {
                alert("Failed to create album");
            }
        } catch (error) {
            alert("Error creating album");
        }
    };

    return (
        <section className="add-album-form">
            <div className="navigation-button">
                <Link href={`/albums/${parentAlbumId}`} passHref>
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
