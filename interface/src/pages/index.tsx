import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Cookies from 'js-cookie';

const Home = () => {
  const router = useRouter();

  useEffect(() => {
    const token = Cookies.get('token');
    if (token) {
      router.push('/Dashboard');
    } else {
      router.push('/login');
    }
  }, [router]);

  return null;
};

export default Home;
