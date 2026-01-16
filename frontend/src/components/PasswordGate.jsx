import { useState } from 'react';

export default function PasswordGate({ onAuthenticated }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Small delay to prevent brute force and show loading state
    setTimeout(() => {
      const correctPassword = import.meta.env.VITE_APP_PASSWORD;

      if (!correctPassword) {
        // No password configured, allow access
        sessionStorage.setItem('authenticated', 'true');
        onAuthenticated();
        return;
      }

      if (password === correctPassword) {
        sessionStorage.setItem('authenticated', 'true');
        onAuthenticated();
      } else {
        setError('Incorrect password');
        setPassword('');
      }
      setIsLoading(false);
    }, 500);
  };

  return (
    <div className="password-gate">
      <div className="password-gate-card">
        <div className="password-gate-icon">🍽️</div>
        <h1>Restaurant Lead Enrichment</h1>
        <p>Enter password to continue</p>

        <form onSubmit={handleSubmit}>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="password-input"
            autoFocus
            disabled={isLoading}
          />

          {error && <div className="password-error">{error}</div>}

          <button
            type="submit"
            className="password-submit"
            disabled={isLoading || !password}
          >
            {isLoading ? 'Checking...' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
  );
}
