"use client";

import { useRouter, useSearchParams } from 'next/navigation';
import React, { useState } from 'react';
import axios, { AxiosError } from 'axios';
import Cookies from 'js-cookie';

const AddMovieForm = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const id = searchParams.get('id');
  const list_id = searchParams.get('list_id');
  const [note, setNote] = useState<number | null>(null);
  const [comment, setComment] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

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
      await axios.post(
        `${apiUrl}/list/${list_id}/add_movie`,
        { movie_id: id, note, comment },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      router.push(`/list/${list_id}`);
    } catch (err: any) {
      if (err.response) {
        setError('Error adding movie to the list');
      } else {
        setError('An error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Add Movie to List</h1>
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
        <button type="submit" className="bg-green-500 text-white p-2 rounded" disabled={loading}>
          {loading ? 'Submitting...' : 'Submit'}
        </button>
        {error && <p className="text-red-500">{error}</p>}
      </form>
    </div>
  );
};

export default AddMovieForm;
