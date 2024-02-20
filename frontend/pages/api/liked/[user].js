import { connectToDatabase } from "@/pages/api/connectMongo";
import { ObjectId } from 'mongodb';

export default async function handler(req, res) {
    const { user } = req.query;

    try {
        const db = await connectToDatabase();
        const collection = db.collection("users");
        const userData = await collection.findOne({ username: user });

        if (!userData) {
            res.status(404).json({ message: "User not found" });
            return;
        }

        const imageCollection = db.collection("images");
        const likedImages = await imageCollection.find({ _id: { $in: userData.liked.map(id => new ObjectId(id)) } }).toArray();

        res.status(200).json(likedImages);
    } catch (error) {
        console.error(error);
        if (error instanceof TypeError) {
            res.status(400).json({ message: "Bad Request" });
        } else if (error instanceof RangeError) {
            res.status(416).json({ message: "Requested Range Not Satisfiable" });
        } else {
            res.status(500).json({ message: "Internal Server Error" });
        }
    }
}