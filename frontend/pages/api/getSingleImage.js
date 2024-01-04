// pages/api/getSingleImage.js
import { connectToDatabase } from "./connectMongo";
import { ObjectId } from "mongodb";

export default async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).end(); // Method Not Allowed
  }

  const { id } = req.query;

  const db = await connectToDatabase();

  try {
    const objectId = new ObjectId(id);
    const image = await db.collection("images").findOne({ _id: objectId });

    if (!image) {
      return res.status(404).end(); // Not Found
    }

    return res.json(image);
  } catch (error) {
    console.error("Error fetching image:", error);
    return res.status(500).end(); // Internal Server Error
  }
}
