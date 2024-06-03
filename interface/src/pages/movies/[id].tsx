import { GetServerSideProps } from 'next';
import dynamic from 'next/dynamic';
import { MoviePageProps } from '@/components/Movie/MoviePage';

const MoviePage = dynamic(() => import('@/components/Movie/MoviePage'), {
  ssr: false,
});

const MovieDetailsPage: React.FC<MoviePageProps> = ({ movie }) => {
  return <MoviePage movie={movie} />;
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { id } = context.params!;
  const res = await fetch(`http://localhost:5001/movies/${id}`);
  const movie = await res.json();

  if (res.status !== 200) {
    return {
      notFound: true,
    };
  }

  return {
    props: {
      movie,
    },
  };
};

export default MovieDetailsPage;
