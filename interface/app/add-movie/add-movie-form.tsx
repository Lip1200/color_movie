'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import React, { useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import Header from '@/components/Header';

const AddMovieForm: React.FC = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const id = searchParams.get('id');
  const list_id = searchParams.get('list_id');
  const [note, setNote] = useState<number | null>(null);
  const [comment, setComment] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (note === null || id === null || list_id === null) {
      setError('Please provide all required information.');
      return;
    }

    const payload = { movie_id: id, note, comment };
    console.log('Sending data:', payload);

    try {
      const token = Cookies.get('token');
      if (!token) {
        setError('No token found. Please login.');
        return;
      }
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (!apiUrl) {
        setError('API URL is not defined.');
        return;
      }
      const response = await axios.post(
        `${apiUrl}/list/${list_id}/add_movie`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
          },
        }
      );

      console.log('Response:', response);
      router.push(`/list/${list_id}`);
    } catch (err: any) {
      setError('Error adding movie to list');
      console.error('Error response:', err.response?.data || err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Add Movie to List</h1>
        <form onSubmit={handleSubmit}>
          <div>
            <label>Rating:</label>
            <input
              type="number"
              value={note ?? ''}
              onChange={(e) => setNote(Number(e.target.value))}
              required
              min="0"
              max="10"
              className="p-2 border border-gray-300 rounded w-full"
            />
          </div>
          <div>
            <label>Comment:</label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="p-2 border border-gray-300 rounded w-full"
            />
          </div>
          <button type="submit" className="bg-green-500 text-white p-2 rounded mt-4">
            Submit
          </button>
          {error && <p className="text-red-500">{error}</p>}
        </form>
      </div>
    </div>
  );
};

export default AddMovieForm;