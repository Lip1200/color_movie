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
  casting: string[];
  synopsis?: string;
  note_moyenne?: number;
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
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/list/${id}`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });
      setListDetails({
        list_name: response.data.list_name,
        movies: response.data.Movie.map((movie: any) => ({
          id: movie.id,
          title: movie.title,
          release_year: movie.release_date,
          director: movie.director,
          synopsis: movie.synopsis,
          casting: movie.casting,
          note_moyenne: movie.note_moyenne,
        })),
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
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
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
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      await axios.delete(`${apiUrl}/list/${id}/remove_movie`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
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

  const handleSimilarMovieClick = (movieId: number) => {
    router.push(`/movies/${movieId}`);
  };

  return (
    <div className="min-h-screen">
      <Header />
      <div className="p-4">
        {error && <p className="text-red-500">{error}</p>}
        {listDetails ? (
          <>
            <h1 className="text-2xl mb-4">{listDetails.list_name}</h1>
            <ul>
              {listDetails.movies.map((movie) => (
                <li key={movie.id} className="flex justify-between items-center mb-2">
                  <span className="cursor-pointer text-blue-500 hover:underline" onClick={() => router.push(`/movies/${movie.id}`)}>
                    {movie.title} ({movie.release_year})
                  </span>
                  <button
                    onClick={() => removeMovieFromList(movie.id)}
                    className="bg-red-500 text-white p-1 rounded ml-2"
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
            <button
              onClick={fetchSimilarMovies}
              className="bg-green-500 text-white p-2 rounded mt-4"
            >
              Suggest Similar Movies
            </button>
            {similarMovies.length > 0 && (
              <div className="mt-4">
                <h2 className="text-xl mb-2">Similar Movies</h2>
                <ul className="border p-2 mt-2">
                  {similarMovies.map((similarMovie) => (
                    <li
                      key={similarMovie.id}
                      className="cursor-pointer mb-2 hover:bg-gray-200"
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
