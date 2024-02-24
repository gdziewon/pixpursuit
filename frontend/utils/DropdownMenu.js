import React from 'react';
import ConfirmDialog from "/utils/ConfirmDialog";
import TagModal from "/utils/TagModal";

const DropdownMenu = ({ isActionsOpen, handleActionsClick, handleAddTags, handleDownload, handleTagSubmit, handleTagModalCancel, tagInput, handleTagInputChange, downloadProgress, isConfirmDialogOpen, setIsConfirmDialogOpen, handleDelete, isTagModalOpen, setIsTagModalOpen }) => {
    if (!isActionsOpen) {
        return null;
    }

    return (
        <div className="absolute below-5 mt-1 w-100 rounded-md shadow-lg bg-gray-300 ring-1 ring-black ring-opacity-5 z-50">
            <div className="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
                {downloadProgress === null ? (
                    <>
                        <button
                            onClick={() => setIsConfirmDialogOpen(true)}
                            className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-800 flex items-center"
                        >
                            Delete selected
                        </button>
                        <button onClick={handleAddTags}
                                className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-800 flex items-center">
                            Add tags to selected
                        </button>
                        <button
                            onClick={handleDownload}
                            className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-800 flex items-center"
                        >
                            Download selected
                        </button>
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
                    <div>
                        {downloadProgress}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DropdownMenu;