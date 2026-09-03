import './globals.css';

export const metadata = {
  title: 'Мій лендінг',
  description: 'Мінімальний лендінг на Next.js 16',
};

export default function RootLayout({ children }) {
  return (
    <html lang="uk">
      <body>{children}</body>
    </html>
  );
}
