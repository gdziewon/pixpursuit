import { connectToDatabase } from "@/pages/api/connectMongo";
import { ObjectId } from 'mongodb';

export async function getAlbums(albumId = null, thumbnailLimit = 50) {
    const db = await connectToDatabase();

    let albumQuery = albumId ? { _id: new ObjectId(albumId) } : { "parent": null };

    const album = await db.collection("albums").findOne(albumQuery);
    if (!album) {
        throw new Error('Album not found');
    }

    const subAlbums = await db.collection("albums").find({ "parent": album._id }).toArray();

    const imageIds = album.images ? album.images.slice(0, thumbnailLimit).map(id => new ObjectId(id)) : [];
    const images = imageIds.length > 0 ? await db.collection("images").find({ _id: { $in: imageIds } }).toArray() : [];

    const combinedData = {
        ...album,
        parentAlbumId: album.parent,
        images,
        sons: subAlbums,
        albumId: album._id
    };

    return combinedData;
}
