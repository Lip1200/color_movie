"use client";

import { useRouter, useParams } from 'next/navigation';
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import Header from '@/components/Header';

interface Movie {
  id: number;
  titre: string;
  annee: number;
  type: string;
  synopsis?: string;
  note_moyenne?: number;
}

interface List {
  id: number;
  nom_liste: string;
}

const MoviePage = () => {
  const [movie, setMovie] = useState<Movie | null>(null);
  const [lists, setLists] = useState<List[]>([]);
  const [selectedList, setSelectedList] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { id } = useParams();

  const fetchMovie = useCallback(async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/movies/${id}`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });
      setMovie(response.data);
    } catch (err: any) {
      console.error('Error fetching movie:', err);
      setError(err.response?.data?.message || 'Failed to fetch movie details');
    }
  }, [id]);

  const fetchUserLists = useCallback(async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/user_lists`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });
      setLists(response.data || []);
    } catch (err: any) {
      console.error('Error fetching user lists:', err);
      setError(err.response?.data?.message || 'Failed to fetch user lists');
    }
  }, []);

  useEffect(() => {
    if (id) {
      fetchMovie();
    }
  }, [id, fetchMovie]);

  useEffect(() => {
    fetchUserLists();
  }, [fetchUserLists]);

  const handleAddToList = () => {
    if (selectedList === null) {
      setError('Please select a list.');
      return;
    }

    console.log(`Navigating to /add-movie?id=${id}&list_id=${selectedList}`);
    router.push(`/add-movie?id=${id}&list_id=${selectedList}`);
  };

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  if (!movie) {
    return <p>Loading...</p>;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">{movie.titre}</h1>
        <p><strong>Year:</strong> {movie.annee}</p>
        <p><strong>Type:</strong> {movie.type}</p>
        {movie.synopsis && <p><strong>Synopsis:</strong> {movie.synopsis}</p>}
        {movie.note_moyenne && <p><strong>Average Rating:</strong> {movie.note_moyenne}</p>}
        <div className="mt-4">
          <select
            value={selectedList ?? ''}
            onChange={(e) => setSelectedList(Number(e.target.value))}
            className="p-2 border border-gray-300 rounded w-full md:w-1/2 lg:w-1/3"
          >
            <option value="" disabled>Select a list to add this movie</option>
            {lists.map((list) => (
              <option key={list.id} value={list.id}>{list.nom_liste}</option>
            ))}
          </select>
          <div className="flex mt-4 space-x-2">
            <button onClick={handleAddToList} className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-700">
              Add to List
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MoviePage;
