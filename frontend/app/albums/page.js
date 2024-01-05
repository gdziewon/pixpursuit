import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { getAlbums } from "@/utils/getAlbums";

export default async function AlbumsPage() {
    const albumData = await getAlbums();

    if (!albumData || (!albumData.sons.length && !albumData.images.length)) {
        return <div>No albums or images found.</div>;
    }

    const albumItems = albumData.sons.map((album, index) => (
        <Link key={index} href={`/albums/${album._id}`} passHref>
            <div className="album-item">
                <Image src="/dir.png" alt="Directory" width={200} height={200} />
                <span>{album.name}</span>
            </div>
        </Link>
    ));

    const imageItems = albumData.images.map((image, idx) => (
        <Link key={idx} href={`/gallery/${image._id}`} passHref>
            <div>
                <Image src={image.thumbnail_url} alt={image.name} width={200} height={200} />
            </div>
        </Link>
    ));

    return (
        <div className="album-container">
            <div className="mb-12 flex items-center justify-between gap-x-16">
                <div>
                </div>
                <div>
                </div>
                <div className="flex space-x-6">
                    <Link href="/gallery/upload">
                        <h2 className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                            Upload Images to this album
                        </h2>
                    </Link>
                    <Link href={`/albums/add/${albumData.albumId}`} passHref>
                        <h2 className="rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800">
                            Add album
                        </h2>
                    </Link>
                </div>
            </div>
            <div className="albums">{albumItems}</div>
            <div className="images">{imageItems}</div>
        </div>
    );
}
