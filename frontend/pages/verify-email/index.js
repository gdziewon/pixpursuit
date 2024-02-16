"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';

export default function VerifyEmail() {
    const router = useRouter();
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState('');

    useEffect(() => {
        // Ensure the router is ready
        if (!router.isReady) return;

        const token = router.query.token;

        if (!token) {
            setMessage('No verification token provided.');
            setLoading(false);
            return;
        }

        const verifyEmail = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/verify-email?token=${token}`);
                setMessage(response.data.message);
            } catch (error) {
                setMessage(error.response?.data?.detail || 'An error occurred during email verification.');
            } finally {
                setLoading(false);
            }
        };

        verifyEmail();
    }, [router, router.isReady]);

    return (
        <div>
            {loading ? (
                <p>Verifying your email...</p>
            ) : (
                <p>{message}</p>
            )}
        </div>
    );
}
