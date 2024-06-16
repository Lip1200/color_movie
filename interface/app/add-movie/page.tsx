import React, { Suspense } from 'react';
import AddMovieForm from './add-movie-form';

const AddMoviePage = () => (
  <Suspense fallback={<div>Loading...</div>}>
    <AddMovieForm />
  </Suspense>
);

export default AddMoviePage;
