export default function Home() {
  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h1>🤖 Telegram Bot</h1>
      <p>Бот працює через вебхук. Ендпойнт: <code>/api/telegram?token=YOUR_TOKEN</code></p>
      <p>Для встановлення вебхука виконайте запит:</p>
      <pre style={{ background: '#f0f0f0', padding: '12px', borderRadius: '8px' }}>
        {`https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/setWebhook?url=${process.env.NEXT_PUBLIC_BASE_URL}/api/telegram?token=${process.env.TELEGRAM_BOT_TOKEN}`}
      </pre>
    </div>
  );
}
