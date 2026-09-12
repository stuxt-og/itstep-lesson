export const metadata = {
  title: 'Optimization Bot',
  description: 'Telegram-бот про оптимізацію коду',
};

export default function RootLayout({ children }) {
  return (
    <html lang="uk">
      <body>{children}</body>
    </html>
  );
}