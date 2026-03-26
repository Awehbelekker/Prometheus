import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

// Component under test
import { FeatureBadges } from '../../components/FeatureBadges';

// Mock the data hook to avoid network
jest.mock('../../hooks/useFeatureAvailability', () => ({
  useFeatureAvailability: () => ({
    data: { features: { A: true, B: false }, feature_modes: { A: 'active', B: 'missing' } },
    detail: { success: true, generated_at: 'now', detail: { A: { available: true, mode: 'active', usage_count: 10 }, B: { available: false, mode: 'missing', usage_count: 0 } } },
    error: null,
    loading: false,
    reload: jest.fn(),
  })
}));

expect.extend(toHaveNoViolations);

describe('FeatureBadges accessibility', () => {
  it('has no detectable a11y violations', async () => {
    const { container } = render(<FeatureBadges />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

