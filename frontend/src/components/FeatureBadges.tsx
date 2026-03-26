import React, { useEffect, useState } from 'react';
import { useFeatureAvailability } from '../hooks/useFeatureAvailability';
import './FeatureBadges.css';

const MODE_COLORS: Record<string,string> = {
  active: '#2e7d32',
  fallback: '#ed6c02',
  missing: '#9e9e9e'
};

export const FeatureBadges: React.FC = () => {
  const { data, detail, loading, error, reload } = useFeatureAvailability(60000);
  const [lazyDetail, setLazyDetail] = useState<typeof detail | null>(null);

  useEffect(() => {
    let timeout: any;
    if (!lazyDetail && !detail) {
      timeout = setTimeout(() => {
        // Trigger explicit reload to ensure detail fetched (hook already does parallel fetch)
        reload();
      }, 1500); // defer detail fetch to allow main dashboard to load first
    }
    if (detail) setLazyDetail(detail);
    return () => timeout && clearTimeout(timeout);
  }, [detail, lazyDetail, reload]);

  const featureDetail = lazyDetail || detail; 

  if (loading && !data) return <div className="feature-badges loading">Loading features...</div>;
  if (error) return <div className="feature-badges error">Feature load error: {error} <button onClick={reload}>Retry</button></div>;

  const modes = data?.feature_modes || {};
  const list = Object.keys(featureDetail?.detail || data?.features || {}).sort();

  return (
    <div className="feature-badges">
      <h4>Platform Features</h4>
      <div className="badges-container">
        {list.map(name => {
          const available = featureDetail?.detail?.[name]?.available ?? data?.features?.[name];
          const mode = featureDetail?.detail?.[name]?.mode || modes[name] || (available ? 'active' : 'missing');
          const usage = featureDetail?.detail?.[name]?.usage_count;
          return (
            <div key={name} className={`feature-badge mode-${mode}`}
              style={{ borderColor: MODE_COLORS[mode] || '#555' }}
              title={`Mode: ${mode}${usage !== undefined ? ` | Usage: ${usage}` : ''}`}
            >
              <span className="name">{name}</span>
              <span className="mode" style={{ background: MODE_COLORS[mode] || '#555' }}>{mode}</span>
              {usage !== undefined && <span className="usage">{usage}</span>}
            </div>
          );
        })}
      </div>
      {data?.fallback?.length ? (
        <div className="fallback-note">Fallback: {data.fallback.join(', ')}</div>
      ) : null}
    </div>
  );
};

export default FeatureBadges;
