import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LoginForm } from '../src/components/auth/LoginForm';

describe('Authentication', () => {
  it('should render login form', () => {
    render(<LoginForm />);
    expect(screen.getByRole('form')).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('should show validation errors for invalid input', async () => {
    render(<LoginForm />);
    
    const submitButton = screen.getByRole('button');
    fireEvent.click(submitButton);

    expect(await screen.findByText(/username must be/i)).toBeInTheDocument();
    expect(await screen.findByText(/password must be/i)).toBeInTheDocument();
  });
});
