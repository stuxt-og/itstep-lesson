export default function Hero() {
  return (
    <section id="hero" style={{ 
      padding: '80px 0',
      textAlign: 'center'
    }}>
      <div className="container">
        <h1 style={{ 
          fontSize: '48px', 
          marginBottom: '20px',
          background: 'linear-gradient(135deg, #8ab4f8, #c084fc)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Ласкаво просимо
        </h1>
        <p style={{ 
          fontSize: '20px', 
          color: '#888', 
          maxWidth: '600px', 
          margin: '0 auto 30px' 
        }}>
          Мінімалістичний лендінг на Next.js 16 з темною темою
        </p>
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
          <a href="#features" style={{
            padding: '12px 32px',
            background: '#8ab4f8',
            color: '#0a0a0a',
            borderRadius: '8px',
            fontWeight: 'bold'
          }}>
            Почати
          </a>
          <a href="#contact" style={{
            padding: '12px 32px',
            border: '1px solid #333',
            borderRadius: '8px'
          }}>
            Дізнатись більше
          </a>
        </div>
      </div>
    </section>
  );
}
