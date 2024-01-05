"use client";

import React, { useState } from 'react';
import axios from 'axios';
import Link from 'next/link';
import {useSession} from "next-auth/react";
import Image from 'next/image';

const AddAlbumForm = ({params}) => {
    const [albumName, setAlbumName] = useState('');
    const parentAlbumId = params.parentid; // Retrieve the parent album ID from the URL
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
            const response = await axios.post('http://localhost:8000/create-album', albumData, {
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${session.accessToken}`,
                },
            });

            if (response.status === 200) {
                alert("Album created successfully");
                window.location.href = `/albums/${parentAlbumId}`; // Redirect to the parent album
            } else {
                alert("Failed to create album");
            }
        } catch (error) {
            alert("Error creating album");
        }
    };

    return (
        <section>
            <Link href={`/albums/${parentAlbumId}`} passHref>
                <button className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                    Go back
                </button>
            </Link>
            <form onSubmit={handleSubmit}>
                <input type="text" value={albumName} onChange={handleAlbumNameChange} placeholder="Album Name"
                       style={{color: 'black'}}/>
                <button type="submit" className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                    Create Album
                </button>
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
        </section>
    );
};

export default AddAlbumForm;
