import { connectToDatabase } from "@/pages/api/connectMongo";
import RandomImage from "@/app/components/RandomImage";

export default async function Home() {
    try {
        await connectToDatabase();
    } catch (error) {
        console.error("Failed to connect to the database", error);
    }

  return (
    <main className="container mx-auto p-4">
      <RandomImage />
    </main>
  );
}
