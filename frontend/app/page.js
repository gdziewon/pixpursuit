import { connectToDatabase } from "@/pages/api/connectMongo";

export default function Home() {
    connectToDatabase();

    return (
        <main className="container mx-auto p-4">
            <h1 className="text-4xl font-bold mb-4">Welcome to Home Page</h1>
            <p className="text-lg mb-8">
                Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aperiam asperiores atque autem consequatur
            </p>
            <section className="mb-8">
                <h2 className="text-2xl font-bold mb-4">Features</h2>
                <ul className="list-disc pl-4">
                    <li>Responsive design</li>
                    <li>Easy to customize</li>
                    <li>Fast loading times</li>
                </ul>
            </section>
        </main>
    )
}

