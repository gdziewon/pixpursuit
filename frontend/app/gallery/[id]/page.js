import { getSingleImage } from "@/utils/getSingleImage";
import Image from "next/image";
export default async function ImagePage({ params }) {
  const id = params.id;

  const image = await getSingleImage(id);

  return (
    <main className="flex flex-col items-center justify-center p-6">
      <div className="">
        <div className="flex justify-center">
          <Image
            src={image.image_url}
            alt={image.description}
            width={800}
            height={800}
            quality={100}
          />
        </div>
        <div className="mt-4">
          <h1 className="text-center text-2xl font-bold text-gray-900 dark:text-white">
            {image.description}
          </h1>
          <ul>
            {image &&
              Array.isArray(image.detected_objects) &&
              image.detected_objects.map((object, index) => (
                <li key={index}>name: {object.name}</li>
              ))}
          </ul>
        </div>
      </div>
    </main>
  );
}
