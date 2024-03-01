import Link from "next/link";
import {ArrowLeftStartOnRectangleIcon, FolderArrowDownIcon, FolderPlusIcon} from "@heroicons/react/24/outline";
import {ChevronDownIcon, ChevronUpIcon} from "@heroicons/react/24/solid";
import DropdownMenu from "@/utils/DropdownMenu";
import DropdownMenuUpload from "@/utils/DropdownMenuUpload";

export function AlbumButtons({ albumId, parentLinkHref, session, selectedImageIds, selectedAlbumIds, isActionsOpen, handleActionsClick, isUploadOpen, handleUploadClick, handleAddTags, handleDownload, handleTagSubmit, handleTagModalCancel, tagInput, handleTagInputChange, downloadProgress, isConfirmDialogOpen, setIsConfirmDialogOpen, handleDelete, isTagModalOpen, setIsTagModalOpen }) {
    return (
        <div className="mb-12 flex items-center justify-between gap-x-16">
            <div className="flex space-x-6">
                <Link href={parentLinkHref} passHref>
                    <button className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800 flex items-center">
                        <ArrowLeftStartOnRectangleIcon className="h-5 w-5 mr-2"/>
                        Previous album
                    </button>
                </Link>
            </div>
            <div>
            </div>
            <div className="flex space-x-6">
                <div className="relative">
                    {selectedImageIds.length + selectedAlbumIds.length > 0 && (
                        <>
                            <button
                                onClick={handleActionsClick}
                                className="rounded border bg-gray-100 px-3 py-1 text-xs text-gray-800 flex items-center"
                            >
                                Actions
                                {isActionsOpen ? <ChevronUpIcon className="h-5 w-5 ml-2"/> :
                                    <ChevronDownIcon className="h-5 w-5 ml-2"/>}
                            </button>
                            <DropdownMenu
                                isActionsOpen={isActionsOpen}
                                handleActionsClick={handleActionsClick}
                                handleAddTags={handleAddTags}
                                handleDownload={handleDownload}
                                handleTagSubmit={handleTagSubmit}
                                handleTagModalCancel={handleTagModalCancel}
                                tagInput={tagInput}
                                handleTagInputChange={handleTagInputChange}
                                downloadProgress={downloadProgress}
                                isConfirmDialogOpen={isConfirmDialogOpen}
                                setIsConfirmDialogOpen={setIsConfirmDialogOpen}
                                handleDelete={handleDelete}
                                isTagModalOpen={isTagModalOpen}
                                setIsTagModalOpen={setIsTagModalOpen}
                            />
                        </>
                    )}
                </div>
                {session && (
                    <div className="flex space-x-6">
                        <DropdownMenuUpload
                            isUploadOpen={isUploadOpen}
                            handleUploadClick={handleUploadClick}
                            albumId={albumId}
                        />
                        <Link href={`/albums/add/${albumId}`} passHref>
                            <button
                                className="rounded border bg-gray-100 px-2 py-1 text-xs text-gray-800 flex items-center">
                                <FolderPlusIcon className="h-5 w-5 mr-2"/>
                                Add album
                            </button>
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
}