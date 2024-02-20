"use client"

import React, { useState } from 'react';

const TagModal = ({ isOpen, onSubmit, onCancel, tagInput, handleTagInputChange }) => {
    const [error, setError] = useState(null);

    try {
        if (!isOpen) {
            return null;
        }

        return (
            <div className="fixed z-10 inset-0 overflow-y-auto">
                <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                    <div className="fixed inset-0 transition-opacity" aria-hidden="true">
                        <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
                    </div>
                    <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                    <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                        <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                            <div className="sm:flex sm:items-start">
                                <div className="mt-3 text-center sm:mt-0 sm:text-left">
                                    <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                                        Tags to add:
                                    </h3>
                                    <div className="mt-2">
                                        <input
                                            value={tagInput}
                                            onChange={handleTagInputChange}
                                            type="text"
                                            style={{width: '400px'}}
                                            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block sm:text-sm border-gray-300 rounded-md text-black text-lg"
                                            placeholder="Enter tags, separated by commas"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                            <button type="button"
                                    className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm" onClick={onSubmit}>
                                Accept
                            </button>
                            <button type="button" className="mt-3 w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:mt-0 sm:w-auto sm:text-sm" onClick={onCancel}>
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    } catch (err) {
        setError(err.message);
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return null;
};

export default TagModal;