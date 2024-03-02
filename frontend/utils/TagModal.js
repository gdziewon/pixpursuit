"use client"

import React, { useState } from 'react';
import '@/styles/design_styles.css';

const TagModal = ({ isOpen, onSubmit, onCancel, tagInput, handleTagInputChange }) => {
    const [error, setError] = useState(null);

    try {
        if (!isOpen) {
            return null;
        }

        return (
            <div className="fixed z-10 inset-0 overflow-y-auto flex items-center justify-center">
                <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                    <div className="fixed inset-0 transition-opacity" aria-hidden="true">
                        <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
                    </div>
                    <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                    <div className="inline-block align-bottom bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                        <div className="bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                            <div className="sm:flex sm:items-start">
                                <div className="mt-3 text-left sm:mt-0 sm:text-left">
                                    <h3 className="text-lg leading-6 font-medium text-white" id="modal-title">
                                        Tags to add:
                                    </h3>
                                    <div className="mt-2">
                                        <input
                                            value={tagInput}
                                            onChange={handleTagInputChange}
                                            type="text"
                                            style={{width: '400px', padding: '10px', borderBottom: '1px solid white'}}
                                            className="shadow-sm block sm:text-sm  text-whtie text-lg bg-gray-800 no-border-on-focus"
                                            placeholder="Enter tags, separated by commas"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="bg-gray-800 px-4 py-3 sm:px-6 sm:flex button-container">
                            <button type="button"
                                    className="mt-3 w-auto inline-flex rounded-full shadow-sm px-4 py-1.5 bg-white text-sm font-medium text-gray-800 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:text-sm mr-2 ml-4"
                                    onClick={onCancel}>
                                Cancel
                            </button>
                            <button type="button"
                                    className="mt-3 w-auto inline-flex rounded-full shadow-sm px-4 py-1.5 accept-button text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:text-sm mr-2 ml-4"
                                    onClick={onSubmit}>
                                Accept
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