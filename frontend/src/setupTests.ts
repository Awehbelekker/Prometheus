// Jest setup file for React Testing Library
import '@testing-library/jest-dom';

// Central console interception: fail tests on unexpected console.error, filter known noisy warnings
const allowedErrorSubstrings = [
	'not wrapped in act', // React act warnings (handled separately in specific tests)
	'React Router Future Flag Warning' // deprecation/future notices
];

const allowedWarnSubstrings = [
	'React Router Future Flag Warning'
];

let currentTestErrors: string[] = [];
let originalConsoleError = console.error;
let originalConsoleWarn = console.warn;

console.error = (...args: any[]) => {
	try {
		const msg = args && args[0] ? String(args[0]) : '';
		if (!allowedErrorSubstrings.some(s => msg.includes(s))) {
			currentTestErrors.push(msg);
		}
	} catch { /* ignore meta errors */ }
	return originalConsoleError.apply(console, args as any);
};

console.warn = (...args: any[]) => {
	try {
		const msg = args && args[0] ? String(args[0]) : '';
		if (allowedWarnSubstrings.some(s => msg.includes(s))) {
			return; // swallow known future flag warnings to keep output clean
		}
	} catch { /* ignore */ }
	return originalConsoleWarn.apply(console, args as any);
};

afterEach(() => {
	if (currentTestErrors.length) {
		const unique = Array.from(new Set(currentTestErrors));
		currentTestErrors = [];
		throw new Error('Unexpected console.error calls:\n' + unique.join('\n'));
	}
	currentTestErrors = [];
});

// ------- jsdom browser polyfills/mocks -------
// ResizeObserver (used by recharts ResponsiveContainer)
class MockResizeObserver {
	observe() {/* noop */}
	unobserve() {/* noop */}
	disconnect() {/* noop */}
}
// @ts-ignore
if (typeof (global as any).ResizeObserver === 'undefined') {
	// @ts-ignore
	(global as any).ResizeObserver = MockResizeObserver;
}

// matchMedia (used by animation prefs and MUI)
// @ts-ignore
if (typeof (window as any).matchMedia !== 'function') {
	// @ts-ignore
	(window as any).matchMedia = (query: string) => ({
		matches: false,
		media: query,
		onchange: null,
		addListener: () => {}, // deprecated
		removeListener: () => {}, // deprecated
		addEventListener: () => {},
		removeEventListener: () => {},
		dispatchEvent: () => false,
	});
}

// Safe default fetch mock so providers that auto-fetch don't crash in tests that didn't mock fetch
// Individual tests can override this via global.fetch = jest.fn()...
// @ts-ignore
if (typeof (global as any).fetch !== 'function') {
	// @ts-ignore
	(global as any).fetch = jest.fn().mockResolvedValue({
		ok: true,
		json: async () => ({ flags: [], revolutionary_enabled: false }),
	});
}

