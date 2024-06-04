import Image from 'next/image';
import { useRouter } from 'next/navigation';

const Header = () => {
  const router = useRouter();

  const handleLogoClick = () => {
    router.push('/dashboard');
  };

  return (
    <div className="w-full py-4 bg-gray-800 flex justify-center items-center">
      <div onClick={handleLogoClick} className="cursor-pointer">
        <Image src="/logo.svg" alt="Logo" width={50} height={50} />
      </div>
    </div>
  );
};

export default Header;
