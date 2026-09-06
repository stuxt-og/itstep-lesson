export default function Hero() {
  return (
    <section
      id="hero"
      style={{
        padding: '80px 0',
        textAlign: 'center',
        backgroundColor: '#f8f9fa',
      }}
    >
      <div className="container">
        <h1
          style={{
            fontSize: '48px',
            marginBottom: '20px',
            background: 'linear-gradient(135deg, #0066cc, #7c3aed)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Оптимізація коду – це не розкіш, а необхідність
        </h1>
        <p
          style={{
            fontSize: '20px',
            color: '#555',
            maxWidth: '700px',
            margin: '0 auto 30px',
          }}
        >
          У сучасному світі швидкість, ефективність та продуктивність визначають
          успіх будь-якого цифрового продукту. Дізнайтеся, чому оптимізація коду
          має бути у вашому щоденному фокусі.
        </p>
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
          <a
            href="#benefits"
            style={{
              padding: '12px 32px',
              background: '#0066cc',
              color: '#ffffff',
              borderRadius: '8px',
              fontWeight: 'bold',
              border: 'none',
            }}
          >
            Дізнатись більше
          </a>
          <a
            href="#stats"
            style={{
              padding: '12px 32px',
              border: '1px solid #ccc',
              borderRadius: '8px',
              color: '#333',
            }}
          >
            Подивитись факти
          </a>
        </div>
      </div>
    </section>
  );
}