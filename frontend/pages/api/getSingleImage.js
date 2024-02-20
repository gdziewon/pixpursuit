// pages/api/getSingleImage.js
import { connectToDatabase } from "./connectMongo";
import { ObjectId } from "mongodb";

export default async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).end();
  }

  const { id } = req.query;

  if (!id) {
    return res.status(400).json({ message: "Missing id in query parameters" });
  }

  const db = await connectToDatabase();

  let objectId;
  try {
    objectId = new ObjectId(id);
  } catch (error) {
    return res.status(400).json({ message: "Invalid id format" });
  }

  try {
    const image = await db.collection("images").findOne({ _id: objectId });

    if (!image) {
      return res.status(404).end();
    }

    return res.json(image);
  } catch (error) {
    console.error("Error fetching image:", error);
    return res.status(500).json({ message: `Server error: ${error.message}` });
  }
}