// pages/api/search-suggestions.js
import { connectToDatabase } from "@/pages/api/connectMongo";

export default async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).end();
  }

  try {
    const { query } = req.query;

    const db = await connectToDatabase();

    const pipeline = [
      {
        $match: {
          $or: [
            { description: { $regex: query, $options: "i" } },
            { added_by: { $regex: query, $options: "i" } },
            { auto_tags: { $regex: query, $options: "i" } },
          ],
        },
      },
      {
        $group: {
          _id: null,
          suggestions: {
            $addToSet: "$description",
          },
        },
      },
    ];

    const result = await db.collection("images").aggregate(pipeline).toArray();

    if (result.length > 0) {
      const suggestions = result[0].suggestions;
      return res.status(200).json(suggestions);
    } else {
      return res.status(200).json([]); // No suggestions found
    }
  } catch (error) {
    console.error("Error fetching search suggestions:", error);
    return res
      .status(500)
      .json({ error: "Failed to fetch search suggestions" });
  }
}
