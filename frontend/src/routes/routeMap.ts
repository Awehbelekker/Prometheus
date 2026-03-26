// Central route / panel catalog so sidebar + palette consume a single source.
// Each entry can optionally declare a required feature flag.
import React from 'react';

export interface RouteDescriptor {
	id: string;
	label: string;
	group: 'core' | 'standard' | 'revolutionary' | 'panels' | 'user' | 'trading' | 'admin' | string;
	featureFlag?: string; // server-provided flag name
	keywords?: string[];
	badge?: string;
}

export const routes: RouteDescriptor[] = [
	{ id: 'dashboard', label: 'Dashboard', group: 'core', keywords: ['home', 'main'] },
	{ id: 'settings', label: 'Settings', group: 'standard', keywords: ['preferences'] },
	{ id: 'analytics', label: 'Analytics', group: 'panels', keywords: ['metrics','charts'] },
	{ id: 'live-trading', label: 'Live Trading', group: 'trading', keywords: ['trading','orders'] },
	{ id: 'hrm-dashboard', label: 'HRM Dashboard', group: 'panels', keywords: ['hrm','human resources'] },
	{ id: 'user-dashboard', label: 'User Dashboard', group: 'user', keywords: ['profile','portfolio'] },
	// Revolutionary showcase panels (gated)
	{ id: 'holographic-ui', label: 'Holographic UI', group: 'revolutionary', featureFlag: 'holographic_ui', badge: 'REV', keywords: ['holo','3d'] },
	{ id: 'quantum-trading', label: 'Quantum Trading', group: 'revolutionary', featureFlag: 'quantum_trading', badge: 'REV', keywords: ['quantum','q'] },
	{ id: 'predictive-oracle', label: 'Predictive Oracle', group: 'revolutionary', featureFlag: 'predictive_oracle', badge: 'REV', keywords: ['oracle','predict'] },
	{ id: 'nanosecond-exec', label: 'Nanosecond Execution', group: 'revolutionary', featureFlag: 'nanosecond_execution', badge: 'REV', keywords: ['nano','speed'] },
	{ id: 'hierarchical-agents', label: 'Hierarchical Agents', group: 'revolutionary', featureFlag: 'hierarchical_agents', badge: 'REV', keywords: ['agents','hierarchy'] },
	{ id: 'multi-agent-orchestrator', label: 'Multi-Agent Orchestrator', group: 'revolutionary', featureFlag: 'multi_agent_orchestrator', badge: 'REV', keywords: ['orchestrator','agents'] },
	// Additional panels (examples)
	{ id: 'risk-engine', label: 'Risk Engine', group: 'panels', keywords: ['risk','limits'] },
	{ id: 'agents', label: 'Agents', group: 'panels', keywords: ['bots'] },
	{ id: 'performance-history', label: 'Performance History', group: 'panels', keywords: ['performance','metrics','history'], featureFlag: 'performance_metrics' }
];

export function visibleRoutes(has: (flag: string) => boolean) {
	return routes.filter(r => !r.featureFlag || has(r.featureFlag));
}

// Central icon registry so components can map id->icon without duplicating imports.
import DashboardIcon from '@mui/icons-material/Dashboard';
import SettingsIcon from '@mui/icons-material/Settings';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import TimelineIcon from '@mui/icons-material/Timeline';
import BuildIcon from '@mui/icons-material/Build';
import AssessmentIcon from '@mui/icons-material/Assessment';

export const routeIcons: Record<string, any> = {
	dashboard: DashboardIcon,
	settings: SettingsIcon,
	analytics: AssessmentIcon,
	'live-trading': TimelineIcon,
	'hrm-dashboard': TimelineIcon,
	'user-dashboard': DashboardIcon,
	'holographic-ui': AutoAwesomeIcon,
	'quantum-trading': AutoAwesomeIcon,
	'predictive-oracle': AutoAwesomeIcon,
	'nanosecond-exec': AutoAwesomeIcon,
	'hierarchical-agents': BuildIcon,
	'multi-agent-orchestrator': BuildIcon,
	'risk-engine': TimelineIcon,
	agents: BuildIcon,
	performance: AssessmentIcon
};

export function getRouteIcon(id: string) { return routeIcons[id]; }

// Extended route map consumed by Sidebar/MainContent
export interface FullRouteEntry {
	id: string;
	title: string;
	group?: string;
	badge?: string;
	featureFlag?: string;
	roles?: string[];
	lazy?: React.LazyExoticComponent<any>;
}

// Helper to safely lazy-load known components
const lazy = (importer: () => Promise<{ default: any }>) => React.lazy(importer);

export const ROUTE_MAP: FullRouteEntry[] = [
	{ id: 'dashboard', title: 'Dashboard', group: 'core', lazy: lazy(() => import('../components/Dashboard')) },
	{ id: 'analytics', title: 'Analytics', group: 'panels', lazy: lazy(() => import('../components/EnhancedAnalyticsDashboard')) },
	{ id: 'live-trading', title: 'Live Trading', group: 'trading', roles: ['admin','trader','user'], lazy: lazy(() => import('../components/TradingDashboard')) },
	{ id: 'live-market', title: 'Live Market', group: 'trading', roles: ['admin','trader','user'], lazy: lazy(() => import('../components/LiveMarketDashboard')) },
	{ id: 'hrm-dashboard', title: 'HRM Dashboard', group: 'panels', lazy: lazy(() => import('../components/HRMDashboard')) },
	{ id: 'user-dashboard', title: 'User Dashboard', group: 'user', lazy: lazy(() => import('../components/UserDashboard')) },
	{ id: 'settings', title: 'Settings', group: 'standard', lazy: lazy(() => import('../components/EnhancedForms')) },
	// Revolutionary placeholders (gate behind flags)
	{ id: 'holographic-ui', title: 'Holographic UI', group: 'revolutionary', badge: 'REV', featureFlag: 'holographic_ui', lazy: lazy(() => import('../components/EnhancedHolographicUI')) },
	{ id: 'predictive-oracle', title: 'Predictive Oracle', group: 'revolutionary', badge: 'REV', featureFlag: 'predictive_oracle', lazy: lazy(() => import('../components/PredictiveMarketOracle')) },
];

export const ROUTES_BY_ID: Record<string, FullRouteEntry> = ROUTE_MAP.reduce((acc, r) => {
	acc[r.id] = r;
	return acc;
}, {} as Record<string, FullRouteEntry>);

