import React from 'react';
import { useFeatureAvailability } from '../hooks/useFeatureAvailability';

export const AdminFeatureBadges: React.FC = () => {
  const { data, error, loading, reload } = useFeatureAvailability(60000);

  if (loading) return <div>Loading feature availability...</div>;
  if (error) return <div style={{color:'red'}}>Feature availability error: {error}</div>;
  if (!data) return <div>No feature data.</div>;

  return (
    <div style={{border:'1px solid #333', padding:12, borderRadius:8}}>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <h3 style={{margin:0}}>Revolutionary Feature Availability</h3>
        <button onClick={reload} style={{padding:'4px 10px'}}>Refresh</button>
      </div>
      <p style={{margin:'4px 0 12px 0', fontSize:12}}>Generated: {new Date(data.generated_at).toLocaleString()} | Missing: {data.missing.length}</p>
      <div style={{display:'flex', flexWrap:'wrap', gap:8}}>
        {Object.entries(data.features).map(([name, available]) => (
          <span key={name} style={{
            padding:'4px 8px',
            borderRadius:12,
            fontSize:12,
            background: available ? 'linear-gradient(90deg,#0f9d58,#34a853)' : 'linear-gradient(90deg,#b00020,#d32f2f)',
            color:'#fff',
            boxShadow:'0 1px 3px rgba(0,0,0,0.3)'
          }} title={available ? 'Available' : 'Unavailable'}>
            {available ? '✓' : '✕'} {name}
          </span>
        ))}
      </div>
      {data.missing.length > 0 && (
        <details style={{marginTop:12}}>
          <summary style={{cursor:'pointer'}}>Missing Feature Guidance</summary>
          <p style={{fontSize:12, lineHeight:1.4}}>{data.notes}</p>
        </details>
      )}
    </div>
  );
};

export default AdminFeatureBadges;
