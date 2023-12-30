import { Suspense } from "react";
import Image from "next/legacy/image";
import Link from "next/link";
import Loading from "@/app/loading";
import Searcher from "@/app/components/Searcher";

import { getImages } from "@/utils/getImages";
import clsx from "clsx";

export default async function Gallery({ searchParams }) {
  let page = parseInt(searchParams.page, 10) || 1;
  let limit = parseInt(searchParams.limit, 10) || 12;
  let search = searchParams.search || undefined;

  const images = await getImages({ limit, page, query: search });

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
                "rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800",
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
                "rounded border bg-gray-100 px-3 py-1 text-sm text-gray-800",
                images.length < limit && "pointer-events-none opacity-50"
              )}
            >
              Next
            </Link>
          </div>
        </div>

        <Suspense fallback={<Loading />}>
          <div className="grid grid-cols-4 gap-8">
            {images.map((image, index) => (
              <Suspense fallback={<Loading />} key={index}>
                <Link
                  href={`/gallery/${image.id}`}
                  className="rounded-md overflow-hidden"
                >
                  <Image
                    src={image.thumbnail_url}
                    alt={image.description}
                    width={300}
                    height={300}
                    layout="responsive"
                  />
                </Link>
              </Suspense>
            ))}
          </div>
        </Suspense>
      </div>
    </section>
  );
}
