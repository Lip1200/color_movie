import { ReactNode } from 'react';
import './globals.css';

const RootLayout = ({ children }: { children: ReactNode }) => {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap"
        />
      </head>
      <body>{children}</body>
    </html>
  );
};

export default RootLayout;
