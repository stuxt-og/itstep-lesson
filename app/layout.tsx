export const metadata = {
  title: 'Telegram Bot',
  description: 'Next.js Telegram Bot Webhook',
};

export default function RootLayout({ children }) {
  return (
    <html lang="uk">
      <body>{children}</body>
    </html>
  );
}
