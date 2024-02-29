import React, { useEffect, useState } from 'react';
import '@/styles/design_styles.css';

const SuccessWindow = ({ message }) => {
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
        }, 5000);

        return () => {
            clearTimeout(fadeInTimer);
            clearTimeout(fadeOutTimer);
            clearTimeout(clearMessageTimer);
        };
    }, [message]);

    return displayMessage ? (
        <div className={`success-window ${fadeIn ? 'fade-in' : ''} ${fadeOut ? 'fade-out' : ''}`}>
            {displayMessage}
        </div>
    ) : null;
};

export default SuccessWindow;