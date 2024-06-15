"use client";

import { useRouter, useParams } from 'next/navigation';
import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import Header from '@/components/Header';

interface Movie {
  id: number;
  title: string;
  release_year: number;
  director: string;
  synopsis?: string;
  note_moyenne?: number;
  note?: number;
  comment?: string;
}

interface ListDetails {
  list_name: string;
  movies: Movie[];
}

  const ListPage = () => {
    const [listDetails, setListDetails] = useState<ListDetails | null>(null);
    const [similarMovies, setSimilarMovies] = useState<Movie[]>([]);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();
    const { id } = useParams();  // Ensure we are using `id` as the parameter name.

    const fetchListDetails = useCallback(async () => {
    try {
      const apiUrl = 'http://localhost:5001'; //process.env.NEXT_PUBLIC_API_URL;
      const token = Cookies.get('token');
      if (!token) {
        throw new Error('No token found');
      }
      const response = await axios.get(`${apiUrl}/list/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Cache-Control': 'no-cache'
        },
      });

      const data = response.data;
      console.log("API Data:", data);

      const movies = data.movies.map((movie: any) => ({
        id: movie.id,
        title: movie.title,
        release_year: movie.release_date,
        director: movie.director,
        synopsis: movie.synopsis || '',
        note_moyenne: movie.note_moyenne || 0,
        note: movie.note || 0,
        comment: movie.comment || '',
      }));
      setListDetails({
        list_name: data.list_name || 'Unnamed List',
        movies: movies || [],
      });
    } catch (err: any) {
      console.error('Error fetching list details:', err);
      setError(err.response?.data?.message || 'Failed to fetch list details');
    }
  }, [id]);


  const fetchSimilarMovies = useCallback(async () => {
    if (!id) {
      setError('List ID is missing.');
      return;
    }
    try {
      const apiUrl = 'http://localhost:5001'; //process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/list/${id}/similar_movies`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });
      setSimilarMovies(response.data.similar_movies.map((movie: any) => ({
        id: movie.id,
        title: movie.title,
        release_year: movie.release_year,
        synopsis: movie.synopsis,
        note_moyenne: movie.note_moyenne,
      })));
    } catch (err: any) {
      console.error('Error fetching similar movies:', err);
      setError(err.response?.data?.message || 'Failed to fetch similar movies');
    }
  }, [id]);


  const removeMovieFromList = async (movieId: number) => {
    try {
      const apiUrl = 'http://localhost:5001'// process.env.NEXT_PUBLIC_API_URL;
      await axios.delete(`${apiUrl}/list/${id}/remove_movie`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
          'Cache-Control': 'no-cache'

        },
        data: { movie_id: movieId },
      });
      // Refresh list details after deletion
      fetchListDetails();
    } catch (err: any) {
      console.error('Error removing movie from list:', err);
      setError(err.response?.data?.message || 'Failed to remove movie from list');
    }
  };

  useEffect(() => {
    if (id) {
      fetchListDetails();
    }
  }, [id, fetchListDetails]);

  useEffect(() => {
    console.log("List Details:", listDetails);
  }, [listDetails]);


  const handleSimilarMovieClick = (movieId: number) => {
    router.push(`/movies/${movieId}`);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <div className="p-4">
        {error && <p className="text-red-500">{error}</p>}
        {listDetails ? (
          <>
            <h1 className="text-2xl font-bold mb-4 text-center">{listDetails.list_name}</h1>
            <ul className="space-y-2">
              {listDetails.movies.map((movie) => (
                <li key={movie.id} className="flex flex-col bg-white p-4 rounded shadow">
                  <div className="flex justify-between items-center">
                    <span className="cursor-pointer text-blue-500 hover:underline" onClick={() => router.push(`/movies/${movie.id}`)}>
                      {movie.title} ({movie.release_year})
                    </span>
                    <button
                      onClick={() => removeMovieFromList(movie.id)}
                      className="bg-red-500 text-white py-1 px-3 rounded hover:bg-red-700"
                    >
                      Remove
                    </button>
                  </div>
                  {movie.note !== undefined && movie.note !== null && (
                    <div className="mt-2">
                      <p>Rating: {movie.note}</p>
                      <p>Comment: {movie.comment}</p>
                    </div>
                  )}
                </li>
              ))}
            </ul>
            <button
              onClick={fetchSimilarMovies}
              className="bg-green-500 text-white py-2 px-4 rounded mt-4 hover:bg-green-700"
            >
              Suggest Similar Movies
            </button>
            {similarMovies.length > 0 && (
              <div className="mt-4">
                <h2 className="text-xl font-bold mb-2">Similar Movies</h2>
                <ul className="space-y-2 bg-white p-4 rounded shadow">
                  {similarMovies.map((similarMovie) => (
                    <li
                      key={similarMovie.id}
                      className="cursor-pointer hover:bg-gray-200 p-2 rounded"
                      onClick={() => handleSimilarMovieClick(similarMovie.id)}
                    >
                      {similarMovie.title} ({similarMovie.release_year})
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        ) : (
          <p>Loading...</p>
        )}
      </div>
    </div>
  );
};

export default ListPage;
