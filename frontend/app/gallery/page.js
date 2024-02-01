import { Suspense } from "react";
import Image from "next/legacy/image";
import Link from "next/link";
import Loading from "@/app/loading";
import Searcher from "@/app/components/Searcher";
import { getImages } from "@/utils/getImages";
import clsx from "clsx";
import {
  CloudArrowUpIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/solid";

export default async function Gallery({ searchParams }) {
  let page = parseInt(searchParams.page, 10) || 1;
  let limit = parseInt(searchParams.limit, 10) || 12;
  let search = searchParams.search || undefined;
  let sort = searchParams.sort || "asc";

  const images = await getImages({ limit, page, query: search, sort });

  return (
    <section className="py-24">
      <div className="container">
        <div className="mb-12 flex items-center justify-between gap-x-16">
          <h1 className="text-3xl font-bold">PixPursuit</h1>
          <Searcher search={search} />
          <div className="flex space-x-6">
            <Link
              href={{
                pathname: "/gallery",
                query: {
                  ...(search ? { search } : {}),
                  page: page > 1 ? page - 1 : 1,
                },
              }}
              className={clsx(
                "rounded border bg-gray-100 px-4 py-2 text-sm text-gray-800",
                page <= 1 && "pointer-events-none opacity-50"
              )}
            >
              Previous
            </Link>
            <Link
              href={{
                pathname: "/gallery",
                query: {
                  ...(search ? { search } : {}),
                  page: page + 1,
                },
              }}
              className={clsx(
                "rounded border bg-gray-100 px-4 py-2 text-sm text-gray-800",
                images.length < limit && "pointer-events-none opacity-50"
              )}
            >
              Next
            </Link>
          </div>
        </div>
        <div className="mb-12 flex justify-end space-x-6">
          <Link href="/gallery/upload/zip">
            <button
                type="button"
                className="rounded border bg-blue-500 px-3 py-1 text-xs text-white"
            >
              Upload Zip{" "}
              <CloudArrowUpIcon className="inline-block w-4 h-4" />
            </button>
          </Link>
          <Link href="/gallery/upload">
            <h2 className="rounded border bg-blue-500 px-3 py-1 text-xs text-white">
              Upload Images{" "}
              <CloudArrowUpIcon className="inline-block w-4 h-4" />
            </h2>
          </Link>
          <Link
            href={{
              pathname: "/gallery",
              query: {
                ...(search ? { search } : {}),
                page,
                sort: sort === "asc" ? "desc" : "asc",
              },
            }}
            className="rounded border bg-gray-300 px-3 py-1 text-xs text-black"
          >
            Sort by date{" "}
            {sort === "asc" ? (
              <ChevronDownIcon className="inline-block w-4 h-4" />
            ) : (
              <ChevronUpIcon className="inline-block w-4 h-4" />
            )}
          </Link>
        </div>
        <Suspense fallback={<Loading />}>
          <div className="grid grid-cols-4 gap-8">
            {images.map((image, index) => (
              <Suspense fallback={<Loading />} key={index}>
                <Link
                  href={`/gallery/${image._id.toString()}`}
                  className="relative rounded-md overflow-hidden group"
                >
                  <Image
                    src={image.thumbnail_url}
                    alt={image.description}
                    width={300}
                    height={300}
                    layout={"responsive"}
                    className="transition duration-500 ease-in-out transform hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition duration-500 ease-in-out">
                    <p className="text-white text-center">
                      {image.description}
                    </p>
                  </div>
                </Link>
              </Suspense>
            ))}
          </div>
        </Suspense>
      </div>
    </section>
  );
}
