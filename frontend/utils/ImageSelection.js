"use client";

import React, { useState, useContext, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { CheckCircleIcon, PlusCircleIcon } from '@heroicons/react/24/solid';
import {SelectedItemsContext} from '/utils/SelectedItemsContext';
import axios from 'axios';
import { useSession } from 'next-auth/react';
import RenameModal from './RenameModal';
import ErrorWindow from '@/utils/ErrorWindow';
import SuccessWindow from "@/utils/SuccessWindow";

const ImageSelection = ({ item, isAlbum }) => {
    const [isSelected, setIsSelected] = useState(false);
    const [isHovered, setIsHovered] = useState(false);
    const [isRenameButtonVisible, setIsRenameButtonVisible] = useState(false);
    const [isRenameModalOpen, setIsRenameModalOpen] = useState(false);
    const [albumName, setAlbumName] = useState(item.name);
    const { selectedItems, selectItem, deselectItem } = useContext(SelectedItemsContext);
    const { isAllItemsDeselected, setIsAllItemsDeselected } = useContext(SelectedItemsContext);
    const { data: session } = useSession();
    const [errorMessage, setErrorMessage] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    useEffect(() => {
        if (isAllItemsDeselected) {
            setIsSelected(false);
            setIsAllItemsDeselected(false);
        }
    }, [isAllItemsDeselected, setIsAllItemsDeselected]);

    const handleMouseEnter = () => {
        setIsHovered(true);
        if (isAlbum && session) {
            setIsRenameButtonVisible(true);
        }
    };

    const handleMouseLeave = () => {
        setIsHovered(false);
        setIsRenameButtonVisible(false);
    };

    const handleClick = (e) => {
        e.preventDefault();
        setIsSelected((prevSelected) => {
            if (prevSelected) {
                deselectItem(item._id.toString(), isAlbum);
            } else {
                selectItem(item._id.toString(), isAlbum);
            }
            return !prevSelected;
        });
    };

    const handleRenameButtonClick = () => {
        setIsRenameModalOpen(true);
    };

    const handleRenameSubmit = async (e) => {
        e.preventDefault();
        const albumId = item._id;
        const headers = {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${session.accessToken}`,
        };

        if (albumName !== item.name && albumName !== '') {
            try {
                const renameResponse = await axios.put(`${process.env.NEXT_PUBLIC_API_URL}/rename-album`, { album_id: albumId, new_name: albumName }, { headers });
                console.log(renameResponse.data);
                setSuccessMessage("Album renamed successfully");
            } catch (error) {
                console.error("Failed to rename album: ", error);
                setErrorMessage("Failed to rename album"); // set the error state
            }
        }
        setAlbumName(item.name);
        setIsRenameModalOpen(false);


    };

    const handleNameAlbumChange = (e) => {
        setAlbumName(e.target.value);
    };


    return (
        <div onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave} className="relative">
            {errorMessage && <ErrorWindow message={errorMessage} clearMessage={() => setErrorMessage(null)} />}
            {successMessage && <SuccessWindow message={successMessage} clearMessage={() => setSuccessMessage(null)} />}
            {(isAlbum) ? (
                <Link href={`/albums/${item._id}`} passHref>
                    <div className="album-item">
                        <Image src="/dir.png" alt="Directory" width={200} height={200}/>
                        <span>{item.name}</span>
                    </div>
                </Link>
            ) : (
                <Link href={`/gallery/${item._id}`} passHref>
                    <Image src={item.thumbnail_url} alt={item.name} width={200} height={200} />
                </Link>
            )}

            {(isHovered || isSelected) && (
                <button onClick={handleClick} className="absolute top-0 left-2 p-1">
                    {isSelected ? (
                        <CheckCircleIcon className="h-10 w-10 text-blue-500" style={{ position: 'relative', top: isAlbum ? '50px' : '0' }} />
                    ) : (
                        <PlusCircleIcon className="h-10 w-10 text-white opacity-50" style={{ position: 'relative', top: isAlbum ? '50px' : '0' }} />
                    )}
                </button>
            )}

            {isRenameButtonVisible && (
                <button onClick={handleRenameButtonClick} className="absolute top-0 left-0 p-1 bg-blue-500 text-white rounded text-xs">
                    Rename album
                </button>
            )}

            <RenameModal isOpen={isRenameModalOpen} onSubmit={handleRenameSubmit} onCancel={() => setIsRenameModalOpen(false)} handleNameAlbumChange={handleNameAlbumChange} albumName={albumName} />
        </div>
    );
};
export default ImageSelection;