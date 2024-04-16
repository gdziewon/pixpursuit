import { connectToDatabase } from "@/pages/api/connectMongo";
import RandomImage from "@/app/components/RandomImage";

/**
 * Home page component.
 *
 * @returns {JSX.Element} - The rendered JSX element.
 */
export default async function Home() {
    try {
        /**
         * Connects to the database.
         */
        await connectToDatabase();
    } catch (error) {
        console.error("Failed to connect to the database", error);
    }

    /**
     * Renders the RandomImage component.
     */
  return (
    <main className="container mx-auto p-4">
      <RandomImage />
    </main>
  );
}
