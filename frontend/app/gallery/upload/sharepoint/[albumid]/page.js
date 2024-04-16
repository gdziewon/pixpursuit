"use client"

import React, { useState } from 'react';
import axios from 'axios';
import { useSession } from 'next-auth/react';
import SuccessWindow from '@/utils/SuccessWindow';
import ErrorWindow from '@/utils/ErrorWindow';

/**
 * SharepointUploadPage component.
 *
 * @param {Object} params - The parameters.
 * @returns {JSX.Element} - The rendered JSX element.
 */
export default function SharepointUploadPage({params}) {
    const [url, setUrl] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [width, setWidth] = useState('');
    const [height, setHeight] = useState('');
    const [errorMessage, setErrorMessage] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);
    const { data: session } = useSession();
    const albumId = params.albumid;

    /**
     * Handles the upload of images.
     *
     * @param {Object} e - The event object.
     * @returns {Promise<void>}
     */
    const handleUpload = async (e) => {
        e.preventDefault();

        const data = {
            sharepoint_url: url,
            sharepoint_username: username,
            sharepoint_password: password,
            parent_id: albumId.toString()
        };

        if (width && height) {
            data.size = [Number(width), Number(height)];
        }

        try {
            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/sharepoint-upload`, data, {
                headers: {
                    'Authorization': `Bearer ${session.accessToken}`
                }
            });

            if (response.status === 200) {
                setSuccessMessage('Upload started successfully');
            } else {
                setErrorMessage('Failed to start upload');
            }
        } catch (error) {
            console.error('Error starting upload:', error.response && error.response.data && error.response.data.message ? error.response.data.message : error);
            setErrorMessage('Failed to start upload');
        }
    };

    /**
     * Handles the cancel action.
     *
     * @returns {void}
     */
    const handleCancel = () => {
        window.history.back();
    };

    /**
     * Renders the SharepointUploadPage component.
     *
     * @returns {JSX.Element} - The rendered JSX element.
     */
    return (
        <div className="container mx-auto max-w-md shadow-md overflow-hidden md:max-w-2xl rounded-lg">
            <div className="p-6 bg-gray-800">
                <div className="mt-5 md:mt-0 md:col-span-2">
                    <form>
                        <div className="shadow sm:rounded-md  sm:overflow-hidden">
                            <div className="px-4 py-4 bg-gray-800 sm:p-4">
                                <div className="grid grid-cols-6 gap-6">
                                    <div className="col-span-6 sm:col-span-4">
                                        <label htmlFor="url" className="block text-sm font-medium text-white"
                                               style={{fontSize: '17px'}}>Enter Sharepoint album URL:</label>
                                        <input type="text" name="url" id="url" style={{
                                            color: 'white',
                                            border: '1px solid white',
                                            width: '580px',
                                            height: '60px',
                                            padding: '14px',
                                            marginBottom: '20px'
                                        }} value={url} onChange={(e) => setUrl(e.target.value)}
                                               className="mt-3 block w-full bg-gray-800 shadow-sm sm:text-sm border-white rounded-md"
                                               placeholder="Enter URL"/>
                                        <label htmlFor="username" className="block text-sm font-medium text-white"
                                               style={{fontSize: '17px'}}>Enter Sharepoint username:</label>
                                        <input type="text" name="username" id="username" style={{
                                            color: 'white',
                                            border: '1px solid white',
                                            width: '580px',
                                            height: '60px',
                                            padding: '14px',
                                            marginBottom: '20px'
                                        }} value={username} onChange={(e) => setUsername(e.target.value)}
                                               className="mt-3 block w-full bg-gray-800 shadow-sm sm:text-sm border-white rounded-md"
                                               placeholder="Enter username"/>
                                        <label htmlFor="password" className="block text-sm font-medium text-white"
                                               style={{fontSize: '17px'}}>Enter Sharepoint password:</label>
                                        <input type="password" name="password" id="password" style={{
                                            color: 'white',
                                            border: '1px solid white',
                                            width: '580px',
                                            height: '60px',
                                            padding: '14px',
                                            marginBottom: '20px'
                                        }} value={password} onChange={(e) => setPassword(e.target.value)}
                                               className="mt-3 block w-full bg-gray-800 shadow-sm sm:text-sm border-white rounded-md"
                                               placeholder="Enter password"/>
                                        <div className="flex space-x-4">
                                            <div>
                                                <label htmlFor="width" className="block text-sm font-medium text-white"
                                                       style={{fontSize: '17px'}}>Enter width:</label>
                                                <input type="number" name="width" id="width" style={{
                                                    color: 'white',
                                                    border: '1px solid white',
                                                    width: '280px',
                                                    height: '60px',
                                                    padding: '14px',
                                                    marginBottom: '16px',
                                                    appearance: 'none'
                                                }} value={width} onChange={(e) => setWidth(e.target.value)}
                                                       className="mt-3 block w-full bg-gray-800 shadow-sm sm:text-sm border-white rounded-md"
                                                       placeholder="Enter width"/>
                                            </div>
                                            <div>
                                                <label htmlFor="height" className="block text-sm font-medium text-white"
                                                       style={{fontSize: '17px'}}>Enter height:</label>
                                                <input type="number" name="height" id="height" style={{
                                                    color: 'white',
                                                    border: '1px solid white',
                                                    width: '280px',
                                                    height: '60px',
                                                    padding: '14px',
                                                    marginBottom: '16px',
                                                    appearance: 'none'
                                                }} value={height} onChange={(e) => setHeight(e.target.value)}
                                                       className="mt-3 block w-full bg-gray-800 shadow-sm sm:text-sm border-white rounded-md"
                                                       placeholder="Enter height"/>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="bg-gray-800 px-4 py-1 sm:px-6 sm:flex button-container">
                                <button type="button" onClick={handleCancel}
                                        className="mt-3 w-auto inline-flex rounded-full shadow-sm px-4 py-1.5 bg-white text-sm font-medium text-gray-800 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:text-sm mr-2 ml-4">
                                    Cancel
                                </button>
                                <button type="button" onClick={handleUpload}
                                        className="mt-3 w-auto inline-flex rounded-full shadow-sm px-4 py-1.5 accept-button text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:text-sm mr-2 ml-4">
                                    Upload
                                </button>
                            </div>
                        </div>
                    </form>
                    {errorMessage && <ErrorWindow message={errorMessage} clearMessage={() => setErrorMessage(null)}/>}
                    {successMessage &&
                        <SuccessWindow message={successMessage} clearMessage={() => setSuccessMessage(null)}/>}
                </div>
            </div>
        </div>
    );
}