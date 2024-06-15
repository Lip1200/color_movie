"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Cookies from 'js-cookie';
import Link from 'next/link';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (event: React.FormEvent) => {
  event.preventDefault();
  setError('');

  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    console.log('API URL:', apiUrl); // Log API URL
    const response = await axios.post(
      `${apiUrl}/login`,
      { email, password },
      {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    console.log('Response:', response); // Log Response

    if (response.status === 200) {
      Cookies.set('token', response.data.token, { expires: 1 }); // Expires in 1 day
      Cookies.set('user_id', response.data.user_id, { expires: 1 }); // Expires in 1 day
      router.push('/user');
    } else {
      setError('Login failed. Please check your credentials.');
    }
  } catch (err: any) {
    console.error('Error:', err); // Log Error
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
        <h1 className="login-title mb-6 text-center">Login</h1>
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
              className="btn-primary"
            >
              Login
            </button>
            <Link href="/register">
              <a className="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800">
                Register here
              </a>
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
