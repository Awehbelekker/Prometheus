// Shared fetch mock utilities for frontend tests
// Provides deterministic timestamps and helpers for common API patterns

export const FIXED_TS = '2024-01-01T00:00:00.000Z';

export interface RiskProfile {
  user_id: string;
  persona: string | null;
  persona_parameters: any;
  base_risk: any;
  effective_risk: any;
  risk_multiplier: number;
  position_size_pct: number;
  live_trading_enabled_global: boolean;
  live_trading_admin_allowed: boolean;
  timestamp: string;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  user_id: string;
  action: string;
  details: string;
  level: string;
  extra?: any;
}

export interface AuditResponse {
  logs: AuditLogEntry[];
  count: number;
  pages: number;
}

export const buildDefaultRiskProfile = (overrides: Partial<RiskProfile> = {}): RiskProfile => ({
  user_id: '2',
  persona: 'balanced_hrm',
  persona_parameters: { risk_multiplier: 1.0 },
  base_risk: { max_position_size: 10000, max_daily_loss: 5000, max_leverage: 2 },
  effective_risk: { max_position_size: 10000, max_daily_loss: 5000, max_leverage: 2 },
  risk_multiplier: 1.0,
  position_size_pct: 0.02,
  live_trading_enabled_global: false,
  live_trading_admin_allowed: false,
  timestamp: FIXED_TS,
  ...overrides,
});

export const buildDefaultAuditResponse = (overrides: Partial<AuditResponse> = {}): AuditResponse => ({
  logs: [
    { id: '1', timestamp: FIXED_TS, user_id: '2', action: 'order_placed', details: 'symbol=AAPL side=buy qty=5 mode=paper', level: 'info', extra: { persona: 'balanced_hrm', risk_multiplier: 1.0 } }
  ],
  count: 1,
  pages: 1,
  ...overrides,
});

export const installRiskAuditFetchMock = (opts: { profile?: Partial<RiskProfile>; audit?: Partial<AuditResponse> } = {}) => {
  const profile = buildDefaultRiskProfile(opts.profile);
  const audit = buildDefaultAuditResponse(opts.audit);

  global.fetch = jest.fn((input: RequestInfo) => {
    const url = typeof input === 'string' ? input : input.toString();
    if (url.includes('/api/risk/profile')) {
      return Promise.resolve(new Response(JSON.stringify(profile), { status: 200 }));
    }
    if (url.includes('/api/audit/recent')) {
      return Promise.resolve(new Response(JSON.stringify(audit), { status: 200 }));
    }
    if (url.includes('/api/audit/export')) {
      return Promise.resolve(new Response(JSON.stringify([]), { status: 200 }));
    }
    return Promise.resolve(new Response('not found', { status: 404 }));
  }) as any;
};

export const captureFetchUrls = (): string[] => {
  const urls: string[] = [];
  const orig = global.fetch;
  global.fetch = jest.fn((input: RequestInfo, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input.toString();
    urls.push(url);
    return (orig as any)(input, init);
  }) as any;
  return urls;
};
