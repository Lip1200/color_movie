"use client";
import './globals.css';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';

const HomePage = () => {
    const router = useRouter();

    useEffect(() => {
        const token = Cookies.get('token');
        if (token) {
            router.push('/dashboard');
        } else {
            router.push('/login');
        }
    }, [router]);

    return null;
};

export default HomePage;
