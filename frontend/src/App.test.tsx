import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Twiga Scan app', () => {
  render(<App />);
  // Look for the Twiga logo emoji or title
  const logoElement = screen.getByText(/🦒/);
  expect(logoElement).toBeInTheDocument();
});
