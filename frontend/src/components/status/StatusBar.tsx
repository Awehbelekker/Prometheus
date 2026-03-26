import React, { useEffect, useState } from 'react';
import { Box, Chip, Tooltip, IconButton } from '@mui/material';
import WifiIcon from '@mui/icons-material/Wifi';
import WifiOffIcon from '@mui/icons-material/WifiOff';
import QueryStatsIcon from '@mui/icons-material/QueryStats';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import KeyboardCommandKeyIcon from '@mui/icons-material/KeyboardCommandKey';
import { getApiUrl } from '../../config/api';
import { getJsonWithRetry } from '../../utils/network';

interface StatusMetrics { latencyMs:number|null; lastPriceTs:number|null; system:'online'|'offline'|'degraded'; cpu?:number; mem?:number; disk?:number; net?:number; }
interface Props { currentPanel:string; onOpenPalette:()=>void; }
import { useWebSocket } from '../../hooks/useWebSocket';
import { getWsUrl, API_ENDPOINTS } from '../../config/api';
const StatusBar:React.FC<Props>=({ currentPanel,onOpenPalette })=>{
  const [metrics,setMetrics]=useState<StatusMetrics>({ latencyMs:null, lastPriceTs:null, system:'offline' });
  const [pinging,setPinging]=useState(false);
  const { lastMessage, isConnected } = useWebSocket(getWsUrl(API_ENDPOINTS.DASHBOARD_WS), 'status-bar');
  useEffect(()=>{ if(!lastMessage) return; try { if(lastMessage.type==='performance_update' && lastMessage.data){ const { cpu, memory, disk, network } = lastMessage.data; setMetrics(m=>({ ...m, cpu, mem: memory, disk, net: network })); } if(lastMessage.type==='status_update'){ setMetrics(m=>({ ...m, system:'online' })); } } catch(e){ /* ignore */ } },[lastMessage]);
  const ping=async()=>{ try { setPinging(true); const start=performance.now(); await getJsonWithRetry(getApiUrl(API_ENDPOINTS.STATUS), {}, { retries: 3, backoffMs: 400, maxBackoffMs: 4000, timeoutMs: 5000 }); const ms=Math.round(performance.now()-start); setMetrics(m=>({ ...m, latencyMs: ms, system: 'online' })); } catch { setMetrics(m=>({ ...m, system:'offline' })); } finally { setPinging(false); } };
  useEffect(()=>{ ping(); const id=setInterval(ping,30000); return ()=>clearInterval(id); },[]);
  return (<Box sx={{ display:'flex', alignItems:'center', gap:1 }}>
    <Tooltip title={`System ${metrics.system}${isConnected? ' (WS)': ' (no WS)'}`}><span><Chip size='small' color={metrics.system==='online'?'success': metrics.system==='degraded'?'warning':'error'} label={metrics.system+(isConnected?'':'*')} /></span></Tooltip>
    <Tooltip title={metrics.latencyMs!=null? `API latency ${metrics.latencyMs}ms`:'Latency unknown'}>
      <Chip size='small' icon={<QueryStatsIcon />} label={metrics.latencyMs!=null? `${metrics.latencyMs}ms`:'--'} variant='outlined' />
    </Tooltip>
    {metrics.cpu!=null && (
      <Tooltip title='CPU usage'><span><Chip size='small' label={`CPU ${metrics.cpu}%`} variant='outlined' /></span></Tooltip>
    )}
    {metrics.mem!=null && (
      <Tooltip title='Memory usage'><span><Chip size='small' label={`Mem ${metrics.mem}%`} variant='outlined' /></span></Tooltip>
    )}
    {metrics.disk!=null && (
      <Tooltip title='Disk usage'><span><Chip size='small' label={`Disk ${metrics.disk}%`} variant='outlined' /></span></Tooltip>
    )}
    {metrics.net!=null && (
      <Tooltip title='Network throughput (arb)'><span><Chip size='small' label={`Net ${metrics.net}%`} variant='outlined' /></span></Tooltip>
    )}
    <Tooltip title='Command Palette (Ctrl/Cmd+K)'>
      <IconButton size='small' onClick={onOpenPalette}><KeyboardCommandKeyIcon fontSize='small' /></IconButton>
    </Tooltip>
    <Tooltip title='Manual ping'><span><IconButton size='small' disabled={pinging} onClick={ping}>{metrics.system==='offline'? <WifiOffIcon fontSize='small' />:<WifiIcon fontSize='small' />}</IconButton></span></Tooltip>
    <Tooltip title='Current panel'>
      <span><Chip size='small' icon={<AccessTimeIcon />} label={currentPanel} /></span>
    </Tooltip>
  </Box>);
};
export default StatusBar;
