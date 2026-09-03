export default function Footer() {
  return (
    <footer id="contact" style={{
      padding: '40px 0',
      borderTop: '1px solid #1a1a1a',
      marginTop: '40px'
    }}>
      <div className="container" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '20px'
      }}>
        <div>
          <p style={{ color: '#666' }}>
            © {new Date().getFullYear()} Мій лендінг
          </p>
        </div>
        <div style={{ display: 'flex', gap: '20px' }}>
          <a href="#" style={{ color: '#666' }}>Twitter</a>
          <a href="#" style={{ color: '#666' }}>GitHub</a>
          <a href="#" style={{ color: '#666' }}>LinkedIn</a>
        </div>
      </div>
    </footer>
  );
}
