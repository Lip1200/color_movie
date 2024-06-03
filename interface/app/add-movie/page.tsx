import { Suspense } from 'react';
import AddMovieForm from '@/components/AddMovie/AddMovieForm';

const AddMoviePage = () => (
  <Suspense fallback={<div>Loading...</div>}>
    <AddMovieForm />
  </Suspense>
);

export default AddMoviePage;
