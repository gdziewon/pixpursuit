// pages/api/add-user-tag.js
import { connectToDatabase } from "./connectMongo";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).end(); // Method Not Allowed
  }

  try {
    const { inserted_id, tags } = req.body;

    const db = await connectToDatabase();

    const result = await db.collection("images").updateOne(
      { _id: inserted_id },
      {
        $push: { user_tags: { $each: tags } },
      }
    );

    if (result.modifiedCount === 1) {
      return res
        .status(200)
        .json({ message: "Tag added successfully", updatedImage: result });
    } else {
      return res.status(500).json({ message: "Failed to add tag" });
    }
  } catch (error) {
    console.error("Error adding tag:", error);
    return res.status(500).json({ message: "Failed to add tag" });
  }
}
