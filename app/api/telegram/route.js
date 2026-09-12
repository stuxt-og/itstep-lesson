import {
  sendMessage,
  handleMessage,
  handleCallback,
  texts,
} from '../../../lib/bot';

const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;

// ============ POST: приймає оновлення від Telegram ============

export async function POST(request) {
  try {
    const url = new URL(request.url);
    const token = url.searchParams.get('token');

    // Перевірка токена
    if (token !== TOKEN) {
      return new Response('Unauthorized', { status: 401 });
    }

    const body = await request.json();
    const { message, callback_query } = body;

    if (callback_query) {
      await handleCallback(callback_query);
      return new Response('OK', { status: 200 });
    }

    if (message) {
      await handleMessage(message);
    }

    return new Response('OK', { status: 200 });
  } catch (error) {
    console.error('Webhook error:', error);
    return new Response('Error', { status: 500 });
  }
}

// ============ GET: керування вебхуком ============

export async function GET(request) {
  const url = new URL(request.url);
  const token = url.searchParams.get('token');
  const action = url.searchParams.get('action');

  if (token !== TOKEN) {
    return new Response('Unauthorized', { status: 401 });
  }

  // --- Встановити вебхук ---
  if (action === 'setWebhook') {
    const webhookUrl = `${BASE_URL}/api/telegram?token=${token}`;
    const res = await fetch(
      `https://api.telegram.org/bot${token}/setWebhook?url=${encodeURIComponent(webhookUrl)}`
    );
    const data = await res.json();
    return Response.json(data);
  }

  // --- Інформація про вебхук ---
  if (action === 'getWebhookInfo') {
    const res = await fetch(`https://api.telegram.org/bot${token}/getWebhookInfo`);
    const data = await res.json();
    return Response.json(data);
  }

  // --- Видалити вебхук ---
  if (action === 'deleteWebhook') {
    const res = await fetch(`https://api.telegram.org/bot${token}/deleteWebhook`);
    const data = await res.json();
    return Response.json(data);
  }

  // --- За замовчуванням: інформація про бота ---
  const me = await fetch(`https://api.telegram.org/bot${token}/getMe`);
  const meData = await me.json();

  return Response.json({
    status: 'ok',
    bot: meData.result,
    webhook: `${BASE_URL}/api/telegram?token=${token}`,
    actions: {
      setWebhook: `/api/telegram?token=${token}&action=setWebhook`,
      getWebhookInfo: `/api/telegram?token=${token}&action=getWebhookInfo`,
      deleteWebhook: `/api/telegram?token=${token}&action=deleteWebhook`,
    },
  });
}
