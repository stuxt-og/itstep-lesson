export default function Header() {
  return (
    <header style={{ 
      padding: '20px 0', 
      borderBottom: '1px solid #1a1a1a' 
    }}>
      <div className="container" style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center' 
      }}>
        <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
          🚀 Лендінг
        </div>
        <nav style={{ display: 'flex', gap: '24px' }}>
          <a href="#hero">Головна</a>
          <a href="#features">Можливості</a>
          <a href="#contact">Контакти</a>
        </nav>
      </div>
    </header>
  );
}
