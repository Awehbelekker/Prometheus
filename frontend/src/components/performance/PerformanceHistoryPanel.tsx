import React, { useEffect, useMemo, useState } from 'react';
import { Box, Typography, Chip, Paper, TextField } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, Tooltip as RTooltip, ResponsiveContainer, Legend } from 'recharts';
import { useWebSocket } from '../../hooks/useWebSocket';
import { API_ENDPOINTS, getWsUrl } from '../../config/api';
interface PerfPoint { cpu:number; memory:number; disk:number; network:number; ts:string; }
interface EnrichedPoint extends PerfPoint {
  cpu_avg:number; memory_avg:number; disk_avg:number; network_norm:number; spikes:string[];
}
const MAX_POINTS = 120;
export const PerformanceHistoryPanel:React.FC=()=>{
  const { lastMessage, isConnected } = useWebSocket(getWsUrl(API_ENDPOINTS.DASHBOARD_WS), 'perf-history');
  const [points,setPoints]=useState<PerfPoint[]>([]);
  const [spikeMultiplier, setSpikeMultiplier] = useState<number>(1.5);
  const [spikeDelta, setSpikeDelta] = useState<number>(10);
  useEffect(()=>{
    if(!lastMessage) return;
    if(lastMessage.type==='performance_history' && Array.isArray(lastMessage.data)){
      setPoints(p=>{ const merged=[...p]; lastMessage.data.forEach((pt:PerfPoint)=>{ if(!merged.find(m=>m.ts===pt.ts)) merged.push(pt); }); return merged.slice(-MAX_POINTS); });
    }
    if(lastMessage.type==='performance_update' && lastMessage.data){
      const p={...lastMessage.data, ts:new Date().toISOString()};
      setPoints(ps=>{
        if(ps.length===0){
          const seedTs = new Date(Date.now()-1).toISOString();
          const seed = { ...p, ts: seedTs } as PerfPoint;
          return [seed, p];
        }
        return [...ps.slice(-(MAX_POINTS-1)), p];
      });
    }
  },[lastMessage]);
  const cpuSeries = points.map(p=>p.cpu);
  const memSeries = points.map(p=>p.memory);
  // Derive normalized network (relative to max in window) and rolling averages for smoothing
  const enriched:EnrichedPoint[] = useMemo(()=>{
    const maxNet = points.reduce((m,p)=> p.network>m? p.network:m, 0) || 1;
    const win = 5; // smoothing window
    const result = points.map((p,i)=>{
      const start = Math.max(0, i-win+1);
      const slice = points.slice(start, i+1);
      const avg = (key: keyof PerfPoint)=> slice.reduce((a,b)=> a + (b[key] as number),0)/slice.length;
  // crude spike detection (value > avg(win)*multiplier & absolute delta > spikeDelta)
      const cpu_avg_tmp = avg('cpu');
      const mem_avg_tmp = avg('memory');
      const disk_avg_tmp = avg('disk');
      const spikes: string[] = [];
  if (p.cpu > cpu_avg_tmp*spikeMultiplier && (p.cpu - cpu_avg_tmp) > spikeDelta) spikes.push('cpu');
  if (p.memory > mem_avg_tmp*spikeMultiplier && (p.memory - mem_avg_tmp) > spikeDelta) spikes.push('mem');
  if (p.disk > disk_avg_tmp*spikeMultiplier && (p.disk - disk_avg_tmp) > spikeDelta) spikes.push('disk');
      return {
        ...p,
        cpu_avg: Number(avg('cpu').toFixed(2)),
        memory_avg: Number(avg('memory').toFixed(2)),
        disk_avg: Number(avg('disk').toFixed(2)),
        network_norm: Number(((p.network/maxNet)*100).toFixed(2)),
        spikes
      };
    });
    return result;
  },[points, spikeMultiplier, spikeDelta]);
  const avg = (arr:number[])=> arr.length? (arr.reduce((a,b)=>a+b,0)/arr.length).toFixed(1):'--';
  return (<Box>
    <Typography variant="h5" gutterBottom>Realtime Performance History</Typography>
    <Box sx={{ display:'flex', gap:1, flexWrap:'wrap', mb:2 }}>
  <Chip size="small" label={`Samples ${points.length}`} />
  <span aria-live="polite" style={{ position:'absolute', width:1, height:1, overflow:'hidden', clip:'rect(1px, 1px, 1px, 1px)' }}>Total samples {points.length}</span>
      <Chip size="small" label={`CPU avg ${avg(cpuSeries)}%`} />
      <Chip size="small" label={`Mem avg ${avg(memSeries)}%`} />
      <Chip size="small" label={isConnected? 'WS Connected':'WS Disconnected'} color={isConnected? 'success':'default'} />
  <TextField size="small" label="Spike x" type="number" value={spikeMultiplier} onChange={(e:React.ChangeEvent<HTMLInputElement>)=>{ const val = parseFloat(e.target.value); setSpikeMultiplier(isNaN(val)?1.5: Math.max(1, val)); }} inputProps={{ step:0.1, min:1, style:{ width:70 } }} />
  <TextField size="small" label="Delta" type="number" value={spikeDelta} onChange={(e:React.ChangeEvent<HTMLInputElement>)=>{ const val = parseFloat(e.target.value); setSpikeDelta(isNaN(val)?10: Math.max(1, val)); }} inputProps={{ step:1, min:1, style:{ width:70 } }} />
    </Box>
    <Paper variant="outlined" sx={{ p:2, height:320, mb:2 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={enriched.slice(-MAX_POINTS)} margin={{ top:5,right:20,left:0,bottom:5 }}>
          <XAxis dataKey="ts" hide tick={false} />
          <YAxis domain={[0,100]} tick={{ fontSize:11 }} />
          <RTooltip labelStyle={{ fontSize:12 }} />
          <Legend />
          <Line type="monotone" dataKey="cpu" stroke="#ff6b35" dot={(props:any)=>{
            if(props && props.payload && Array.isArray(props.payload.spikes) && props.payload.spikes.includes('cpu')) {
              return <circle cx={props.cx} cy={props.cy} r={5} fill="#ff3b30" stroke="#fff" strokeWidth={1} />;
            }
            return <></>;
          }} strokeWidth={1} isAnimationActive={false} />
          <Line type="monotone" dataKey="cpu_avg" stroke="#ff9e68" dot={false} strokeWidth={2} isAnimationActive={false} name="cpu (avg)" />
          <Line type="monotone" dataKey="memory" stroke="#00d4ff" dot={(props:any)=>{
            if(props && props.payload && Array.isArray(props.payload.spikes) && props.payload.spikes.includes('mem')) {
              return <circle cx={props.cx} cy={props.cy} r={5} fill="#007aff" stroke="#fff" strokeWidth={1} />;
            }
            return <></>;
          }} strokeWidth={1} isAnimationActive={false} />
          <Line type="monotone" dataKey="memory_avg" stroke="#5dffff" dot={false} strokeWidth={2} isAnimationActive={false} name="mem (avg)" />
          <Line type="monotone" dataKey="disk" stroke="#c084fc" dot={(props:any)=>{
            if(props && props.payload && Array.isArray(props.payload.spikes) && props.payload.spikes.includes('disk')) {
              return <circle cx={props.cx} cy={props.cy} r={5} fill="#9d4edd" stroke="#fff" strokeWidth={1} />;
            }
            return <></>;
          }} strokeWidth={1} isAnimationActive={false} />
          <Line type="monotone" dataKey="network_norm" stroke="#22c55e" dot={false} strokeWidth={1} isAnimationActive={false} name="net %" />
        </LineChart>
      </ResponsiveContainer>
    </Paper>
    <Paper variant="outlined" sx={{ p:2, height:180, overflow:'auto', fontFamily:'monospace', fontSize:12 }}>
      {enriched.slice(-40).map((p, idx)=> <div key={`${p.ts}-${idx}`}>{p.ts} | cpu {p.cpu}% mem {p.memory}% disk {p.disk}% net {p.network}{p.spikes.length? `  SPIKES:${p.spikes.join(',')}`:''}</div>)}
    </Paper>
  </Box>);
};
export default PerformanceHistoryPanel;
