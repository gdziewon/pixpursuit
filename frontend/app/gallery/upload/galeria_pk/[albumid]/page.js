"use client"

import React, { useState } from 'react';
import axios from 'axios';
import { useSession } from 'next-auth/react';

export default function GaleriaPKUploadPage({params}) {
    const [url, setUrl] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const { data: session } = useSession();
    const albumId = params.albumid;

    const handleUpload = async (e) => {
        e.preventDefault();

        try {
            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/scrape-images`, {
                url: url,
                album_id: albumId.toString()
            }, {
                headers: {
                    'Authorization': `Bearer ${session.accessToken}`
                }
            });

            if (response.status === 200) {
                alert('Images scraped successfully');
            } else {
                alert('Failed to scrape images');
            }
        } catch (error) {
            setErrorMessage('Error scraping images: ' + error.message);
        }
    };

    return (
        <div className="container mx-auto max-w-md mx-auto shadow-md overflow-hidden md:max-w-2xl">
            <div className="p-8 bg-white">
                <div className="mt-5 md:mt-0 md:col-span-2">
                    <form>
                        <div className="shadow sm:rounded-md sm:overflow-hidden">
                            <div className="px-4 py-5 bg-white sm:p-6">
                                <div className="grid grid-cols-6 gap-6">
                                    <div className="col-span-6 sm:col-span-4">
                                        <label htmlFor="url" className="block text-sm font-medium text-gray-700">Enter albums URL:</label>
                                        <input type="text" name="url" id="url" style={{ color: 'black' }} value={url} onChange={(e) => setUrl(e.target.value)} className="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md" placeholder="Enter URL" />
                                    </div>
                                </div>
                                {errorMessage && <p className="text-red-500">{errorMessage}</p>}
                            </div>
                            <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
                                <button type="button" onClick={handleUpload}
                                        className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                    Upload
                                </button>

                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}