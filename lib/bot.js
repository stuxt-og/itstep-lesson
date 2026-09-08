// Бібліотека для роботи з Telegram API
const TELEGRAM_API = `https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}`;

// Клавіатура головного меню
export const mainMenuKeyboard = {
  keyboard: [
    [{ text: 'ℹ️ Інформація' }, { text: '📊 Статистика' }],
    [{ text: '🎯 Команди' }, { text: '❓ Допомога' }],
    [{ text: '👤 Профіль' }],
  ],
  resize_keyboard: true,
  one_time_keyboard: false,
};

// Inline кнопки
export const inlineButtons = {
  reply_markup: {
    inline_keyboard: [
      [
        { text: '✅ Так', callback_data: 'yes' },
        { text: '❌ Ні', callback_data: 'no' },
      ],
      [{ text: '📞 Зв\'язатися', url: 'https://t.me/your_support' }],
    ],
  },
};

// Відправка запиту до Telegram API
export async function sendMessage(chatId, text, replyMarkup = null) {
  const response = await fetch(`${TELEGRAM_API}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text,
      reply_markup: replyMarkup,
      parse_mode: 'HTML',
    }),
  });
  return response.json();
}

// Відправка відповіді на callback query
export async function answerCallbackQuery(callbackQueryId, text = null) {
  const response = await fetch(`${TELEGRAM_API}/answerCallbackQuery`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      callback_query_id: callbackQueryId,
      text,
      show_alert: false,
    }),
  });
  return response.json();
}

// Встановлення вебхука
export async function setWebhook(url) {
  const response = await fetch(`${TELEGRAM_API}/setWebhook`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  return response.json();
}

// Відправка повідомлення з фото
export async function sendPhoto(chatId, photoUrl, caption = '') {
  const response = await fetch(`${TELEGRAM_API}/sendPhoto`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      photo: photoUrl,
      caption,
      parse_mode: 'HTML',
    }),
  });
  return response.json();
}

// Отримання інформації про бота
export async function getMe() {
  const response = await fetch(`${TELEGRAM_API}/getMe`);
  return response.json();
}
