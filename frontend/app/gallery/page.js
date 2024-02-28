"use client";

import { Suspense } from "react";
import Image from "next/legacy/image";
import Link from "next/link";
import Loading from "@/app/loading";
import Searcher from "@/app/components/Searcher";
import { getImages } from "@/utils/getImages";
import clsx from "clsx";
import {
  ChevronUpIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/solid";
import { useEffect, useState } from "react";

export default function Gallery({ searchParams }) {
    let page = parseInt(searchParams.page, 10) || (typeof window !== 'undefined' ? parseInt(localStorage.getItem('page'), 10) : null) || 1;
    let limit = parseInt(searchParams.limit, 10) || 12;
    let search = searchParams.search || undefined;
    let dropdown = searchParams.dropdown || "hidden";
    let sort = searchParams.sort || (typeof window !== 'undefined' ? localStorage.getItem('sort') : null) || "desc";

    // Save sort option to local storage
    if (typeof window !== 'undefined') {
        localStorage.setItem('sort', sort);
        localStorage.setItem('page', page.toString());
    }

    const [images, setImages] = useState([]);

    useEffect(() => {
        const fetchImages = async () => {
            try {
                const fetchedImages = await getImages({ limit, page, query: search, sort });
                setImages(fetchedImages);
            } catch (error) {
                console.error(error);
            }
        };

        fetchImages();
    }, [limit, page, search, sort]);

    const renderDropdownMenu = () => {
        if (dropdown === "visible") {
            return (
                <div className="absolute right-0 mt-2 w-40 rounded-md shadow-lg bg-gray-300 ring-1 ring-black ring-opacity-5 z-50">
                    <div className="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
                        <Link
                            href={{
                                pathname: "/gallery",
                                query: {
                                    ...(search ? { search } : {}),
                                    page,
                                    sort: "desc",
                                    dropdown: "hidden",
                                },
                            }}
                            className={`block px-4 py-2 text-xs ${sort === "desc" ? "text-black font-bold" : "text-gray-700"} hover:bg-gray-100`}
                            role="menuitem"
                        >
                            Newest
                        </Link>
                        <Link
                            href={{
                                pathname: "/gallery",
                                query: {
                                    ...(search ? { search } : {}),
                                    page,
                                    sort: "asc",
                                    dropdown: "hidden",
                                },
                            }}
                            className={`block px-4 py-2 text-xs ${sort === "asc" ? "text-black font-bold" : "text-gray-700"} hover:bg-gray-100`}
                            role="menuitem"
                        >
                            Oldest
                        </Link>
                        <Link
                            href={{
                                pathname: "/gallery",
                                query: {
                                    ...(search ? { search } : {}),
                                    page,
                                    sort: "mostPopular",
                                    dropdown: "hidden",
                                },
                            }}
                            className={`block px-4 py-2 text-xs ${sort === "mostPopular" ? "text-black font-bold" : "text-gray-700"} hover:bg-gray-100`}
                            role="menuitem"
                        >
                            Most Popular
                        </Link>
                        <Link
                            href={{
                                pathname: "/gallery",
                                query: {
                                    ...(search ? { search } : {}),
                                    page,
                                    sort: "leastPopular",
                                    dropdown: "hidden",
                                },
                            }}
                            className={`block px-4 py-2 text-xs ${sort === "leastPopular" ? "text-black font-bold" : "text-gray-700"} hover:bg-gray-100`}
                            role="menuitem"
                        >
                            Least Popular
                        </Link>
                    </div>
                </div>
            );
        }
    };

    return (
        <section className="py-24">
            <div className="container">
            <div className="mb-12 flex items-center justify-between gap-x-16">
          <h1 className="text-3xl font-bold">PixPursuit</h1>
          <Searcher search={search}/>
          <div className="flex space-x-6">
            <Link
                href={{
                  pathname: "/gallery",
                  query: {
                    ...(search ? {search} : {}),
                    page: page > 1 ? page - 1 : 1,
                      sort: sort,
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
                    ...(search ? {search} : {}),
                    page: page + 1,
                      sort: sort,
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
            <div className="relative">
                <Link
                    href={{
                        pathname: "/gallery",
                        query: {
                            ...(search ? {search} : {}),
                            page,
                            sort,
                            dropdown: dropdown === "visible" ? "hidden" : "visible",
                        },
                    }}
                    className="rounded border bg-gray-300 px-3 py-1 text-xs text-black flex items-center space-x-2"
                >
                    <span>Sort by </span>
                    {dropdown === "visible" ? <ChevronUpIcon className="w-4 h-4"/> :
                        <ChevronDownIcon className="w-4 h-4"/>}
                </Link>
                {renderDropdownMenu()}
            </div>
        </div>
            <Suspense fallback={<Loading/>}>
                <div className="grid grid-cols-4 gap-8">
                    {Array.isArray(images) && images.map((image, index) => (
                        <Suspense fallback={<Loading/>} key={index}>
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
                                <div
                                    className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition duration-500 ease-in-out">
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
