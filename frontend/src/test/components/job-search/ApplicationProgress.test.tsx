import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ApplicationProgress } from '@/components/job-search/ApplicationProgress';

describe('ApplicationProgress', () => {
  it('renders automation steps', () => {
    render(<ApplicationProgress currentStep={2} status="started" />);
    expect(screen.getByText('Navigate')).toBeInTheDocument();
    expect(screen.getByText(/status: started/i)).toBeInTheDocument();
  });
});
