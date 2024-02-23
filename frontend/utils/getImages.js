import { connectToDatabase } from "@/pages/api/connectMongo";

export async function getImages({ limit, page, query, sort }) {
  try{
    const db = await connectToDatabase();

    const skip = limit * (page - 1);
    const pipeline = [
      {
        $sort: {
          ...(sort === "desc" ? { "metadata.DateTime": -1 } :
              sort === "mostPopular" ? { views: -1 } :
                  sort === "leastPopular" ? { views: 1 } :
                      sort === "asc" ? { "metadata.DateTime": 1 } : {}),
        },
      },
      { $skip: skip },
      { $limit: limit },
    ];

    if (query) {
      pipeline.unshift({
        $search: {
          index: "pixiep",
          text: {
            query,
            fuzzy: {
              maxEdits: 1,
              prefixLength: 3,
              maxExpansions: 50,
            },
            path: {
              wildcard: "*",
            },
          },
        },
      });
    }

    const images = await db.collection("images").aggregate(pipeline).toArray();

    return images;
  } catch (error) {
    console.error(`Error occurred while fetching images: ${error.message}`);
    throw error;
  }
}
