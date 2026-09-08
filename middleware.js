import { NextResponse } from 'next/server';

export function middleware(request) {
  // Перевіряємо тільки для /api/telegram
  if (request.nextUrl.pathname === '/api/telegram') {
    const token = request.nextUrl.searchParams.get('token');
    if (token !== process.env.TELEGRAM_BOT_TOKEN) {
      return new NextResponse('Unauthorized', { status: 401 });
    }
  }
  return NextResponse.next();
}

export const config = {
  matcher: '/api/telegram',
};
