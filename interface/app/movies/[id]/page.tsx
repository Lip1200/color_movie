"use client";

import { useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState, useCallback } from 'react';
import axios, {AxiosError} from 'axios';

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
  const searchParams = useSearchParams();
  const id = searchParams.get('id');

  const fetchMovie = useCallback(async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/movies/${id}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
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
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setLists(response.data || []); // Default to an empty array if data is null
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

  const handleAddToList = async () => {
    if (selectedList === null) {
      setError('Please select a list.');
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      await axios.post(
        `${apiUrl}/list/${selectedList}/add_movie`,
        { movie_id: id },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      alert('Movie added to list');
    } catch (err: any) {
      console.error('Error adding movie to list:', err);
      setError(err.response?.data?.message || 'Failed to add movie to list.');
    }
  };

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  if (!movie) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>{movie.titre}</h1>
      <p><strong>Year:</strong> {movie.annee}</p>
      <p><strong>Type:</strong> {movie.type}</p>
      {movie.synopsis && <p><strong>Synopsis:</strong> {movie.synopsis}</p>}
      {movie.note_moyenne && <p><strong>Average Rating:</strong> {movie.note_moyenne}</p>}
      <div>
        <select value={selectedList ?? ''} onChange={(e) => setSelectedList(Number(e.target.value))}>
          <option value="" disabled>Select a list</option>
          {lists.length > 0 ? (
            lists.map((list) => (
              <option key={list.id} value={list.id}>{list.nom_liste}</option>
            ))
          ) : (
            <option disabled>No lists found</option>
          )}
        </select>
        <button onClick={handleAddToList} className="bg-blue-500 text-white p-2 rounded ml-2">
          Add to List
        </button>
        {error && <p className="text-red-500">{error}</p>}
      </div>
    </div>
  );
};

export default MoviePage;
