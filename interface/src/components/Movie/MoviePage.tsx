import { GetServerSideProps } from 'next';
import { useRouter } from 'next/router';
import React, { useEffect, useState } from 'react';
import axios from 'axios';

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

export interface MoviePageProps {
  movie: Movie;
}

const MoviePage: React.FC<MoviePageProps> = ({ movie }) => {
  const [lists, setLists] = useState<List[]>([]);
  const [selectedList, setSelectedList] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchUserLists = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:5001/user_lists', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setLists(response.data);
      } catch (err) {
        console.error('Error fetching user lists:', err);
      }
    };

    fetchUserLists();
  }, []);

  const handleAddToList = () => {
    if (selectedList === null) {
      setError('Please select a list.');
      return;
    }

    router.push(`/add-movie/${movie.id}?list_id=${selectedList}`);
  };

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
          {lists.map((list) => (
            <option key={list.id} value={list.id}>{list.nom_liste}</option>
          ))}
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
