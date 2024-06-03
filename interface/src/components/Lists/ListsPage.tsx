"use client";

import { useRouter } from 'next/navigation';
import React, { useState, useEffect, useCallback } from 'react';
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

interface UserList {
  list_id: number;
  list_name: string;
}

const ListsPage = () => {
  const router = useRouter();
  const [userLists, setUserLists] = useState<UserList[]>([]);
  const [newListName, setNewListName] = useState('');
  const [error, setError] = useState<string | null>(null);

  const fetchUserLists = useCallback(async () => {
    try {
      const token = Cookies.get('token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.get(`${apiUrl}/user_lists`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setUserLists(response.data);
    } catch (err) {
      console.error('Error fetching user lists:', err);
    }
  }, []);

  useEffect(() => {
    fetchUserLists();
  }, [fetchUserLists]);

  const handleCreateList = async () => {
    if (!newListName) {
      setError('Please provide a List name.');
      return;
    }

    try {
      const token = Cookies.get('token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await axios.post(`${apiUrl}/lists`, { name: newListName }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setNewListName('');
      setUserLists([...userLists, response.data.list]);
    } catch (err) {
      console.error('Error creating List:', err);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Your Lists</h1>
      <div className="mb-4">
        <input
          type="text"
          value={newListName}
          onChange={(e) => setNewListName(e.target.value)}
          placeholder="New List Name"
          className="border p-2 mr-2"
        />
        <button
          onClick={handleCreateList}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Create List
        </button>
        {error && <p className="text-red-500">{error}</p>}
      </div>
      {userLists.length > 0 ? (
        <ul>
          {userLists.map((list) => (
            <li key={list.list_id} className="mb-2 flex justify-between items-center">
              <p>{list.list_name}</p>
              <button
                onClick={() => router.push(`/list/${list.list_id}`)}
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-2 rounded"
              >
                View List
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p>You have no lists.</p>
      )}
    </div>
  );
};

export default ListsPage;
