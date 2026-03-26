import React, { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react';
import { getApiUrl, API_ENDPOINTS } from '../config/api';
import { getJsonWithRetry } from '../utils/network';

/**
 * User / Feature Flags Context
 * - Fetches server authoritative feature flags
 * - Provides helper to test if a flag is enabled
 * NOTE: We purposely do NOT verify the HMAC signature client‑side to avoid embedding secrets.
 *       The signature presence + short expiry offers replay mitigation; server remains source of truth.
 */
interface FeatureFlagsState {
	flags: Set<string>;
	revolutionaryEnabled: boolean;
	loading: boolean;
	lastUpdated?: number;
	refresh: () => Promise<void>;
	has: (flag: string) => boolean;
}

const FeatureFlagsContext = createContext<FeatureFlagsState | undefined>(undefined);

export const FeatureFlagsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const [flags, setFlags] = useState<Set<string>>(new Set());
	const [revolutionaryEnabled, setRevolutionaryEnabled] = useState(false);
	const [loading, setLoading] = useState(true);
	const [lastUpdated, setLastUpdated] = useState<number | undefined>(undefined);

	const load = useCallback(async () => {
		setLoading(true);
		try {
			const data = await getJsonWithRetry<any>(getApiUrl(API_ENDPOINTS.FEATURE_FLAGS), {}, { retries: 3, backoffMs: 400, maxBackoffMs: 4000, timeoutMs: 6000 });
			const list: string[] = Array.isArray(data.flags) ? data.flags : [];
			setFlags(new Set(list));
			setRevolutionaryEnabled(!!data.revolutionary_enabled);
			setLastUpdated(Date.now());
		} catch (e) {
			// Non-fatal: keep previous flags
			console.warn('Feature flags load error', e);
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		load();
		const id = setInterval(load, 240000); // refresh every 4 minutes (expiry is 5m)
		return () => clearInterval(id);
	}, [load]);

	const has = useCallback((flag: string) => flags.has(flag), [flags]);

	return (
		<FeatureFlagsContext.Provider value={{ flags, revolutionaryEnabled, loading, lastUpdated, refresh: load, has }}>
			{children}
		</FeatureFlagsContext.Provider>
	);
};

export function useFeatureFlags() {
	const ctx = useContext(FeatureFlagsContext);
	if (!ctx) throw new Error('useFeatureFlags must be used within FeatureFlagsProvider');
	return ctx;
}

// --------------------
// Lightweight User Context expected by components
// --------------------
interface UserMeta { investment_amount?: number; currency?: string }
interface UserCtxState {
	currentUser: { role: string } | null;
	userMeta: UserMeta;
	loading: boolean;
	error: string | null;
	featuresEnabled: string[];
	activePersona?: string;
	personaParameters?: Record<string, any>;
	setInvestment: (amt: number, currency: string) => Promise<void>;
	applyPersona: (persona: string) => Promise<boolean>;
}

const UserContext = createContext<UserCtxState | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const [currentUser, setCurrentUser] = useState<{ role: string } | null>(() => {
		try {
			const userData = localStorage.getItem('userData');
			if (userData) {
				const parsed = JSON.parse(userData);
				return { role: parsed.role || 'user' };
			}
		} catch {}
		return { role: 'user' };
	});
	const [userMeta, setUserMeta] = useState<UserMeta>({});
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [activePersona, setActivePersona] = useState<string | undefined>(undefined);
	const [personaParameters, setPersonaParameters] = useState<Record<string, any> | undefined>(undefined);

	// Bridge flags into simple array for legacy components
	const { flags } = useFeatureFlags();
	const featuresEnabled = useMemo(() => Array.from(flags.values()), [flags]);

	const setInvestment = useCallback(async (amt: number, currency: string) => {
		setLoading(true); setError(null);
		try {
			// Persist locally for demo; in prod call API
			setUserMeta({ investment_amount: amt, currency });
			try { localStorage.setItem('user_investment', JSON.stringify({ amt, currency })); } catch {}
		} catch (e:any) {
			setError(e?.message || 'Failed to set investment');
		} finally { setLoading(false); }
	}, []);

	const applyPersona = useCallback(async (persona: string) => {
		try {
			// Call backend persona apply if available; otherwise simulate
			setActivePersona(persona);
			const defaults: Record<string, any> = {
				risk_multiplier: persona.includes('aggressive') ? 1.5 : persona.includes('conservative') ? 0.7 : 1,
				position_size_pct: persona.includes('aggressive') ? 0.15 : 0.05,
				hold_hours: persona.includes('arbitrage') ? 2 : 8,
			};
			setPersonaParameters(defaults);
			return true;
		} catch { return false; }
	}, []);

	useEffect(() => {
		// Load persisted investment
		try {
			const raw = localStorage.getItem('user_investment');
			if (raw) {
				const { amt, currency } = JSON.parse(raw);
				setUserMeta({ investment_amount: amt, currency });
			}
		} catch {}
	}, []);

	const value: UserCtxState = {
		currentUser,
		userMeta,
		loading,
		error,
		featuresEnabled,
		activePersona,
		personaParameters,
		setInvestment,
		applyPersona,
	};

	return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

export function useUserContext() {
	const ctx = useContext(UserContext);
	if (!ctx) throw new Error('useUserContext must be used within UserProvider');
	return ctx;
}

// Back-compat named re-exports for consumers
export { UserProvider as default };

