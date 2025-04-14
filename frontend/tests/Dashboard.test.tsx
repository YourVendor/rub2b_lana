import { render, screen } from '@testing-library/react';
import Dashboard from '../src/components/Dashboard';

test('renders dashboard', () => {
  render(<Dashboard />);
  expect(screen.getByText(/Дашборд/i)).toBeInTheDocument();
});