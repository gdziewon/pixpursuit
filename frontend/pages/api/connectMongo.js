import { MongoClient } from "mongodb";

const MONGODB_URI = process.env.MONGODB_URI;
let client = null;
let db = null;

export async function connectToDatabase() {
  if (db) {
    return db;
  }

  if (!MONGODB_URI) {
    throw new Error("MONGODB_URI env variable not set");
  }

  try {
    if (!client) {
      client = await MongoClient.connect(MONGODB_URI);
    }
    db = client.db("pixpursuit_db");
    return db;
  } catch (error) {
    console.error("Error connecting to MongoDB:", error);
    throw error;
  }
}
