import { connectToDatabase } from "@/pages/api/connectMongo";
import { ObjectId } from "mongodb";

export async function getSingleImage(id) {
  const db = await connectToDatabase();

  try {
    const objectId = new ObjectId(id);

    const image = await db.collection("images").findOne({ _id: objectId });

    return image;
  } catch (error) {
    console.error("Error fetching image:", error);
    return null;
  }
}
