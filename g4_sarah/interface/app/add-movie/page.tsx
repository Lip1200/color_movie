"use client";

import { useRouter, useSearchParams } from 'next/navigation';
import React, { useState, useEffect, Suspense } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import Image from 'next/image';

const AddMovieForm = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const id = searchParams.get('id');
  const list_id = searchParams.get('list_id');
  const [note, setNote] = useState<number | null>(null);
  const [comment, setComment] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!id || !list_id) {
      setError('Movie ID or List ID is missing.');
    }
  }, [id, list_id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (note === null) {
      setError('Please provide a rating.');
      return;
    }

    setLoading(true);
    try {
      const token = Cookies.get('token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      console.log(`Posting to ${apiUrl}/list/${list_id}/add_movie with movie_id: ${id}, note: ${note}, comment: ${comment}`);
      const response = await axios.post(
        `${apiUrl}/list/${list_id}/add_movie`,
        { movie_id: id, note, comment },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 201) {
        router.push(`/list/${list_id}`);
      } else {
        setError('Failed to add movie to the list.');
      }
    } catch (err: any) {
      console.error('Error adding movie to list:', err);
      setError(err.response?.data?.message || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };
    const handleBackToHome = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen p-4">
      <h1 className="text-2xl mb-4">Add Movie to List</h1>
        <div onClick={handleBackToHome} className="cursor-pointer">
          <Image
            src="/public/logo.png"
            alt="Back to Home"
            width={50}
            height={50}
          />
        </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="note" className="block text-sm font-medium text-gray-700">
            Rating:
          </label>
          <input
            id="note"
            name="note"
            type="number"
            value={note ?? ''}
            onChange={(e) => setNote(Number(e.target.value))}
            required
            min="0"
            max="10"
            className="mt-1 p-2 block w-full border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label htmlFor="comment" className="block text-sm font-medium text-gray-700">
            Comment:
          </label>
          <textarea
            id="comment"
            name="comment"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            className="mt-1 p-2 block w-full border border-gray-300 rounded-md"
          />
        </div>
        <button type="submit" className="bg-green-500 text-white p-2 rounded" disabled={loading || !id || !list_id}>
          {loading ? 'Submitting...' : 'Submit'}
        </button>
        {error && <p className="text-red-500">{error}</p>}
      </form>
    </div>
  );
};

const AddMoviePage = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AddMovieForm />
    </Suspense>
  );
};

export default AddMoviePage;
