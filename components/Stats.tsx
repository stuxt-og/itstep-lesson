interface Stat {
  value: string;
  label: string;
}

export default function Stats() {
  const stats: Stat[] = [
    { value: '53%', label: 'користувачів покидають сайт, якщо він завантажується довше 3 секунд' },
    { value: '47%', label: 'зменшення часу завантаження збільшує конверсію на 47%' },
    { value: '70%', label: 'оптимізовані сайти споживають на 70% менше трафіку' },
  ];

  return (
    <section
      id="stats"
      style={{
        backgroundColor: '#f0f4ff',
        padding: '60px 0',
      }}
    >
      <div className="container">
        <h2>Факти, які говорять самі за себе</h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '30px',
            marginTop: '20px',
          }}
        >
          {stats.map((s, i) => (
            <div
              key={i}
              style={{
                background: '#ffffff',
                padding: '30px',
                borderRadius: '12px',
                border: '1px solid #d0dfff',
                textAlign: 'center',
                boxShadow: '0 4px 12px rgba(0,102,204,0.08)',
              }}
            >
              <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#0066cc', marginBottom: '12px' }}>
                {s.value}
              </div>
              <p style={{ color: '#333', fontSize: '16px' }}>{s.label}</p>
            </div>
          ))}
        </div>
        <p style={{ textAlign: 'center', marginTop: '40px', color: '#555', fontSize: '18px' }}>
          Джерело: дослідження Google, Akamai та Web Almanac
        </p>
      </div>
    </section>
  );
}