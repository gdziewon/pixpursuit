import { connectToDatabase } from "@/pages/api/connectMongo";
import { ObjectId } from "mongodb";
import { getRootId } from "@/utils/getRootId";

// Function to get albums with pagination
export async function getAlbums(
  albumId = "root",
  thumbnailLimit = 10,
  page = 1,
  limit = 10
) {
  const db = await connectToDatabase();

  // Prepare the album query
  let albumQuery;
  if (typeof albumId === "string" && albumId === "root") {
    albumQuery = {};
  } else {
    albumQuery = { _id: new ObjectId(albumId) };
  }

  // Fetch the album
  const album = await db.collection("albums").findOne(albumQuery);
  if (!album) {
    throw new Error("Album not found");
  }

  // Calculate skip value for pagination
  const skip = (page - 1) * limit;

  // Fetch subalbums with pagination
  const subAlbums = await db
    .collection("albums")
    .find({ parent: album._id.toString() })
    .sort({ _id: -1 }) // Sort by ObjectId in descending order
    .skip(skip)
    .limit(limit)
    .toArray();

  // Count the total number of subalbums
  const totalSubAlbumsCount = await db
    .collection("albums")
    .find({ parent: album._id.toString() })
    .count();

  // Calculate the remaining albums count
  const remainingAlbumsCount = totalSubAlbumsCount - (skip + subAlbums.length);

  // Fetch images for the current album
  const imageIds = album.images
    ? album.images.map((id) => new ObjectId(id))
    : [];
  const images =
    imageIds.length > 0
      ? await db
          .collection("images")
          .find({ _id: { $in: imageIds } })
          .toArray()
      : [];

  // Check if the parent album is root
  let parentIsRoot = false;
  const rootId = await getRootId();
  if (album.parent) {
    parentIsRoot = album.parent ? rootId === album.parent.toString() : false;
  }

  // Calculate whether there are more subalbums available
  const hasMoreSubAlbums = remainingAlbumsCount > 0;

  // Combine the album data along with the flag indicating whether there are more subalbums
  const combinedData = {
    ...album,
    parentAlbumId: album.parent,
    parentIsRoot,
    images,
    sons: subAlbums,
    albumId: album._id,
    name: album.name,
    hasMoreSubAlbums: hasMoreSubAlbums,
  };
  return combinedData;
}

// Function to get random images
export async function getRandomImages(albumId, count) {
  const db = await connectToDatabase();
  const album = await db
    .collection("albums")
    .findOne({ _id: new ObjectId(albumId) });

  if (!album) {
    throw new Error("Album not found");
  }

  const imageIds = album.images.map((id) => new ObjectId(id));
  const images = await db
    .collection("images")
    .aggregate([
      { $match: { _id: { $in: imageIds } } },
      { $sample: { size: parseInt(count) } },
    ])
    .toArray();

  return images;
}

// Main handler function
export default async function handler(req, res) {
  const { albumId, randomImages, count, page } = req.query;

  try {
    if (randomImages) {
      const images = await getRandomImages(albumId, count);
      res.status(200).json(images);
    } else {
      const combinedData = await getAlbums(albumId, 10, parseInt(page));
      const responseData = {
        ...combinedData,
      };
      res.status(200).json(responseData);
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: error.message });
  }
}
