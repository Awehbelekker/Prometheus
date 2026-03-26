import React from 'react';
import { render, screen } from '@testing-library/react';
import UnifiedSidebar from '../components/unified/UnifiedSidebar';
import { FeatureFlagsProvider } from '../context/UserContext';

// Helper to mock fetch flags
function mockFlags(list: string[]) {
  // @ts-ignore
  global.fetch = jest.fn().mockResolvedValue({ ok:true, json: async()=> ({ flags: list, revolutionary_enabled: list.some(f=>f.startsWith('holo')) }) });
}

describe('UnifiedSidebar feature gating', ()=>{
  afterEach(()=>{ // @ts-ignore
    if(global.fetch) (global.fetch as jest.Mock).mockReset(); });

  test('without revolutionary flags hides group items', async()=>{
    mockFlags(['dashboard','settings']);
    const { container, findByText } = render(<FeatureFlagsProvider><UnifiedSidebar selected="dashboard" onSelect={()=>{}} /></FeatureFlagsProvider>);
    // Wait for the CORE group header (disambiguates from item labels containing "Dashboard")
    await findByText(/^CORE$/i);
    expect(container.textContent).not.toMatch(/Holographic UI/i);
  });

  test('with revolutionary flags shows holographic item', async()=>{
    mockFlags(['dashboard','settings','holographic_ui']);
    const { findByText } = render(<FeatureFlagsProvider><UnifiedSidebar selected="dashboard" onSelect={()=>{}} /></FeatureFlagsProvider>);
    await findByText(/Holographic UI/);
  });
});
