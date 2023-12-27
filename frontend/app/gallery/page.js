import { Suspense } from "react";
import { connectToDatabase } from "@/pages/api/connectMongo";
import Image from "next/image";
import Link from "next/link";

async function getImages(perPage, page) {
  const db = await connectToDatabase();
  const images = await db
    .collection("images")
    .find({})
    .skip(perPage * (page - 1))
    .limit(perPage)
    .toArray();
  const imageCount = await db.collection("images").countDocuments({});
  const response = { images, imageCount };
  return response;
}

export default async function Gallery({ searchParams }) {
  let page = parseInt(searchParams.page, 10);
  page = !page || page < 1 ? 1 : page;
  let perPage = 12;

  const data = await getImages(perPage, page);

  // pagination
  const totalPages = Math.ceil(data.imageCount / perPage);
  const prevPage = page - 1 > 0 ? page - 1 : 1;
  const nextPage = page + 1;

  const pageNumber = [];
  const offsetNumber = 1;
  for (
    let i = page - offsetNumber;
    i <= page + offsetNumber && i <= totalPages;
    i++
  ) {
    if (i >= 1 && i <= totalPages && totalPages > 1) {
      pageNumber.push(i);
    }
  }

  return (
    <main>
      <Suspense fallback={<div>Loading...</div>}>
        <div className="grid grid-cols-4 gap-4">
          {data.images.map((image) => (
            <Suspense fallback={<div>Loading...</div>} key={image._id}>
              <div
                className="relative overflow-hidden rounded group cursor-pointer"
                style={{
                  aspectRatio: "1/1",
                }}
              >
                <Image
                  src={image.thumbnail_url}
                  alt={image.description}
                  layout="fill"
                  objectFit="cover"
                  objectPosition="center"
                  className="rounded transition-transform group-hover:scale-105"
                />
                <div
                  className="absolute inset-0 flex items-center justify-center text-white p-4 opacity-0 transition-opacity group-hover:opacity-100"
                  style={{
                    backgroundColor: "rgba(0, 0, 0, 0.7)",
                  }}
                >
                  <p className="text-center">{image.description}</p>
                </div>
              </div>
            </Suspense>
          ))}
        </div>
      </Suspense>
      <div className="flex justify-center mt-8 items-center">
        <div className="flex gap-4 p-4">
          {page === 1 ? (
            <div
              className="opacity-60 px-4 py-2 text-white "
              aria-disabled="true"
            >
              Previous
            </div>
          ) : (
            <Link
              href={`?page=${prevPage}`}
              aria-label="Previous Page"
              className="px-4 py-2 text-white rounded hover:bg-green-500"
            >
              Previous
            </Link>
          )}
          <div className="flex flex-row ">
            {pageNumber.map((number) => (
              <div className="px-2 py-2">
                <Link
                  href={`?page=${number}`}
                  key={number}
                  className={`px-4 py-2 rounded-full hover:bg-green-500 ${
                    page === number ? "border-light-green border-[2px]" : ""
                  }`}
                >
                  {number}
                </Link>
              </div>
            ))}
          </div>
          {page === totalPages ? (
            <div
              className="opacity-60 px-4 py-2 text-white"
              aria-disabled="true"
            >
              Next
            </div>
          ) : (
            <Link
              href={`?page=${nextPage}`}
              aria-label="Next Page"
              className="px-4 py-2 text-white rounded hover:bg-green-500"
            >
              Next
            </Link>
          )}
        </div>
      </div>
    </main>
  );
}
