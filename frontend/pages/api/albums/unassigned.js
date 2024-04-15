import { connectToDatabase } from "@/pages/api/connectMongo";
import { ObjectId } from "mongodb";

// Function to get unassigned images
export async function getUnassignedImages(albumId = "root") {
  const db = await connectToDatabase();

  // Prepare the album query
  let albumQuery;
  if (typeof albumId === "string" && albumId === "root") {
    albumQuery = {};
  } else {
    albumQuery = { _id: new ObjectId(albumId) };
  }

  // Fetch the album
  const rootAlbum = await db.collection("albums").findOne(albumQuery);
  if (!rootAlbum) {
    throw new Error("Root album not found");
  }

  // Fetch images for the root album
  const imageIds = rootAlbum.images
    ? rootAlbum.images.map((id) => new ObjectId(id))
    : [];
  const images =
    imageIds.length > 0
      ? await db
          .collection("images")
          .find({ _id: { $in: imageIds } })
          .toArray()
      : [];

  return images;
}

// Main handler function
export default async function handler(req, res) {
  try {
    const images = await getUnassignedImages();
    res.status(200).json(images);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: error.message });
  }
}
