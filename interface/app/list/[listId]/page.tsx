"use client";

import { useRouter, useParams } from 'next/navigation';
import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';

interface Movie {
  id: number;
  title: string;
  release_year: number;
  director: string;
  synopsis?: string;
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
  const { listId } = useParams();

  const fetchListDetails = useCallback(async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/list/${listId}`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });
      setListDetails(response.data);
    } catch (err: any) {
      console.error('Error fetching list details:', err);
      setError(err.response?.data?.message || 'Failed to fetch list details');
    }
  }, [listId]);

  const fetchSimilarMovies = useCallback(async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/similar_movies_by_list/${listId}`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });
      setSimilarMovies(response.data.similar_movie_ids.map((id: number) => ({
        id,
        title: `Movie Title ${id}`,
        release_year: 2022,
      })));
    } catch (err: any) {
      console.error('Error fetching similar movies:', err);
      setError(err.response?.data?.message || 'Failed to fetch similar movies');
    }
  }, [listId]);

  useEffect(() => {
    if (listId) {
      fetchListDetails();
    }
  }, [listId, fetchListDetails]);

  const handleSimilarMovieClick = (movieId: number) => {
    router.push(`/movies/${movieId}`);
  };

  return (
    <div className="min-h-screen p-4">
      {error && <p className="text-red-500">{error}</p>}
      {listDetails ? (
        <>
          <h1 className="text-2xl mb-4">{listDetails.list_name}</h1>
          <ul>
            {listDetails.movies.map((movie) => (
              <li
                key={movie.id}
                className="cursor-pointer text-blue-500 hover:underline"
                onClick={() => router.push(`/movies/${movie.id}`)}
              >
                {movie.title} ({movie.release_year})
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
  );
};

export default ListPage;
