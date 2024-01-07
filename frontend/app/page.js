import { connectToDatabase } from "@/pages/api/connectMongo";
import RandomImage from "@/app/components/RandomImage";

export default async function Home() {
  await connectToDatabase();

  return (
    <main className="container mx-auto p-4">
      <RandomImage />
    </main>
  );
}
