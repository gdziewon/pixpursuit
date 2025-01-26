process.env.DO_SPACE_ENDPOINT
import { connectToDatabase } from "./connectMongo";

export default async function handler(req, res) {
  let { limit, page, query, sort, searchMode } = req.query;

  if (typeof searchMode === "undefined") {
    searchMode = "OR";
  }

  try {
    const db = await connectToDatabase();

    const skip = Number(limit) * (page - 1);
    const pipeline = [
      {
        $sort: {
          ...(sort === "desc"
            ? { "metadata.DateTime": -1, _id: -1 }
            : sort === "mostPopular"
            ? { views: -1 }
            : sort === "leastPopular"
            ? { views: 1 }
            : sort === "asc"
            ? { "metadata.DateTime": 1, _id: 1 }
            : {}),
        },
      },
      { $skip: skip },
      { $limit: Number(limit) },
    ];

    if (query && query !== "undefined") {
      const searchWords = query.split(" ");

      try {
        let searchCompound;

        switch (searchMode) {
          case "OR":
            searchCompound = {
              should: searchWords.map((word) => ({
                text: {
                  query: word,
                  fuzzy: {
                    maxEdits: 1,
                    prefixLength: 3,
                    maxExpansions: 50,
                  },
                  path: {
                    wildcard: "*",
                  },
                },
              })),
            };
            break;
          case "AND":
            searchCompound = {
              must: searchWords.map((word) => ({
                text: {
                  query: word,
                  fuzzy: {
                    maxEdits: 1,
                    prefixLength: 3,
                    maxExpansions: 50,
                  },
                  path: {
                    wildcard: "*",
                  },
                },
              })),
            };
            break;
          case "NOR":
            searchCompound = {
              mustNot: searchWords.map((word) => ({
                text: {
                  query: word,
                  fuzzy: {
                    maxEdits: 1,
                    prefixLength: 3,
                    maxExpansions: 50,
                  },
                  path: {
                    wildcard: "*",
                  },
                },
              })),
            };
            break;
        }

        pipeline.unshift({
          $search: {
            index: env.process.ATLAS_SEARCH_INDEX,
            compound: searchCompound,
          },
        });
      } catch (error) {
        console.error("Error adding $search stage:", error);
        throw error;
      }
    }

    const images = await db.collection("images").aggregate(pipeline).toArray();

    res.status(200).json(images);
  } catch (error) {
    res.status(500).json({ error: error.toString() });
  }
}
