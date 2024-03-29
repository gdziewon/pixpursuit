import { connectToDatabase } from "@/pages/api/connectMongo";

export default async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).end();
  }

  try {
    const { query } = req.query;
    const db = await connectToDatabase();

    const regexQuery = { $regex: `.*${query}.*`, $options: "i" };
    const arrayFieldsToSearch = [
      "auto_tags",
      "user_tags",
      "user_faces",
      "backlog_faces",
    ];
    const simpleFieldsToSearch = ["description", "added_by", "album_name"];

    const arrayMatchConditions = arrayFieldsToSearch.map((field) => ({
      [field]: { $elemMatch: regexQuery },
    }));
    const simpleMatchConditions = simpleFieldsToSearch.map((field) => ({
      [field]: regexQuery,
    }));

    const pipeline = [
      { $match: { $or: [...arrayMatchConditions, ...simpleMatchConditions] } },
      {
        $project: {
          suggestions: {
            $concatArrays: [
              ["$description", "$added_by", "$album_name"],
              "$auto_tags",
              "$user_tags",
              "$user_faces",
              "$backlog_faces",
            ],
          },
        },
      },
      { $unwind: "$suggestions" },
      { $match: { suggestions: regexQuery } },
      { $group: { _id: null, suggestions: { $addToSet: "$suggestions" } } },
      { $project: { suggestions: { $slice: ["$suggestions", 10] } } },
    ];

    const result = await db.collection("images").aggregate(pipeline).toArray();

    if (result.length > 0) {
      const suggestions = result[0].suggestions.filter((suggestion) =>
        suggestion.toLowerCase().includes(query.toLowerCase())
      );
      return res.status(200).json(suggestions);
    } else {
      return res.status(200).json([]);
    }
  } catch (error) {
    console.error("Error fetching search suggestions:", error);
    return res
      .status(500)
      .json({ error: "Failed to fetch search suggestions" });
  }
}
