'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';

interface Movie {
  id: number;
  title: string;
  release_year: number;
  director: string;
  synopsis?: string;
}

interface List {
  list_id: number;
  list_name: string;
  is_empty: boolean;
}

const UserPageContent = () => {
  const [lists, setLists] = useState<List[]>([]);
  const [newListName, setNewListName] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<Movie[]>([]);
  const [selectedListId, setSelectedListId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const fetchUserLists = useCallback(async () => {
    const userId = Cookies.get('user_id');
    if (!userId) {
      setError('User ID not found');
      return;
    }

    try {
      const apiUrl = 'http://localhost:5001'; //process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/user/${userId}/lists`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });
      console.log('Fetched lists:', response.data);
      setLists(response.data || []);
    } catch (error: any) {
      console.error('Error fetching user lists', error);
      setError(error.response?.data?.message || 'Failed to fetch user lists.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = Cookies.get('token');
    if (!token) {
      router.push('/login');
    } else {
      fetchUserLists();
    }
  }, [router, fetchUserLists]);

  const handleSearch = useCallback(async (query: string) => {
    if (query.trim() === '') {
      setSearchResults([]);
      return;
    }

    try {
      const apiUrl = 'http://localhost:5001'; //process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/search_movies`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
        params: { query },
      });
      setSearchResults(response.data || []);
    } catch (error: any) {
      console.error('Error searching movies', error);
      setError(error.response?.data?.message || 'Failed to search movies.');
    }
  }, []);

  const handleCreateList = async () => {
    try {
      const apiUrl = 'http://localhost:5001'; //process.env.NEXT_PUBLIC_API_URL;
      await axios.post(
        `${apiUrl}/lists`,
        { name: newListName },
        {
          headers: {
            Authorization: `Bearer ${Cookies.get('token')}`,
          },
        }
      );
      setNewListName('');
      fetchUserLists(); // Re-fetch user lists after creating a new list
      alert('List created successfully');
    } catch (error: any) {
      console.error('Error creating list', error);
      setError(error.response?.data?.message || 'Failed to create list.');
    }
  };

  const handleAddMovieToList = async (movieId: number) => {
    if (selectedListId === null) {
      alert('Please select a list first');
      return;
    }

    try {
      const apiUrl = 'http://localhost:5001'; //process.env.NEXT_PUBLIC_API_URL;
      await axios.post(
        `${apiUrl}/list/${selectedListId}/add_movie`,
        { movie_id: movieId },
        {
          headers: {
            Authorization: `Bearer ${Cookies.get('token')}`,
          },
        }
      );
      fetchUserLists(); // Refresh the lists after adding a movie
      alert('Movie added to list');
      setSearchTerm('');
      setSearchResults([]);
    } catch (error: any) {
      console.error('Error adding movie to list', error);
      setError(error.response?.data?.message || 'Failed to add movie to list.');
    }
  };

  const handleMovieClick = (movieId: number) => {
    router.push(`/movies/${movieId}`);
  };

  const handleListClick = (listId: number) => {
    router.push(`/list/${listId}`);
  };

  const handleDeleteList = async (listId: number) => {
    try {
      const apiUrl = 'http://localhost:5001'; //process.env.NEXT_PUBLIC_API_URL;
      await axios.delete(`${apiUrl}/list/${listId}`, {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });
      fetchUserLists(); // Refresh the lists after deletion
      alert('List deleted successfully');
    } catch (error: any) {
      console.error('Error deleting list', error);
      setError(error.response?.data?.message || 'Failed to delete list.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <div className="p-4">
        {error && <p className="text-red-500">{error}</p>}
        <div className="mb-4">
          <input
            type="text"
            value={newListName}
            onChange={(e) => setNewListName(e.target.value)}
            className="p-2 border border-gray-300 rounded w-full md:w-1/2"
            placeholder="New list name"
          />
          <button onClick={handleCreateList} className="bg-green-500 text-white py-2 px-4 rounded ml-2 hover:bg-green-700">
            Create List
          </button>
        </div>
        <div className="mb-4">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              handleSearch(e.target.value);
            }}
            className="p-2 border border-gray-300 rounded w-full md:w-1/2"
            placeholder="Search movies"
          />
          {searchResults.length > 0 && (
            <ul className="border border-gray-300 rounded mt-2 max-h-60 overflow-y-auto bg-white p-2 space-y-2 shadow">
              {searchResults.map((movie) => (
                <li
                  key={movie.id}
                  className="p-2 hover:bg-gray-200 cursor-pointer rounded"
                  onClick={() => handleMovieClick(movie.id)}
                >
                  {movie.title} ({movie.release_year})
                </li>
              ))}
            </ul>
          )}
        </div>
        <div>
          <h2 className="text-xl font-bold mb-4">My Lists</h2>
          {loading ? (
            <p>Loading...</p>
          ) : lists.length > 0 ? (
            lists.map((list) => (
              <div key={list.list_id} className="mb-4 p-4 border border-gray-300 rounded bg-white shadow">
                <h3
                  className="text-lg font-bold cursor-pointer text-blue-500 hover:underline"
                  onClick={() => handleListClick(list.list_id)}
                >
                  {list.list_name}
                </h3>
                <button
                  onClick={() => handleDeleteList(list.list_id)}
                  className="bg-red-500 text-white py-1 px-3 rounded mt-2 hover:bg-red-700"
                >
                  Delete List
                </button>
                {list.is_empty ? (
                  <p className="mt-2">No movies in this list.</p>
                ) : (
                  <p className="mt-2">This list has movies.</p>
                )}
              </div>
            ))
          ) : (
            <p>No lists found.</p>
          )}
        </div>
      </div>
    </div>
  );
};

const UserPage = () => (
  <Suspense fallback={<div>Loading...</div>}>
    <UserPageContent />
  </Suspense>
);

export default UserPage;
