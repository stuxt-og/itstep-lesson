export default function Features() {
  const features = [
    { emoji: '⚡', title: 'Швидкість', desc: 'Побудовано на найновішому Next.js' },
    { emoji: '🎨', title: 'Дизайн', desc: 'Мінімалістична темна тема' },
    { emoji: '📱', title: 'Адаптивність', desc: 'Працює на всіх пристроях' },
  ];

  return (
    <section id="features" style={{ padding: '60px 0' }}>
      <div className="container">
        <h2 style={{ 
          fontSize: '36px', 
          textAlign: 'center', 
          marginBottom: '40px' 
        }}>
          Можливості
        </h2>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '30px' 
        }}>
          {features.map((f, i) => (
            <div key={i} style={{
              padding: '30px',
              background: '#111',
              borderRadius: '12px',
              border: '1px solid #1a1a1a',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '40px', marginBottom: '12px' }}>{f.emoji}</div>
              <h3 style={{ marginBottom: '8px' }}>{f.title}</h3>
              <p style={{ color: '#888' }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
