import '@/../app/globals.css';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import logo from '@/../public/Logo.png';

const Header = () => {
  const router = useRouter();

  const handleLogoClick = () => {
    router.push('/dashboard');
  };

  return (
    <div className="w-full py-2 bg-pink-400 flex justify-center items-center shadow-md">
      <div onClick={handleLogoClick} className="cursor-pointer bg-white p-0 rounded-full hover:bg-gray-200 transition duration-300 flex items-center justify-center" style={{ width: '100px', height: '100px' }}>
        <Image
          src={logo}
          alt="Logo"
          width={120}
          height={120}
          className="rounded-full"
        />
      </div>
    </div>
  );
};

export default Header;
