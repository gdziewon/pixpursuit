import { connectToDatabase } from "@/pages/api/connectMongo";
import { ObjectId } from 'mongodb';
import { getRootId } from "@/utils/getRootId";

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
    const rootId = await getRootId();
    if (album.parent) {
        parentIsRoot = album.parent ? rootId === album.parent.toString() : false;
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

export async function getRandomImages(albumId, count) {
    const db = await connectToDatabase();
    const album = await db.collection("albums").findOne({ _id: new ObjectId(albumId) });

    if (!album) {
        throw new Error('Album not found');
    }

    const imageIds = album.images.map(id => new ObjectId(id));
    const images = await db.collection("images").aggregate([
        { $match: { _id: { $in: imageIds } } },
        { $sample: { size: parseInt(count) } }
    ]).toArray();

    return images;
}

export default async function handler(req, res) {
    const { albumId, randomImages, count } = req.query;

    try {
        if (randomImages) {
            const images = await getRandomImages(albumId, count);
            res.status(200).json(images);
        } else {
            const albumData = await getAlbums(albumId);
            const responseData = {
                ...albumData,
            };
            res.status(200).json(responseData);
        }
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: error.message });
    }
}