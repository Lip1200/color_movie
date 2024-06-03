import { useRouter } from 'next/router';
import React, { useState } from 'react';
import axios from 'axios';

const AddMovieForm = () => {
  const router = useRouter();
  const { id, list_id } = router.query;
  const [note, setNote] = useState<number | null>(null);
  const [comment, setComment] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (note === null) {
      setError('Please provide a rating.');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `http://localhost:5001/list/${list_id}/add_movie`,
        { movie_id: id, note, comment },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      router.push(`/list/${list_id}`);
    } catch (err) {
      setError('Error adding movie to Lists');
      console.error(err);
    }
  };

  return (
    <div>
      <h1>Add Movie to List</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Rating:</label>
          <input
            type="number"
            value={note ?? ''}
            onChange={(e) => setNote(Number(e.target.value))}
            required
            min="0"
            max="10"
          />
        </div>
        <div>
          <label>Comment:</label>
          <textarea value={comment} onChange={(e) => setComment(e.target.value)} />
        </div>
        <button type="submit" className="bg-green-500 text-white p-2 rounded">
          Submit
        </button>
        {error && <p className="text-red-500">{error}</p>}
      </form>
    </div>
  );
};

export default AddMovieForm;
