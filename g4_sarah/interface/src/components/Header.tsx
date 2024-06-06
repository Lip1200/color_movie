import '@/app/globals.css';
import Image from 'next/image';
import { useRouter } from 'next/navigation';

const Header = () => {
  const router = useRouter();

  const handleLogoClick = () => {
    router.push('/dashboard');
  };

  return (
    <div className="w-full py-4 bg-gray-800 flex justify-center items-center">
      <div onClick={handleLogoClick} className="cursor-pointer bg-white p-2 rounded-full">
        <Image
          src="/logo.png"
          alt="Logo"
          width={100}
          height={100}
        />
      </div>
    </div>
  );
};

export default Header;
