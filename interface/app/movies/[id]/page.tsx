"use client";

import { useRouter, useParams } from 'next/navigation';
import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import Header from '@/components/Header'; // Ajuster le chemin si nécessaire

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
  const [similarMovies, setSimilarMovies] = useState<{ id: number; titre: string; annee: number; }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { id } = useParams();

  const fetchMovie = useCallback(async () => {
    try {
      const apiUrl = 'http://localhost:5001'; //process.env.NEXT_PUBLIC_API_URL;
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
      const apiUrl = 'http://localhost:5001'; //process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/user_lists`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });
      setLists(response.data || []); // Default to an empty array if data is null
    } catch (err: any) {
      console.error('Error fetching user lists:', err);
      setError(err.response?.data?.message || 'Failed to fetch user lists');
    }
  }, []);

  const fetchSimilarMovies = useCallback(async () => {
    try {
      const apiUrl = 'http://localhost:5001'; //process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/similar_movies/${id}`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });

      setSimilarMovies(response.data.similar_movies.map((movie: any) => ({
        id: movie.id,
        titre: movie.title,
        annee: movie.release_year,
      })));
    } catch (err: any) {
      console.error('Error fetching similar movies:', err);
      setError(err.response?.data?.message || 'Failed to fetch similar movies');
    }
  }, [id]);

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

    router.push(`/add-movie?id=${id}&list_id=${selectedList}`);
  };

  const handleSuggestSimilar = () => {
    fetchSimilarMovies();
  };

  const handleSimilarMovieClick = (movieId: number) => {
    router.push(`/movies/${movieId}`);
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
            {lists.length > 0 ? (
              lists.map((list) => (
                <option key={list.id} value={list.id}>{list.nom_liste}</option>
              ))
            ) : (
              <option disabled>No lists found</option>
            )}
          </select>
          <div className="flex mt-4 space-x-2">
            <button onClick={handleAddToList} className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-700">
              Add to List
            </button>
            <button onClick={handleSuggestSimilar} className="bg-green-500 text-white py-2 px-4 rounded hover:bg-green-700">
              Suggest Similar Movies
            </button>
          </div>
        </div>
        {similarMovies.length > 0 && (
          <div className="mt-4">
            <h2 className="text-xl font-bold mb-2">Similar Movies</h2>
            <ul className="border p-2 mt-2 rounded shadow bg-white space-y-2">
              {similarMovies.map((similarMovie) => (
                <li key={similarMovie.id} className="cursor-pointer p-2 hover:bg-gray-200 rounded" onClick={() => handleSimilarMovieClick(similarMovie.id)}>
                  {similarMovie.titre} ({similarMovie.annee})
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default MoviePage;
