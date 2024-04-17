import React, { useEffect, useState } from 'react';
import '@/styles/design_styles.css';

/**
 * Renders an error window with a fade in and fade out effect.
 *
 * @param {Object} props - The props.
 * @param {string} props.message - The error message to display.
 * @param {Function} props.clearMessage - The function to clear the error message.
 * @returns {JSX.Element|null} - The rendered JSX element, or null if there is no error message.
 */
const ErrorWindow = ({ message, clearMessage }) => {
    const [displayMessage, setDisplayMessage] = useState(message);
    const [fadeOut, setFadeOut] = useState(false);
    const [fadeIn, setFadeIn] = useState(false);

    useEffect(() => {
        setDisplayMessage(message);
        setFadeOut(false);
        setFadeIn(true);

        const fadeInTimer = setTimeout(() => {
            setFadeIn(false);
        }, 5000);

        const fadeOutTimer = setTimeout(() => {
            setFadeOut(true);
        }, 5000);

        const clearMessageTimer = setTimeout(() => {
            setDisplayMessage(null);
            clearMessage();
        }, 5000);

        return () => {
            clearTimeout(fadeInTimer);
            clearTimeout(fadeOutTimer);
            clearTimeout(clearMessageTimer);
        };
    }, [message, clearMessage]);

    return displayMessage ? (
        <div className={`error-window ${fadeIn ? 'fade-in' : ''} ${fadeOut ? 'fade-out' : ''}`}>
            {displayMessage}
        </div>
    ) : null;
};

export default ErrorWindow;