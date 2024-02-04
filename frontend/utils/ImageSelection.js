"use client";

import React, { useState, useContext, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { CheckCircleIcon, PlusCircleIcon } from '@heroicons/react/24/solid';
import {SelectedItemsContext} from '/utils/SelectedItemsContext';
import axios from 'axios';
import { useSession } from 'next-auth/react';
import TagModal from './TagModal';

const ImageSelection = ({ item, isAlbum }) => {
    const [isSelected, setIsSelected] = useState(false);
    const [isHovered, setIsHovered] = useState(false);
    const [isAddTagsButtonVisible, setIsAddTagsButtonVisible] = useState(false);
    const [isTagModalOpen, setIsTagModalOpen] = useState(false);
    const [tagInput, setTagInput] = useState('');
    const [albumName, setAlbumName] = useState(item.name);
    const { selectedItems, selectItem, deselectItem } = useContext(SelectedItemsContext);
    const { isAllItemsDeselected, setIsAllItemsDeselected } = useContext(SelectedItemsContext);
    const { data: session } = useSession();

    useEffect(() => {
        if (isAllItemsDeselected) {
            setIsSelected(false);
            setIsAllItemsDeselected(false);
        }
    }, [isAllItemsDeselected, setIsAllItemsDeselected]);

    const handleMouseEnter = () => {
        setIsHovered(true);
        if (isAlbum && session) {
            setIsAddTagsButtonVisible(true);
        }
    };

    const handleMouseLeave = () => {
        setIsHovered(false);
        setIsAddTagsButtonVisible(false);
    };

    const handleClick = (e) => {
        e.preventDefault();
        setIsSelected((prevSelected) => {
            if (prevSelected) {
                deselectItem(item._id.toString(), isAlbum);
            } else {
                selectItem(item._id.toString(), isAlbum);
            }
            console.log('item._id:', item._id);
            return !prevSelected;
        });
    };

    const handleTagButtonClick = () => {
        setIsTagModalOpen(true);
    };

    const handleTagSubmit = async (e) => {
        e.preventDefault();
        const tags = tagInput.split(',').map(tag => tag.trim());
        const albumId = item._id;
        const headers = {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${session.accessToken}`,
        };
        const response = await axios.post('http://localhost:8000/add-tags-to-album', { album_id: albumId, tags: tags }, { headers });
        console.log(response.data);

        if (albumName !== item.name && albumName !== '') {
            try {
                const renameResponse = await axios.put('http://localhost:8000/rename-album', { album_id: albumId, new_name: albumName }, { headers });
                console.log(renameResponse.data);
            } catch (error) {
                console.error("Failed to rename album: ", error);
            }
        }
        setTagInput('');
        setAlbumName(item.name);
        setIsTagModalOpen(false);


    };

    const handleNameAlbumChange = (e) => {
        setAlbumName(e.target.value);
    };

    const handleTagInputChange = (e) => {
        setTagInput(e.target.value);
    };

    return (
        <div onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave} className="relative">
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

            {isAddTagsButtonVisible && (
                <button onClick={handleTagButtonClick} className="absolute top-0 left-0 p-1 bg-blue-500 text-white rounded text-xs">
                    Edit album
                </button>
            )}

            <TagModal isOpen={isTagModalOpen} onSubmit={handleTagSubmit} onCancel={() => setIsTagModalOpen(false)} tagInput={tagInput} handleTagInputChange={handleTagInputChange} handleNameAlbumChange={handleNameAlbumChange} albumName={albumName} />
        </div>
    );
};
export default ImageSelection;