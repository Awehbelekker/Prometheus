import React from 'react';
import { render, screen, act } from '@testing-library/react';
import StatusBar from '../components/status/StatusBar';

// Mock fetch for pings
beforeAll(()=>{
  // @ts-ignore
  global.fetch = jest.fn().mockResolvedValue({ ok:true, json: async()=> ({ system:'online' }) });
});

afterAll(()=>{ // @ts-ignore
  delete global.fetch; });

afterEach(()=>{ // @ts-ignore
  (global.fetch as jest.Mock).mockClear(); });

// Mock WebSocket
class MockWebSocket {
  static instances: MockWebSocket[] = [];
  onopen: any; onmessage: any; onclose: any; onerror: any; readyState = 1;
  constructor(url: string){ MockWebSocket.instances.push(this); setTimeout(()=> this.onopen && this.onopen({}), 0); }
  send(){ /* noop */ }
  close(){ this.readyState = 3; this.onclose && this.onclose({}); }
}
// @ts-ignore
global.WebSocket = MockWebSocket;

test('StatusBar updates on performance_update message', async()=> {
  render(<StatusBar currentPanel="dashboard" onOpenPalette={()=>{}} />);
  // Emit performance update
  await act(async()=>{
    const ws = MockWebSocket.instances[0];
    ws.onmessage({ data: JSON.stringify({ type:'performance_update', data:{ cpu:12, memory:34, disk:56, network:78 }, timestamp: new Date().toISOString() }) });
  });
  expect(await screen.findByText(/CPU 12%/)).toBeInTheDocument();
  expect(screen.getByText(/Mem 34%/)).toBeInTheDocument();
  expect(screen.getByText(/Disk 56%/)).toBeInTheDocument();
  expect(screen.getByText(/Net 78%/)).toBeInTheDocument();
});
