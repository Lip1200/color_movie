import MoviePage from './movie-page';
import React, { Suspense } from 'react';

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <MoviePage />
    </Suspense>
  );
}
