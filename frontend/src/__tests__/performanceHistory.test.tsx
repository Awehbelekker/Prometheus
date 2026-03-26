import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { PerformanceHistoryPanel } from '../components/performance/PerformanceHistoryPanel';

class MockWebSocket { static instances: MockWebSocket[]=[]; onopen:any; onmessage:any; onclose:any; readyState=1; constructor(url:string){ MockWebSocket.instances.push(this); setTimeout(()=> this.onopen && this.onopen({}),0);} send(){} close(){ this.readyState=3; this.onclose && this.onclose({}); }}
// @ts-ignore
global.WebSocket = MockWebSocket;

test('aggregates performance_history snapshots', async()=>{
  render(<PerformanceHistoryPanel />);
  await act(async()=>{
    const ws = MockWebSocket.instances[0];
    ws.onmessage({ data: JSON.stringify({ type:'performance_history', data:[{ cpu:10,memory:20,disk:30,network:40, ts:'2025-01-01T00:00:00Z'}], timestamp:new Date().toISOString() }) });
    ws.onmessage({ data: JSON.stringify({ type:'performance_update', data:{ cpu:11,memory:21,disk:31,network:41 }, timestamp:new Date().toISOString() }) });
  });
  expect(await screen.findByText(/Samples 2/)).toBeInTheDocument();
});
