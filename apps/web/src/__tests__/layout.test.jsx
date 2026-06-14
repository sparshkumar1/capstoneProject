import { useState } from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ThemeToggle from '../ThemeToggle';
import Topbar from '../Topbar';
import { ThemeContext, SessionContext } from '../contexts';

function ThemeHarness() {
  const [theme, setTheme] = useState('dark');
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <ThemeToggle />
      <div data-testid="theme-value">{theme}</div>
    </ThemeContext.Provider>
  );
}

function renderTopbar({ candidate = null, navigate = vi.fn(), showNav = true } = {}) {
  return render(
    <ThemeContext.Provider value={{ theme: 'dark', setTheme: vi.fn() }}>
      <SessionContext.Provider value={{ candidate, session: null, setSession: vi.fn(), setCandidate: vi.fn() }}>
        <Topbar navigate={navigate} showNav={showNav} />
      </SessionContext.Provider>
    </ThemeContext.Provider>,
  );
}

describe('ThemeToggle', () => {
  it('toggles between dark and light themes', () => {
    render(<ThemeHarness />);

    const button = screen.getByRole('button', { name: /toggle theme/i });
    expect(button).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
    expect(button).toHaveTextContent('☀️');

    fireEvent.click(button);

    expect(button).toHaveAttribute('aria-pressed', 'false');
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
    expect(button).toHaveTextContent('🌙');
  });
});

describe('Topbar', () => {
  it('renders the candidate badge and navigation buttons', () => {
    const navigate = vi.fn();
    renderTopbar({ candidate: { name: 'Aria' }, navigate });

    expect(screen.getByText(/Interview Preparation Platform/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /topics/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /admin/i })).toBeInTheDocument();
    expect(screen.getByText('Aria')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /topics/i }));
    expect(navigate).toHaveBeenCalledWith('topics');
  });

  it('can hide navigation controls when requested', () => {
    renderTopbar({ showNav: false });
    expect(screen.queryByRole('button', { name: /topics/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /admin/i })).not.toBeInTheDocument();
  });
});
