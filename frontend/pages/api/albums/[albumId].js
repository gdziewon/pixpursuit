// pages/api/albums/[albumId].js
import { connectToDatabase } from "@/pages/api/connectMongo";
import { ObjectId } from 'mongodb';
import { isRootId } from "@/utils/isRootId";

export async function getAlbums(albumId = 'root', thumbnailLimit = 50) {
    const db = await connectToDatabase();

    let albumQuery;
    if (typeof albumId === 'string' && albumId === 'root') {
        albumQuery = { "parent": null };
    } else {
        albumQuery = { _id: new ObjectId(albumId) };
    }

    const album = await db.collection("albums").findOne(albumQuery);
    if (!album) {
        throw new Error('Album not found');
    }

    const subAlbums = await db.collection("albums").find({ "parent": album._id.toString() }).toArray();

    const imageIds = album.images ? album.images.slice(0, thumbnailLimit).map(id => new ObjectId(id)) : [];
    const images = imageIds.length > 0 ? await db.collection("images").find({ _id: { $in: imageIds } }).toArray() : [];

    let parentIsRoot = false;
    if (album.parent) {
        parentIsRoot = album.parent ? await isRootId(album.parent) : false;
    }

    const combinedData = {
        ...album,
        parentAlbumId: album.parent,
        parentIsRoot,
        images,
        sons: subAlbums,
        albumId: album._id
    };

    return combinedData;
}

export default async function handler(req, res) {
    let { albumId } = req.query;

    try {
        const albumData = await getAlbums(albumId);
        const responseData = {
            ...albumData,
        };

        res.status(200).json(responseData);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Error fetching album data" });
    }
}