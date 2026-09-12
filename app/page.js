export default function Home() {
  const token = process.env.TELEGRAM_BOT_TOKEN || '';
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || '';

  return (
    <div style={{ padding: '40px', fontFamily: 'system-ui', maxWidth: '720px', margin: '0 auto' }}>
      <h1>🤖 Optimization Bot</h1>
      <p>Telegram-бот про оптимізацію коду через вебхук.</p>

      <h2>Встановити вебхук</h2>
      <p>Відкрийте це посилання у браузері:</p>
      <pre style={{ background: '#f0f0f0', padding: '12px', borderRadius: '8px', overflowX: 'auto' }}>
        {`${baseUrl}/api/telegram?token=${token}&action=setWebhook`}
      </pre>

      <h2>Перевірити вебхук</h2>
      <pre style={{ background: '#f0f0f0', padding: '12px', borderRadius: '8px', overflowX: 'auto' }}>
        {`${baseUrl}/api/telegram?token=${token}&action=getWebhookInfo`}
      </pre>

      <h2>Видалити вебхук</h2>
      <pre style={{ background: '#f0f0f0', padding: '12px', borderRadius: '8px', overflowX: 'auto' }}>
        {`${baseUrl}/api/telegram?token=${token}&action=deleteWebhook`}
      </pre>
    </div>
  );
}