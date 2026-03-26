import React from 'react';
import { render } from '@testing-library/react';
import UnifiedSidebar from '../components/unified/UnifiedSidebar';
import { FeatureFlagsProvider } from '../context/UserContext';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

// Mock fetch for feature flags
beforeEach(()=>{
  // @ts-ignore
  global.fetch = jest.fn().mockResolvedValue({ ok:true, json: async()=> ({ flags:['dashboard','settings'], revolutionary_enabled:false }) });
});

afterEach(()=>{ // @ts-ignore
  global.fetch && global.fetch.mockClear(); });

test('UnifiedSidebar has no a11y violations', async()=>{
  const { container } = render(<FeatureFlagsProvider><UnifiedSidebar selected="dashboard" onSelect={()=>{}} /></FeatureFlagsProvider>);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
