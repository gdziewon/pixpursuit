import { connectToDatabase } from "@/pages/api/connectMongo";

let rootId = null;

export async function isRootId(albumId) {
    if (!albumId) return false;

    const albumId_str = albumId.toString()

    if (rootId) {
        return rootId === albumId_str;
    }

    const db = await connectToDatabase();
    const rootAlbum = await db.collection("albums").findOne({ "parent": null });
    if (!rootAlbum) {
        throw new Error('Root album not found');
    }
    rootId = rootAlbum._id.toString();

    return rootId === albumId_str;
}
