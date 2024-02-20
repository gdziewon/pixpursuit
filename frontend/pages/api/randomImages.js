// pages/api/random-images.js
import { connectToDatabase } from "@/pages/api/connectMongo";

export default async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).end();
  }

  try {
    const db = await connectToDatabase();
    if (!db) {
      console.error("Error connecting to database");
      return res.status(500).json({ error: "Failed to connect to database" });
    }

    let randomImage;
    try {
      randomImage = await db
          .collection("images")
          .aggregate([{ $sample: { size: 1 } }])
          .toArray();
    } catch (error) {
      console.error("Error fetching random image:", error);
      return res.status(500).json({ error: "Failed to fetch random image" });
    }

    if (randomImage.length > 0) {
      return res.status(200).json(randomImage[0]);
    } else {
      return res.status(404).json({ error: "No random image found" });
    }
  } catch (error) {
    console.error("Unexpected error:", error);
    return res.status(500).json({ error: "Unexpected error occurred" });
  }
}
