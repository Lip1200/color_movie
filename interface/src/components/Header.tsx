import '@/../app/globals.css';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import logo from '@/../public/Logo.png'

const Header = () => {
  const router = useRouter();

  const handleLogoClick = () => {
    router.push('/dashboard');
  };

  return (
    <div className="w-full py-4 bg-gray-800 flex justify-center items-center shadow-md">
      <div onClick={handleLogoClick} className="cursor-pointer bg-white p-2 rounded-full hover:bg-gray-200 transition duration-300">
        <Image
          src={logo}
          alt="Logo"
          width={300}
          height={300}
        />
      </div>
    </div>
  );
};

export default Header;
