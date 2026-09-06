interface Benefit {
  emoji: string;
  title: string;
  desc: string;
}

export default function Benefits() {
  const benefits: Benefit[] = [
    {
      emoji: '🚀',
      title: 'Швидкість завантаження',
      desc: 'Користувачі очікують, що сторінка завантажиться за 2–3 секунди. Оптимізований код скорочує час відповіді та зменшує показник відмов.',
    },
    {
      emoji: '💰',
      title: 'Економія ресурсів',
      desc: 'Менше споживання процесора, пам’яті та трафіку – це зниження витрат на хостинг і покращення екологічності вашого продукту.',
    },
    {
      emoji: '📈',
      title: 'Кращий UX та SEO',
      desc: 'Швидкі сайти краще ранжуються в пошукових системах. Задоволені користувачі частіше повертаються та рекомендують ваш продукт.',
    },
  ];

  return (
    <section id="benefits" style={{ padding: '60px 0' }}>
      <div className="container">
        <h2>Чому оптимізація – обов’язкова?</h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '30px',
          }}
        >
          {benefits.map((b, i) => (
            <div
              key={i}
              style={{
                padding: '30px',
                background: '#ffffff',
                borderRadius: '12px',
                border: '1px solid #e0e0e0',
                boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>{b.emoji}</div>
              <h3 style={{ fontSize: '24px', marginBottom: '12px', color: '#1a1a1a' }}>
                {b.title}
              </h3>
              <p style={{ color: '#555', lineHeight: 1.7 }}>{b.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}