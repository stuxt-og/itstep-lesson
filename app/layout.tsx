import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Оптимізація коду – запорука успіху',
  description: 'Чому оптимізація коду залишається обов\'язковим заняттям у сучасному світі',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uk">
      <body>{children}</body>
    </html>
  );
}