"use client";

import React, { useState, useContext, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { CheckCircleIcon, PlusCircleIcon } from '@heroicons/react/24/solid';
import {SelectedItemsContext} from '/utils/SelectedItemsContext';

const ImageSelection = ({ item, isAlbum }) => {
    const [isSelected, setIsSelected] = useState(false);
    const [isHovered, setIsHovered] = useState(false);
    const { selectedItems, selectItem, deselectItem } = useContext(SelectedItemsContext);
    const { isAllItemsDeselected, setIsAllItemsDeselected } = useContext(SelectedItemsContext);

    useEffect(() => {
        if (isAllItemsDeselected) {
            setIsSelected(false);
            setIsAllItemsDeselected(false);
        }
    }, [isAllItemsDeselected, setIsAllItemsDeselected]);

    if (!item) {
        return null;
    }

    const handleMouseEnter = () => {
        setIsHovered(true);
    };

    const handleMouseLeave = () => {
        setIsHovered(false);
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
                <button onClick={handleClick} className="absolute top-0 right-2 p-1">
                    {isSelected ? (
                        <CheckCircleIcon className="h-10 w-10 text-blue-500" style={{ position: 'relative', top: isAlbum ? '50px' : '0' }} />
                    ) : (
                        <PlusCircleIcon className="h-10 w-10 text-white opacity-50" style={{ position: 'relative', top: isAlbum ? '50px' : '0' }} />
                    )}
                </button>
            )}
        </div>
    );
};
export default ImageSelection;