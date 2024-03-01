import React, { useEffect, useRef } from 'react';
import Link from 'next/link';
import { ChevronUpIcon, ChevronDownIcon } from "@heroicons/react/24/solid";

const DropdownMenuUpload = ({
    isUploadOpen,
    handleUploadClick,
    albumId
}) => {
    const dropdownRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                handleUploadClick();
            }
        }

        if (isUploadOpen) {
            document.addEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [isUploadOpen, handleUploadClick]);

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={handleUploadClick}
                className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-800 flex items-center"
            >
                Upload
                {isUploadOpen ? <ChevronUpIcon className="h-5 w-5 ml-3"/> :
                    <ChevronDownIcon className="h-5 w-5 ml-3"/>}
            </button>
            {isUploadOpen && (
                <div className="absolute below-5 mt-1 w-100 rounded-md shadow-lg bg-gray-300 ring-1 ring-black ring-opacity-5 z-50">
                    <div className="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
                        <Link href={`/gallery/upload/galeria_pk`}>
                            <div className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-800 flex items-center">
                                from GaleriaPK
                            </div>
                        </Link>
                        <Link href={`/gallery/upload/zip/`}>
                            <div className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-800 flex items-center">
                                ZIP file
                            </div>
                        </Link>
                        <Link href={`/gallery/upload/${albumId}`}>
                            <div className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-800 flex items-center">
                                Images
                            </div>
                        </Link>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DropdownMenuUpload;