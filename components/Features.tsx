interface Feature {
  emoji: string;
  title: string;
  desc: string;
}

export default function Features() {
  const features: Feature[] = [
    { emoji: '⚡', title: 'Швидкість', desc: 'Побудовано на найновішому Next.js' },
    { emoji: '🎨', title: 'Дизайн', desc: 'Мінімалістична світла тема' },
    { emoji: '📱', title: 'Адаптивність', desc: 'Працює на всіх пристроях' },
  ];

  return (
    <section id="features" style={{ padding: '60px 0' }}>
      <div className="container">
        <h2
          style={{
            fontSize: '36px',
            textAlign: 'center',
            marginBottom: '40px',
            color: '#1a1a1a',
          }}
        >
          Можливості
        </h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '30px',
          }}
        >
          {features.map((f: Feature, i: number) => (
            <div
              key={i}
              style={{
                padding: '30px',
                background: '#ffffff',
                borderRadius: '12px',
                border: '1px solid #e0e0e0',
                textAlign: 'center',
                boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
              }}
            >
              <div style={{ fontSize: '40px', marginBottom: '12px' }}>
                {f.emoji}
              </div>
              <h3 style={{ marginBottom: '8px', color: '#1a1a1a' }}>
                {f.title}
              </h3>
              <p style={{ color: '#666' }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}