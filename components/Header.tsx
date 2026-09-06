export default function Header() {
  return (
    <header
      style={{
        padding: '20px 0',
        borderBottom: '1px solid #e0e0e0',
        backgroundColor: '#f8f9fa',
      }}
    >
      <div
        className="container"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1a1a1a' }}>
          ⚡ CodeOptimize
        </div>
        <nav style={{ display: 'flex', gap: '24px' }}>
          <a href="#benefits" style={{ color: '#333' }}>Чому?</a>
          <a href="#stats" style={{ color: '#333' }}>Факти</a>
          <a href="#contact" style={{ color: '#333' }}>Контакти</a>
        </nav>
      </div>
    </header>
  );
}