import { Component, StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

class RootErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 24, background: "var(--bg)", color: "var(--text)" }}>
          <div style={{ maxWidth: 560, width: "100%", textAlign: "center", border: "1px solid var(--border)", borderRadius: 16, padding: 28, background: "var(--surface)", boxShadow: "var(--shadow-card)" }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>⚠️</div>
            <h1 style={{ marginBottom: 10, fontFamily: "Syne" }}>App failed to render</h1>
            <p style={{ color: "var(--text-2)", lineHeight: 1.6 }}>
              The frontend hit a JavaScript error while loading. This is not usually a backend connection issue.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RootErrorBoundary>
      <App />
    </RootErrorBoundary>
  </StrictMode>,
)
