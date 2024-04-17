import Link from "next/link";
import {ArrowLeftStartOnRectangleIcon,  FolderPlusIcon} from "@heroicons/react/24/outline";
import {ChevronDownIcon, ChevronUpIcon} from "@heroicons/react/24/solid";
import DropdownMenu from "@/utils/DropdownMenu";
import DropdownMenuUpload from "@/utils/DropdownMenuUpload";

/**
 * Renders the album buttons.
 *
 * @param {Object} props - The props.
 * @param {string} props.albumId - The ID of the album.
 * @param {string} props.parentLinkHref - The href of the parent link.
 * @param {Object} props.session - The session object.
 * @param {Array<string>} props.selectedImageIds - The IDs of the selected images.
 * @param {Array<string>} props.selectedAlbumIds - The IDs of the selected albums.
 * @param {boolean} props.isActionsOpen - Whether the actions dropdown is open.
 * @param {Function} props.handleActionsClick - The function to handle click on actions.
 * @param {boolean} props.isUploadOpen - Whether the upload dropdown is open.
 * @param {Function} props.handleUploadClick - The function to handle click on upload.
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
 * @returns {JSX.Element} - The rendered JSX element.
 */
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