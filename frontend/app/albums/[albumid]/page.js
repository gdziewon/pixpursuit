import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { getAlbums } from "@/utils/getAlbums";
import { isRootId} from "@/utils/isRootId";

export default async function SubAlbumPage({ params }) {
    const albumId = params.albumid;
    const albumData = await getAlbums(albumId);

    const isRoot = albumData.parentAlbumId ? await isRootId(albumData.parentAlbumId) : true;

    const parentLinkHref = isRoot ? '/albums' : `/albums/${albumData.parentAlbumId}`;

    if (!albumData || (!albumData.sons.length && !albumData.images.length)) {
        return <div>
            <Link href={parentLinkHref} passHref>
                <div className="up-arrow-icon">
                    <Image src="/up-arrow.png" alt="Up-arrow" width={100} height={100} />
                </div>
            </Link>No albums or images found.</div>;
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
            <Link href={parentLinkHref} passHref>
                <div className="up-arrow-icon">
                    <Image src="/up-arrow.png" alt="Up-arrow" width={100} height={100} />
                </div>
            </Link>
            <div className="albums">{albumItems}</div>
            <div className="images">{imageItems}</div>
        </div>
    );
}
