import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { getAlbums } from "@/utils/getAlbums";
import { isRootId} from "@/utils/isRootId";
import "/styles/album_layout_styles.css"

export default async function SubAlbumPage({ params }) {
    const albumId = params.albumid;
    const albumData = await getAlbums(albumId);


    const isRoot = albumData.parentAlbumId ? await isRootId(albumData.parentAlbumId) : true;

    const parentLinkHref = isRoot ? '/albums' : `/albums/${albumData.parentAlbumId}`;

    if (!albumData || (!albumData.sons.length && !albumData.images.length)) {
        return <div>
            <div className="mb-12 flex items-center justify-between gap-x-16">
                <div className="flex space-x-6">
                    <Link href={parentLinkHref} passHref>
                        <h2 className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                            Previous album
                        </h2>
                    </Link>
                </div>
                <div>
                </div>
                <div className="flex space-x-6">
                    <Link href={`/gallery/upload/${albumId}`} passHref>
                        <h2 className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                            Upload Images to this album
                        </h2>
                    </Link>
                    <Link href={`/albums/add/${albumId}`} passHref>
                        <h2 className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                            Add album
                        </h2>
                    </Link>
                </div>
            </div>
            No albums or images found.</div>;
    }

    const albumItems = albumData.sons.map((album, index) => (
        <Link key={index} href={`/albums/${album._id}`} passHref>
            <div className="album-item">
                <Image src="/dir.png" alt="Directory" width={200} height={200}/>
                <span>{album.name}</span>
            </div>
        </Link>
    ));
    const imageItems = albumData.images.map((image, idx) => (
        <Link key={idx} href={`/gallery/${image._id}`} passHref>
            <div>
                <Image src={image.thumbnail_url} alt={image.name} width={200} height={200}/>
            </div>
        </Link>
    ));

    return (
        <div className="container">
            <div className="mb-12 flex items-center justify-between gap-x-16">
                <div className="flex space-x-6">
                    <Link href={parentLinkHref} passHref>
                        <h2 className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                            Previous album
                    </h2>
                </Link>
                </div>
                <div>
                </div>
                <div className="flex space-x-6">
                    <Link href={`/gallery/upload/${albumId}`} passHref>
                        <h2 className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                            Upload Images to this album
                        </h2>
                    </Link>
                    <Link href={`/albums/add/${albumId}`} passHref>
                        <h2 className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                            Add album
                        </h2>
                    </Link>
                </div>
            </div>
            <div className="album-container grid-layout">
                {albumItems}
                {imageItems}
            </div>
        </div>
    );
}
