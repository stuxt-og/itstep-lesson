import { 
  sendMessage, 
  answerCallbackQuery, 
  mainMenuKeyboard, 
  inlineButtons 
} from '../../../lib/bot';

export async function POST(request) {
  try {
    const url = new URL(request.url);
    const token = url.searchParams.get('token');
    
    // Перевірка токена
    if (token !== process.env.TELEGRAM_BOT_TOKEN) {
      return new Response('Unauthorized', { status: 401 });
    }

    const body = await request.json();
    const { message, callback_query } = body;

    // Обробка callback_query (натискання на inline кнопки)
    if (callback_query) {
      await handleCallbackQuery(callback_query);
      return new Response('OK', { status: 200 });
    }

    // Обробка звичайних повідомлень
    if (message) {
      await handleMessage(message);
    }

    return new Response('OK', { status: 200 });
  } catch (error) {
    console.error('Telegram webhook error:', error);
    return new Response('Error', { status: 500 });
  }
}

// Обробка callback queries
async function handleCallbackQuery(callbackQuery) {
  const { id, data, from, message } = callbackQuery;
  const chatId = message.chat.id;
  const userId = from.id;

  // Відповідаємо на callback (прибираємо "годинник")
  await answerCallbackQuery(id);

  let responseText = '';

  switch (data) {
    case 'yes':
      responseText = '✅ Чудово! Ви обрали "Так". Що далі?';
      break;
    case 'no':
      responseText = '❌ Ви обрали "Ні". Можливо, наступного разу?';
      break;
    default:
      responseText = `❓ Невідома дія: ${data}`;
  }

  // Відправляємо відповідь
  await sendMessage(chatId, responseText, mainMenuKeyboard);
}

// Обробка звичайних повідомлень
async function handleMessage(message) {
  const chatId = message.chat.id;
  const text = message.text || '';
  const firstName = message.from?.first_name || 'Користувач';

  // Команди
  if (text === '/start' || text === '/menu') {
    await sendMessage(
      chatId,
      `👋 Вітаю, <b>${firstName}</b>!\n\nЯ — ваш помічник. Ось що я вмію:\n\n` +
      `📌 <b>Основні команди:</b>\n` +
      `/start - Головне меню\n` +
      `/help - Допомога\n` +
      `/info - Інформація\n` +
      `/stats - Статистика\n` +
      `/profile - Профіль\n\n` +
      `Використовуйте кнопки для зручної навігації.`,
      mainMenuKeyboard
    );
    return;
  }

  if (text === '/help' || text === '❓ Допомога') {
    await sendMessage(
      chatId,
      `🆘 <b>Допомога</b>\n\n` +
      `Я вмію відповідати на команди та повідомлення.\n\n` +
      `📋 <b>Доступні команди:</b>\n` +
      `/start - Головне меню\n` +
      `/help - Це повідомлення\n` +
      `/info - Інформація про бота\n` +
      `/stats - Статистика використання\n` +
      `/profile - Ваш профіль\n\n` +
      `Також я реагую на кнопки та текстові повідомлення.`,
      mainMenuKeyboard
    );
    return;
  }

  if (text === '/info' || text === 'ℹ️ Інформація') {
    await sendMessage(
      chatId,
      `🤖 <b>Інформація про бота</b>\n\n` +
      `📌 <b>Назва:</b> Next.js Telegram Bot\n` +
      `🛠 <b>Технології:</b> Next.js 16, App Router\n` +
      `📅 <b>Версія:</b> 1.0.0\n` +
      `👨‍💻 <b>Розробник:</b> AI Assistant\n\n` +
      `💡 Бот створено для демонстрації роботи вебхуків Next.js.`,
      mainMenuKeyboard
    );
    return;
  }

  if (text === '/stats' || text === '📊 Статистика') {
    await sendMessage(
      chatId,
      `📈 <b>Статистика</b>\n\n` +
      `👥 <b>Користувачі:</b> 1\n` +
      `💬 <b>Повідомлень:</b> Багато 😄\n` +
      `⏱ <b>Час роботи:</b> 24/7\n\n` +
      `Це демонстраційна статистика.`,
      mainMenuKeyboard
    );
    return;
  }

  if (text === '/profile' || text === '👤 Профіль') {
    const user = message.from;
    await sendMessage(
      chatId,
      `👤 <b>Ваш профіль</b>\n\n` +
      `🆔 <b>ID:</b> ${user.id}\n` +
      `👋 <b>Ім'я:</b> ${user.first_name || 'Невідомо'}\n` +
      `🏷 <b>Username:</b> ${user.username ? '@' + user.username : 'Не вказано'}\n` +
      `🌍 <b>Мова:</b> ${user.language_code || 'Невідомо'}\n\n` +
      `🤖 <b>Статус:</b> Активний`,
      mainMenuKeyboard
    );
    return;
  }

  if (text === '🎯 Команди') {
    await sendMessage(
      chatId,
      `🎯 <b>Доступні команди</b>\n\n` +
      `/start - Головне меню\n` +
      `/help - Допомога\n` +
      `/info - Інформація\n` +
      `/stats - Статистика\n` +
      `/profile - Профіль\n\n` +
      `Також я реагую на текстові повідомлення. Спробуйте щось написати!`,
      mainMenuKeyboard
    );
    return;
  }

  // Обробка звичайних текстових повідомлень (не команд)
  if (text && !text.startsWith('/')) {
    // Показуємо inline кнопки для інтерактиву
    await sendMessage(
      chatId,
      `✍️ Ви написали: <b>${text}</b>\n\n` +
      `Це звичайне повідомлення. Ось що я можу запропонувати:`,
      inlineButtons.reply_markup
    );
    return;
  }

  // Якщо нічого не підійшло
  await sendMessage(
    chatId,
    `🤔 Я не зрозумів вашу команду. Використовуйте /help для списку команд.`,
    mainMenuKeyboard
  );
}

// GET запит для встановлення вебхука та інформації
export async function GET(request) {
  const url = new URL(request.url);
  const token = url.searchParams.get('token');
  const action = url.searchParams.get('action');

  if (token !== process.env.TELEGRAM_BOT_TOKEN) {
    return new Response('Unauthorized', { status: 401 });
  }

  // Встановлення вебхука
  if (action === 'setWebhook') {
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL;
    const webhookUrl = `${baseUrl}/api/telegram?token=${token}`;
    
    const response = await fetch(
      `https://api.telegram.org/bot${token}/setWebhook?url=${encodeURIComponent(webhookUrl)}`
    );
    const data = await response.json();
    
    return new Response(JSON.stringify(data, null, 2), {
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Отримання інформації про вебхук
  if (action === 'getWebhookInfo') {
    const response = await fetch(
      `https://api.telegram.org/bot${token}/getWebhookInfo`
    );
    const data = await response.json();
    
    return new Response(JSON.stringify(data, null, 2), {
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Інформація про бота
  const me = await fetch(`https://api.telegram.org/bot${token}/getMe`);
  const meData = await me.json();

  return new Response(JSON.stringify({
    status: 'ok',
    bot: meData.result,
    webhook: `${process.env.NEXT_PUBLIC_BASE_URL}/api/telegram?token=${token}`,
    endpoints: {
      setWebhook: `/api/telegram?token=${token}&action=setWebhook`,
      getWebhookInfo: `/api/telegram?token=${token}&action=getWebhookInfo`,
    }
  }, null, 2), {
    headers: { 'Content-Type': 'application/json' },
  });
}
