"use client";

import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header'; // Adjust the path if necessary

interface Movie {
  id: number;
  title: string;
  release_year: number;
  director: string;
  synopsis?: string;
}

const Dashboard = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<Movie[]>([]);
  const [userName, setUserName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const fetchUserName = useCallback(async () => {
    try {
      const user_id = Cookies.get('user_id');
      if (!user_id) {
        setError('Failed to fetch user ID');
        return;
      }

      const token = Cookies.get('token');
      if (!token) {
        setError('Failed to fetch token');
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL;

      let res = await axios({
        url: `${apiUrl}/user/${user_id}/details`,
        method: 'get',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        timeout: 8000,
      });

      if (res.status === 200) {
        setUserName(res.data.user_name);
      } else {
        setError('Failed to fetch user details');
      }

      return res.data;
    } catch (err) {
      console.error('Error fetching user name', err);
      setError('Failed to fetch user name');
    }
  }, []);

  useEffect(() => {
    const token = Cookies.get('token');
    if (!token) {
      router.push('/login');
    } else {
      fetchUserName();
    }
  }, [fetchUserName, router]);

  const handleSearch = useCallback(async () => {
    if (searchTerm.trim() === '') {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/search_movies`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
          'Cache-Control': 'no-cache',
        },
        params: { query: searchTerm },
      });
      setSearchResults(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching search results:', err);
      setError('Failed to fetch search results');
    } finally {
      setLoading(false);
    }
  }, [searchTerm]);

  useEffect(() => {
    handleSearch();
  }, [searchTerm, handleSearch]);

  const handleMovieClick = (movieId: number) => {
    router.push(`/movies/${movieId}`);
  };

  const handleUserClick = () => {
    router.push('/user');
  };

  const handleLogout = () => {
    Cookies.remove('token');
    Cookies.remove('user_id');
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <div className="p-4">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <div className="flex items-center">
            <button onClick={handleUserClick} className="text-blue-500 underline mr-4">
              {userName}
            </button>
            <button onClick={handleLogout} className="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-700">
              Logout
            </button>
          </div>
        </div>
        <div className="mb-4">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="p-2 border border-gray-300 rounded w-full"
            placeholder="Search movies"
          />
          {loading && <p className="text-gray-500">Loading...</p>}
          {error && <p className="text-red-500">{error}</p>}
          {searchResults.length > 0 && (
            <ul className="border p-2 mt-2 rounded shadow bg-white space-y-2">
              {searchResults.map((movie) => (
                <li
                  key={movie.id}
                  onClick={() => handleMovieClick(movie.id)}
                  className="cursor-pointer p-2 hover:bg-gray-200 rounded"
                >
                  {movie.title} ({movie.release_year})
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
