import { ReactNode } from 'react';
import './globals.css';
import { Roboto } from 'next/font/google';

// Use next/font to optimize font loading
const roboto = Roboto({
  weight: ['400', '500', '700'],
  subsets: ['latin'],
  display: 'swap',
});

const RootLayout = ({ children }: { children: ReactNode }) => {
  return (
    <html lang="fr">
      <head>
        {/* metadatas pour seo*/}
      </head>
      <body className={roboto.className}>
        {children}
      </body>
    </html>
  );
};

export default RootLayout;
