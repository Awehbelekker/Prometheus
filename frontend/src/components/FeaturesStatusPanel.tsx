import React, { useEffect, useState } from 'react';
import { apiCall, API_ENDPOINTS } from '../config/api';

type FeatureAvail = Record<string, boolean>;

export default function FeaturesStatusPanel() {
	const [features, setFeatures] = useState<FeatureAvail>({});
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		let mounted = true;
		(async () => {
			try {
				// Endpoint path may be /api/features/availability in backend; fall back gracefully
				const data = await apiCall('/api/features/availability');
				if (mounted) {
					setFeatures(data.features || {});
					setLoading(false);
				}
			} catch (e: any) {
				if (mounted) {
					setError(e?.message || 'Failed to load features');
					setLoading(false);
				}
			}
		})();
		return () => {
			mounted = false;
		};
	}, []);

	if (loading) return <div>Loading features…</div>;
	if (error) return <div style={{ color: 'tomato' }}>Error: {error}</div>;

	const entries = Object.entries(features);
	if (!entries.length) return <div>No feature info available.</div>;

	return (
		<div style={{ padding: 12, border: '1px solid #e0e0e0', borderRadius: 8 }}>
			<h3 style={{ margin: '0 0 8px' }}>Feature availability</h3>
			<ul style={{ margin: 0, paddingLeft: 18 }}>
				{entries.map(([k, v]) => (
					<li key={k}>
						<strong>{k}:</strong> {v ? 'enabled' : 'disabled'}
					</li>
				))}
			</ul>
		</div>
	);
}

// Named export to satisfy isolatedModules and allow flexible imports
export const __FeaturesStatusPanel = FeaturesStatusPanel;
