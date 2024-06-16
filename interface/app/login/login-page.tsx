"use client";

import { useRouter } from 'next/navigation';
import React, {Suspense, useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { Metadata } from 'next';
import Link from 'next/link';
import Header from '@/components/Header';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null); // Reset error message

    if (!email || !password) {
      setError('Please provide all required information.');
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      console.log(apiUrl);
      const response = await axios.post(`${apiUrl}/login`, { email, password });

      if (response.status === 200) {
        Cookies.set('token', response.data.token, { expires: 1 }); // Expires in 1 day
        Cookies.set('user_id', response.data.user_id, { expires: 1 }); // Expires in 1 day
        router.push('/user');
      } else {
        setError('Login failed. Please check your credentials.');
      }
    } catch (err: any) {
      console.error('Error:', err); // Log the error for debugging
      if (err.response) {
        setError('Login failed. Please check your credentials.');
      } else if (err.request) {
        setError('No response from the server. Please try again later.');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Login</h1>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          <div className="flex items-center justify-between">
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              Login
            </button>
            <Link href="/register" className="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800">
                Register here
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

const LoginPageWrapper: React.FC = () => {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <LoginPage />
    </React.Suspense>
  );
};

export default LoginPageWrapper;
