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

interface List {
  list_id: number;
  list_name: string;
  movies: Movie[];
}

const UserPage = () => {
  const [lists, setLists] = useState<List[]>([]);
  const [newListName, setNewListName] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<Movie[]>([]);
  const [selectedListId, setSelectedListId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchUserLists = useCallback(async () => {
    try {
      const response = await axios.get('http://localhost:5001/user_lists', {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      });
      setLists(response.data);
    } catch (error) {
      console.error('Error fetching user lists', error);
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

  const handleSearch = async (query: string) => {
    if (query.trim() === '') {
      setSearchResults([]);
      return;
    }

    try {
      const response = await axios.get('http://localhost:5001/search_movies', {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
        params: { query },
      });
      setSearchResults(response.data);
    } catch (error) {
      console.error('Error searching Movie', error);
    }
  };

  const handleCreateList = async () => {
    try {
      const response = await axios.post(
        'http://localhost:5001/lists',
        { name: newListName },
        {
          headers: {
            Authorization: `Bearer ${Cookies.get('token')}`,
          },
        }
      );
      setNewListName('');
      fetchUserLists(); // Refresh the lists after creating a new one
      alert('Lists created successfully');
    } catch (error) {
      console.error('Error creating Lists', error);
    }
  };

  const handleAddMovieToList = async (movieId: number) => {
    if (selectedListId === null) {
      alert('Please select a Lists first');
      return;
    }

    try {
      await axios.post(
        `http://localhost:5001/list/${selectedListId}/add_movie`,
        { movie_id: movieId },
        {
          headers: {
            Authorization: `Bearer ${Cookies.get('token')}`,
          },
        }
      );
      fetchUserLists(); // Refresh the lists after adding a movie
      alert('Movie added to Lists');
      setSearchTerm('');
      setSearchResults([]);
    } catch (error) {
      console.error('Error adding movie to Lists', error);
    }
  };

  const handleMovieClick = (movieId: number) => {
    router.push(`/movies/${movieId}`);
  };

  return (
    <div className="min-h-screen p-4">
      <h1 className="text-2xl mb-4">User Dashboard</h1>
      <div className="mb-4">
        <input
          type="text"
          value={newListName}
          onChange={(e) => setNewListName(e.target.value)}
          className="p-2 border border-gray-300 rounded"
          placeholder="New list name"
        />
        <button onClick={handleCreateList} className="bg-green-500 text-white p-2 rounded ml-2">
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
          className="p-2 border border-gray-300 rounded"
          placeholder="Search movies"
        />
        {searchResults.length > 0 && (
          <ul className="border border-gray-300 rounded mt-2 max-h-60 overflow-y-auto">
            {searchResults.map((movie) => (
              <li
                key={movie.id}
                className="p-2 hover:bg-gray-200 cursor-pointer"
                onClick={() => handleMovieClick(movie.id)}
              >
                {movie.title} ({movie.release_year})
              </li>
            ))}
          </ul>
        )}
      </div>
      <div>
        <h2 className="text-xl mb-4">My Lists</h2>
        {loading ? (
          <p>Loading...</p>
        ) : lists.length > 0 ? (
          lists.map((list) => (
            <div key={list.list_id} className="mb-4 p-4 border border-gray-300 rounded">
              <h3 className="text-lg font-bold">{list.list_name}</h3>
              <ul>
                {list.movies.length > 0 ? (
                  list.movies.map((movie) => (
                    <li key={movie.id} className="flex justify-between items-center">
                      {movie.title} ({movie.release_year})
                    </li>
                  ))
                ) : (
                  <p>No movies in this list.</p>
                )}
              </ul>
            </div>
          ))
        ) : (
          <p>No lists found.</p>
        )}
      </div>
    </div>
  );
};

export default UserPage;
