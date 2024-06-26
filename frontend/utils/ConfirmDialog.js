"use client";

import React, { useState } from 'react';
import '@/styles/design_styles.css';

/**
 * Renders a confirmation dialog.
 *
 * @param {Object} props - The props.
 * @param {boolean} props.isOpen - Whether the dialog is open.
 * @param {Function} props.onConfirm - The function to call when the confirm button is clicked.
 * @param {Function} props.onCancel - The function to call when the cancel button is clicked.
 * @returns {JSX.Element|null} - The rendered JSX element, or null if the dialog is not open.
 */
const ConfirmDialog = ({ isOpen, onConfirm, onCancel }) => {
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
                    <span className="hidden sm:inline-block sm:align-middle sm:h-screen"
                          aria-hidden="true">&#8203;</span>
                    <div
                        className="inline-block align-bottom bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                        <div className="bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                            <div className="sm:flex sm:items-start">
                                <div className="mt-3 text-center sm:mt-0 sm:text-center" style={{marginTop: '10px'}}>
                                    <h3 className="text-lg text-white leading-6 font-medium  text-center"
                                        id="modal-title">
                                        Are you sure you want to delete the selected items?
                                    </h3>
                                </div>
                            </div>
                        </div>
                        <div className="bg-gray-800 px-4 py-3 sm:px-6 sm:flex button-container"  style={{marginBottom: '10px', marginTop: '15px'}}>
                            <button type="button"
                                    className="mt-3 w-auto inline-flex rounded-full shadow-sm px-4 py-1.5 bg-white text-sm font-medium text-gray-800 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:text-sm mr-2 ml-4"
                                    onClick={onCancel}>
                                Cancel
                            </button>
                            <button type="button"
                                    className="mt-3 w-auto inline-flex rounded-full shadow-sm px-4 py-1.5 delete-button text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:text-sm mr-2 ml-4"
                                    onClick={onConfirm}>
                                Delete
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
};

export default ConfirmDialog;