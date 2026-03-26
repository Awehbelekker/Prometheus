import React, { useEffect, useState } from 'react';
import { Box, Typography, Alert, Button, Chip, CircularProgress } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import LockIcon from '@mui/icons-material/Lock';
import { apiCall } from '../../config/api';
interface Props { featureFlag:string; title:string; description:string; docsUrl?:string; }
interface AvailabilityDetail { available:boolean; mode:string; usage_count:number; }
export const PlaceholderPanel:React.FC<Props>=({ featureFlag,title,description,docsUrl })=>{
  const [loading,setLoading]=useState(true);
  const [detail,setDetail]=useState<AvailabilityDetail|undefined>();
  const [error,setError]=useState<string|undefined>();
  const [envMap,setEnvMap]=useState<Record<string,string[]>>({});
  useEffect(()=>{ let mounted=true; (async()=>{
    try {
      const data = await apiCall('/api/features/detail');
      if(!mounted) return; const entry = data.detail?.[title] || data.detail?.[featureFlag] || data.detail?.[title.replace(/ /g,' ')];
      if(entry) setDetail({ available: !!entry.available, mode: entry.mode, usage_count: entry.usage_count });
    } catch(e:any){ setError(e.message); } finally { if(mounted) setLoading(false); }
  })(); return ()=>{ mounted=false; }; },[featureFlag,title]);
  useEffect(()=>{ let mounted=true; (async()=>{ try { const j=await apiCall('/api/features/env-map'); if(mounted){ setEnvMap(j.shorthand||{}); } } catch{} })(); return ()=>{ mounted=false; }; },[]);
  const envFlagMap: Record<string,string> = Object.fromEntries(Object.entries(envMap).map(([k,v])=>[k, (v&&v.length? `${v[0]}=1`:'') ]));
  return (<Box sx={{ maxWidth:760 }}>
    <Typography variant="h4" gutterBottom display="flex" alignItems="center" gap={1}><AutoAwesomeIcon color="primary" />{title}</Typography>
    <Alert severity="info" sx={{ mb:3 }} icon={<LockIcon />}>
      This revolutionary capability is currently gated.
      <br/>Flag: <code>{featureFlag}</code> is disabled for this environment.
    </Alert>
    <Typography paragraph>{description}</Typography>
    <Box sx={{ display:'flex', gap:1, flexWrap:'wrap', mb:2 }}>
      {loading && <CircularProgress size={18} />}
      {!loading && detail && <Chip size="small" label={`Mode: ${detail.mode}`} />}
      {!loading && detail && <Chip size="small" label={`Usage: ${detail.usage_count}`} />}
      {error && <Chip size="small" color="error" label="Availability load error" />}
    </Box>
    <Typography paragraph variant="body2" color="text.secondary">An administrator can enable this by exporting the module & setting the corresponding environment flag, then restarting the unified server{envFlagMap[featureFlag]? ` (e.g. ${envFlagMap[featureFlag]})`:''}.</Typography>
    {docsUrl && <Button href={docsUrl} target="_blank" rel="noopener" variant="outlined">View Documentation</Button>}
  </Box>);
};
export default PlaceholderPanel;
