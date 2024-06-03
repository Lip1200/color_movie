import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useRouter } from 'next/router';

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
  const router = useRouter();

  useEffect(() => {
    const token = Cookies.get('token');
    if (!token) {
      router.push('/login');
    } else {
      fetchUserName();
    }
  }, [router]);

  const fetchUserName = async () => {
    try {
      const response = await axios.get('http://localhost:5001/user/details', {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });
      setUserName(response.data.name);
    } catch (error) {
      console.error('Error fetching user name', error);
    }
  };

  const handleSearch = useCallback(async () => {
    if (searchTerm) {
      try {
        const response = await axios.get('http://localhost:5001/search_movies', {
          headers: {
            Authorization: `Bearer ${Cookies.get('token')}`,
            'Cache-Control': 'no-cache',
          },
          params: { query: searchTerm },
        });
        setSearchResults(response.data);
      } catch (err) {
        console.error('Error fetching search results:', err);
      }
    } else {
      setSearchResults([]);
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
    router.push('/login');
  };

  return (
    <div className="min-h-screen p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl">Dashboard</h1>
        <div className="flex items-center">
          <button onClick={handleUserClick} className="text-blue-500 underline mr-4">
            {userName}
          </button>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white p-2 rounded"
          >
            Logout
          </button>
        </div>
      </div>
      <div className="mb-4">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="p-2 border border-gray-300 rounded"
          placeholder="Search movies"
        />
        {searchResults.length > 0 && (
          <ul className="border p-2 mt-2">
            {searchResults.map((movie) => (
              <li
                key={movie.id}
                onClick={() => handleMovieClick(movie.id)}
                className="cursor-pointer mb-2 hover:bg-gray-200"
              >
                {movie.title} ({movie.release_year})
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
