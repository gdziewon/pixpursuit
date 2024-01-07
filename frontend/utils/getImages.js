import { connectToDatabase } from "@/pages/api/connectMongo";

export async function getImages({ limit, page, query, sort }) {
  const db = await connectToDatabase();

  const skip = limit * (page - 1);
  const pipeline = [
    { $skip: skip },
    { $limit: limit },
    {
      $sort: {
        "metadata.DateTime": sort === "asc" ? 1 : -1,
      },
    },
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
}
