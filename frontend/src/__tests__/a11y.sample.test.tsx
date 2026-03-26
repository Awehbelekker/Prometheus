import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import PerformanceHistoryPanel from '../components/performance/PerformanceHistoryPanel';

expect.extend(toHaveNoViolations);

// Basic accessibility smoke test for a key panel
// NOTE: WebSocket usage will attempt to connect; we can mock it or stub global.WebSocket
class MockWebSocket { onopen:any; onmessage:any; readyState=1; constructor(){ setTimeout(()=> this.onopen && this.onopen({}),0);} send(){} close(){} }
// @ts-ignore
global.WebSocket = MockWebSocket;

test('PerformanceHistoryPanel has no obvious a11y violations', async()=>{
  const { container } = render(<PerformanceHistoryPanel />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
