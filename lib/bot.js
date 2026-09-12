const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const API = `https://api.telegram.org/bot${TOKEN}`;

// ========== КЛАВІАТУРИ ==========

export const mainMenu = {
  keyboard: [
    [{ text: '⚡ Швидкість' }, { text: '💰 Економія' }],
    [{ text: '📈 SEO та UX' }, { text: '🛠 Інструменти' }],
    [{ text: '📚 Поради' }, { text: '❓ Допомога' }],
  ],
  resize_keyboard: true,
};

export const toolsMenu = {
  inline_keyboard: [
    [{ text: '🔍 Lighthouse', url: 'https://pagespeed.web.dev/' }],
    [{ text: '📦 Bundle Analyzer', url: 'https://www.npmjs.com/package/@next/bundle-analyzer' }],
    [{ text: '🧹 ESLint', url: 'https://eslint.org/' }],
    [{ text: '⬅️ Назад', callback_data: 'back_to_main' }],
  ],
};

export const tipsMenu = {
  inline_keyboard: [
    [{ text: '💡 Порада 1', callback_data: 'tip_1' }],
    [{ text: '💡 Порада 2', callback_data: 'tip_2' }],
    [{ text: '💡 Порада 3', callback_data: 'tip_3' }],
    [{ text: '⬅️ Назад', callback_data: 'back_to_main' }],
  ],
};

// ========== ВІДПРАВКА ==========

export async function sendMessage(chatId, text, replyMarkup = null) {
  try {
    const res = await fetch(`${API}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text,
        parse_mode: 'HTML',
        reply_markup: replyMarkup,
        disable_web_page_preview: true,
      }),
    });
    return await res.json();
  } catch (e) {
    console.error('sendMessage error:', e.message);
  }
}

export async function answerCallback(id, text = '') {
  try {
    await fetch(`${API}/answerCallbackQuery`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ callback_query_id: id, text }),
    });
  } catch (e) {
    console.error('answerCallback error:', e.message);
  }
}

// ========== ТЕКСТИ ==========

export const texts = {
  start: (name) =>
    `👋 Вітаю, <b>${name}</b>!\n\n` +
    `Я — бот про <b>оптимізацію коду</b>. Розповім, чому це критично важливо у сучасному світі, ` +
    `які є інструменти та як покращити свій продукт.\n\n` +
    `Обери категорію нижче 👇`,

  speed:
    `⚡ <b>Швидкість завантаження</b>\n\n` +
    `Користувачі очікують, що сторінка завантажиться за <b>2–3 секунди</b>. ` +
    `Кожна зайва секунда — це <b>-7% конверсії</b>.\n\n` +
    `🔹 <b>Що впливає на швидкість:</b>\n` +
    `• Розмір JS-бандла\n` +
    `• Кількість HTTP-запитів\n` +
    `• Оптимізація зображень\n` +
    `• Кешування та CDN\n` +
    `• Lazy loading`,

  economy:
    `💰 <b>Економія ресурсів</b>\n\n` +
    `Оптимізований код споживає менше:\n\n` +
    `🖥 <b>CPU</b> — менше навантаження\n` +
    `🧠 <b>RAM</b> — менше пам'яті\n` +
    `📡 <b>Трафік</b> — менше даних\n` +
    `🔋 <b>Батарею</b> — на мобільних\n\n` +
    `🌱 Це ще й <b>екологічно</b>.`,

  seo:
    `📈 <b>SEO та UX</b>\n\n` +
    `Google враховує швидкість сайту в ранжуванні:\n\n` +
    `✅ Вище в пошуку\n` +
    `✅ Менше відмов\n` +
    `✅ Більше часу на сторінці\n` +
    `✅ Кращий Core Web Vitals`,

  tools:
    `🛠 <b>Інструменти оптимізації</b>\n\n` +
    `Обери інструмент нижче 👇`,

  help:
    `❓ <b>Допомога</b>\n\n` +
    `📋 <b>Команди:</b>\n` +
    `/start — головне меню\n` +
    `/help — довідка\n` +
    `/info — про бота\n` +
    `/stats — статистика\n` +
    `/profile — профіль`,

  info:
    `🤖 <b>Про бота</b>\n\n` +
    `📌 <b>Назва:</b> Optimization Bot\n` +
    `🎯 <b>Тема:</b> Оптимізація коду\n` +
    `🛠 <b>Технології:</b> Next.js 16 + Telegram Webhook\n` +
    `📅 <b>Версія:</b> 1.0.0`,
};

// ========== CALLBACK ==========

export async function handleCallback(cb) {
  const chatId = cb.message.chat.id;
  const data = cb.data;

  await answerCallback(cb.id);

  switch (data) {
    case 'back_to_main':
      await sendMessage(chatId, '🏠 Головне меню:', mainMenu);
      break;

    case 'tip_1':
      await sendMessage(
        chatId,
        `💡 <b>Порада 1: Мініфікуйте код</b>\n\n` +
        `Terser або esbuild стискають JS на <b>30–50%</b> без втрати функціональності.`,
        tipsMenu
      );
      break;

    case 'tip_2':
      await sendMessage(
        chatId,
        `💡 <b>Порада 2: Lazy loading</b>\n\n` +
        `Завантажуйте зображення та компоненти лише тоді, коли вони потрібні.`,
        tipsMenu
      );
      break;

    case 'tip_3':
      await sendMessage(
        chatId,
        `💡 <b>Порада 3: Кешуйте все</b>\n\n` +
        `HTTP-кеш, Redis, CDN — зменшують навантаження в рази.`,
        tipsMenu
      );
      break;

    default:
      await sendMessage(chatId, '❓ Невідома дія', mainMenu);
  }
}

// ========== ПОВІДОМЛЕННЯ ==========

export async function handleMessage(msg) {
  const chatId = msg.chat.id;
  const text = (msg.text || '').trim();
  const name = msg.from?.first_name || 'друже';

  if (text === '/start') {
    await sendMessage(chatId, texts.start(name), mainMenu);
    return;
  }
  if (text === '/help' || text === '❓ Допомога') {
    await sendMessage(chatId, texts.help, mainMenu);
    return;
  }
  if (text === '/info') {
    await sendMessage(chatId, texts.info, mainMenu);
    return;
  }
  if (text === '/stats') {
    await sendMessage(chatId, `📊 <b>Статистика</b>\n\n👥 Користувачів: 1`, mainMenu);
    return;
  }
  if (text === '/profile') {
    const u = msg.from;
    await sendMessage(
      chatId,
      `👤 <b>Профіль</b>\n\n🆔 <code>${u.id}</code>\n👋 ${u.first_name || '—'}\n` +
      `🏷 ${u.username ? '@' + u.username : '—'}\n🌍 ${u.language_code || '—'}`,
      mainMenu
    );
    return;
  }

  if (text === '⚡ Швидкість') return sendMessage(chatId, texts.speed, mainMenu);
  if (text === '💰 Економія') return sendMessage(chatId, texts.economy, mainMenu);
  if (text === '📈 SEO та UX') return sendMessage(chatId, texts.seo, mainMenu);
  if (text === '🛠 Інструменти') return sendMessage(chatId, texts.tools, toolsMenu);
  if (text === '📚 Поради') {
    return sendMessage(
      chatId,
      '📚 <b>Поради з оптимізації</b>\n\nОбери, що цікавить 👇',
      tipsMenu
    );
  }

  await sendMessage(
    chatId,
    `✍️ Ви написали: <b>${text}</b>\n\nСпробуйте /help.`,
    mainMenu
  );
}