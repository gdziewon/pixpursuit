import React from 'react';
import { useSession } from 'next-auth/react';
import ConfirmDialog from "/utils/ConfirmDialog";
import TagModal from "/utils/TagModal";

/**
 * Renders a dropdown menu with various actions.
 *
 * @param {Object} props - The props.
 * @param {boolean} props.isActionsOpen - Whether the actions dropdown is open.
 * @param {Function} props.handleActionsClick - The function to handle click on actions.
 * @param {Function} props.handleAddTags - The function to handle adding tags.
 * @param {Function} props.handleDownload - The function to handle download.
 * @param {Function} props.handleTagSubmit - The function to handle tag submission.
 * @param {Function} props.handleTagModalCancel - The function to handle tag modal cancellation.
 * @param {Object} props.tagInput - The tag input object.
 * @param {Function} props.handleTagInputChange - The function to handle tag input change.
 * @param {number} props.downloadProgress - The download progress.
 * @param {boolean} props.isConfirmDialogOpen - Whether the confirm dialog is open.
 * @param {Function} props.setIsConfirmDialogOpen - The function to set whether the confirm dialog is open.
 * @param {Function} props.handleDelete - The function to handle delete.
 * @param {boolean} props.isTagModalOpen - Whether the tag modal is open.
 * @param {Function} props.setIsTagModalOpen - The function to set whether the tag modal is open.
 * @returns {JSX.Element|null} - The rendered JSX element, or null if the actions dropdown is not open.
 */
const DropdownMenu = ({ isActionsOpen, handleActionsClick, handleAddTags, handleDownload, handleTagSubmit, handleTagModalCancel, tagInput, handleTagInputChange, downloadProgress, isConfirmDialogOpen, setIsConfirmDialogOpen, handleDelete, isTagModalOpen, setIsTagModalOpen }) => {
    const { data: session } = useSession();

    if (!isActionsOpen) {
        return null;
    }

    const buttonStyle = {
        width: '95px',
        height: '30px',
    };

    return (
        <div
            className="absolute below-5 mt-1 w-100 rounded-md shadow-lg bg-gray-300 ring-1 ring-black ring-opacity-5 z-50">
            <div className="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
                {downloadProgress === null ? (
                    <>
                    <button
                        onClick={handleDownload}
                        style={buttonStyle}
                        className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-800 flex items-center"
                    >
                        Download
                    </button>
                        {session && (
                            <>
                                <button onClick={handleAddTags}
                                        style={buttonStyle}
                                        className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-800 flex items-center">
                                    Add tags
                                </button>
                                <button
                                    onClick={() => setIsConfirmDialogOpen(true)}
                                    style={buttonStyle}
                                    className="rounded border bg-gray-100 px-3 py-1 text-xs text-red-700 flex items-center"
                                >
                                    Delete
                                </button>
                            </>
                        )}
                        <ConfirmDialog
                            isOpen={isConfirmDialogOpen}
                            onConfirm={() => {
                                handleDelete();
                                setIsConfirmDialogOpen(false);
                            }}
                            onCancel={() => setIsConfirmDialogOpen(false)}
                        />
                        <TagModal
                            isOpen={isTagModalOpen}
                            onSubmit={handleTagSubmit}
                            onCancel={handleTagModalCancel}
                            tagInput={tagInput}
                            handleTagInputChange={handleTagInputChange}
                        />
                    </>
                ) : (
                    <div className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-700 flex items-center">
                        {downloadProgress}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DropdownMenu;