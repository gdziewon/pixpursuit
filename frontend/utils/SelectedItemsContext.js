"use client";

import React, { createContext, useState } from 'react';

/**
 * Provides the selected items' context.
 *
 * @param {Object} props - The props.
 * @param {ReactNode} props.children - The children to be rendered within this context provider.
 * @returns {JSX.Element} - The rendered JSX element.
 */
export const SelectedItemsContext = createContext();

export const SelectedItemsProvider = ({ children }) => {
    const [selectedImageIds, setSelectedImageIds] = useState([]);
    const [selectedAlbumIds, setSelectedAlbumIds] = useState([]);
    const [isAllItemsDeselected, setIsAllItemsDeselected] = useState(false);

    const selectItem = (id, isAlbum) => {
        try {
            if (isAlbum) {
                setSelectedAlbumIds((prevItems) => {
                    if (!prevItems.includes(id)) {
                        return [...prevItems, id];
                    }
                    return prevItems;
                });
            } else {
                setSelectedImageIds((prevItems) => {
                    if (!prevItems.includes(id)) {
                        return [...prevItems, id];
                    }
                    return prevItems;
                });
            }
        } catch (error) {
            console.error(`Error selecting item: ${error}`);
            throw error;
        }
    };

    const deselectItem = (id, isAlbum) => {
        try {
            if (isAlbum) {
                setSelectedAlbumIds((prevItems) => prevItems.filter((itemId) => itemId !== id));
            } else {
                setSelectedImageIds((prevItems) => prevItems.filter((itemId) => itemId !== id));
            }
        } catch (error) {
            console.error(`Error deselecting item: ${error}`);
            throw error;
        }
    };

    return (
        <SelectedItemsContext.Provider value={{ selectedImageIds, selectedAlbumIds, setSelectedImageIds, setSelectedAlbumIds, selectItem, deselectItem, isAllItemsDeselected, setIsAllItemsDeselected }}>
            {children}
        </SelectedItemsContext.Provider>
    );
};