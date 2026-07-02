import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MatchScoreBadge } from '@/components/ui/Badge';

describe('MatchScoreBadge', () => {
  it('renders score and category', () => {
    render(<MatchScoreBadge score={92} category="Excellent Match" />);
    expect(screen.getByText(/92%/)).toBeInTheDocument();
    expect(screen.getByText(/Excellent Match/)).toBeInTheDocument();
  });

  it('renders nothing without score', () => {
    const { container } = render(<MatchScoreBadge score={null} />);
    expect(container).toBeEmptyDOMElement();
  });
});
