"use client";

import React, { createContext, useState } from 'react';

export const SelectedItemsContext = createContext();

export const SelectedItemsProvider = ({ children }) => {
    const [selectedImageIds, setSelectedImageIds] = useState([]);
    const [selectedAlbumIds, setSelectedAlbumIds] = useState([]);

    const selectItem = (id, isAlbum) => {
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
    };

    const deselectItem = (id, isAlbum) => {
        if (isAlbum) {
            setSelectedAlbumIds((prevItems) => prevItems.filter((itemId) => itemId !== id));
        } else {
            setSelectedImageIds((prevItems) => prevItems.filter((itemId) => itemId !== id));
        }
    };

    return (
        <SelectedItemsContext.Provider value={{ selectedImageIds, selectedAlbumIds, setSelectedImageIds, setSelectedAlbumIds, selectItem, deselectItem }}>
            {children}
        </SelectedItemsContext.Provider>
    );
};