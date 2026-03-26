import React from 'react';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import RiskEnginePanel from '../components/RiskEnginePanel';
import { SnackbarProvider } from 'notistack';
import { installRiskAuditFetchMock, FIXED_TS } from '../testUtils/fetchMocks';

jest.mock('notistack', () => ({
  SnackbarProvider: ({ children }: any) => children,
  useSnackbar: () => ({ enqueueSnackbar: jest.fn() })
}));

// Suppress repetitive act() warnings originating from async MUI input layout effects
const ACT_WARNING_SNIPPET = 'not wrapped in act';
let originalConsoleError: any;
beforeAll(() => {
  originalConsoleError = console.error;
  console.error = (...args: any[]) => {
    if (typeof args[0] === 'string' && args[0].includes(ACT_WARNING_SNIPPET)) return;
    originalConsoleError(...args);
  };
});
afterAll(() => { console.error = originalConsoleError; });

// Replaced local mock with shared utility in testUtils/fetchMocks

describe('RiskEnginePanel RTL', () => {
  beforeEach(()=>{ jest.resetAllMocks(); localStorage.setItem('auth_token','test'); });

  it('renders risk metrics and audit log row then expands', async () => {
    installRiskAuditFetchMock();
    await act(async () => {
      render(<SnackbarProvider maxSnack={3}><RiskEnginePanel /></SnackbarProvider>);
    });

    // Effective limits content
    expect(await screen.findByText(/Effective Limits/i)).toBeInTheDocument();
  // There are two panels (Effective and Base) each showing Max Position; ensure at least one rendered
  expect(screen.getAllByText(/Max Position:/i).length).toBeGreaterThanOrEqual(1);

    // Audit row appears
    expect(await screen.findByText(/order_placed/)).toBeInTheDocument();

    // Expand row
    const expandButtons = screen.getAllByLabelText(/expand audit row/i);
    fireEvent.click(expandButtons[0]);

    await waitFor(()=>{
      expect(screen.getByText(/Full Details/i)).toBeInTheDocument();
    });
  });

  it('applies search debounce and triggers fetch with query', async () => {
    const fetchSpy: string[] = [];
    // Wrap base mock to capture URLs
    installRiskAuditFetchMock({ audit: { logs: [], count: 0, pages: 1 } });
    const baseFetch = global.fetch;
  global.fetch = (jest.fn((input: any, init?: any) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/audit/recent')) fetchSpy.push(url);
      return (baseFetch as any)(input, init);
  }) as unknown) as any;

    await act(async () => {
      render(<SnackbarProvider maxSnack={2}><RiskEnginePanel /></SnackbarProvider>);
    });

    const search = await screen.findByLabelText(/Search/i);
    fireEvent.change(search, { target: { value: 'persona' } });

    // Wait longer than debounce (300ms)
    await new Promise(r=>setTimeout(r, 500));

    // Ensure at least one fetch with query param q=persona
    expect(fetchSpy.some(u=>u.includes('q=persona'))).toBeTruthy();
  });

  it('renders key sections and controls after data load', async () => {
    installRiskAuditFetchMock();
    await act(async () => {
      render(<SnackbarProvider maxSnack={2}><RiskEnginePanel /></SnackbarProvider>);
    });
    // Assert presence of core content instead of brittle snapshot
    expect(await screen.findByText(/Effective Limits/i)).toBeInTheDocument();
    expect(screen.getByText(/Base Limits/i)).toBeInTheDocument();
    expect(screen.getByText(/Live Trading Access/i)).toBeInTheDocument();
    // Pagination and search controls exist
    expect(screen.getByLabelText(/Search/i)).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: /pagination/i })).toBeInTheDocument();
  });
});
