import { connectToDatabase } from "./connectMongo";

export default async function handler(req, res) {
    const { limit, page, query, sort } = req.query;

    try {
        const db = await connectToDatabase();

        const skip = Number(limit) * (page - 1);
        const pipeline = [
            {
                $sort: {
                    ...(sort === "desc" ? { "metadata.DateTime": -1, "_id": -1 } :
                        sort === "mostPopular" ? { views: -1 } :
                            sort === "leastPopular" ? { views: 1 } :
                                sort === "asc" ? { "metadata.DateTime": 1, "_id": 1 } : {}),
                },
            },
            { $skip: skip },
            { $limit: Number(limit) },
        ];


        if (query  && query !== 'undefined') {
            try {
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
            } catch (error) {
                console.error('Error adding $search stage:', error);
                throw error;
            }
        }


        const images = await db.collection("images").aggregate(pipeline).toArray();

        res.status(200).json(images);

    } catch (error) {
        res.status(500).json({ error: error.toString() });
    }
}