// pages/api/random-images.js
import { connectToDatabase } from "@/pages/api/connectMongo";

export default async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).end();
  }

  try {
    const db = await connectToDatabase();

    const randomImage = await db
      .collection("images")
      .aggregate([{ $sample: { size: 1 } }])
      .toArray();

    if (randomImage.length > 0) {
      return res.status(200).json(randomImage[0]);
    } else {
      return res.status(404).json({ error: "No random image found" });
    }
  } catch (error) {
    console.error("Error fetching random image:", error);
    return res.status(500).json({ error: "Failed to fetch random image" });
  }
}
