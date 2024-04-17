import { connectToDatabase } from "@/pages/api/connectMongo";

let rootId = null;

/**
 * Fetches the root ID from the database.
 *
 * @returns {Promise<string>} - A promise that resolves to the root ID.
 * @throws {Error} - If the root album is not found or if there is an error connecting to the database.
 */
export async function getRootId() {
    try {
        if (rootId) {
            return rootId;
        }

        const db = await connectToDatabase();
        const rootAlbum = await db.collection("albums").findOne({ "parent": null });
        if (!rootAlbum) {
            throw new Error('Root album not found');
        }
        rootId = rootAlbum._id.toString();

        return rootId;
    } catch (error) {
        console.error(error);
        throw error;
    }
}
