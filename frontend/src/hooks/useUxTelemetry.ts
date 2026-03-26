import { useEffect, useRef } from 'react';
import { getApiUrl } from '../config/api';
import { fetchWithRetry } from '../utils/network';
interface TelemetryEvent { type:string; ts:number; data?:Record<string,any>; }
interface Options { flushIntervalMs?:number; endpoint?:string; enabled?:boolean; }
export function useUxTelemetry(o:Options={}){
  const { flushIntervalMs=15000, endpoint='/api/ux/telemetry', enabled=true }=o;
  const endpointUrl = endpoint.startsWith('http') ? endpoint : getApiUrl(endpoint);
  const buf=useRef<TelemetryEvent[]>([]);
  const tti=useRef(false);
  
  useEffect(()=>{
    if(!enabled) return;
    const start=performance.now();
    const mark=()=>{
      if(tti.current) return;
      tti.current=true;
      buf.current.push({ type:'time_to_interactive', ts:Date.now(), data:{ ms: performance.now()-start } });
    };
    if('requestIdleCallback' in window){ (window as any).requestIdleCallback(mark,{timeout:3000}); } else setTimeout(mark,1200);
  },[enabled]);
  
  useEffect(()=>{
    if(!enabled) return;
    const id=setInterval(()=>{
      if(!buf.current.length) return;
      const payload=buf.current.splice(0,buf.current.length);
      fetchWithRetry(endpointUrl,{ method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ events: payload }) },{ retries:2, backoffMs:300, maxBackoffMs:2000, timeoutMs:3000 }).catch(()=>{});
      if(process.env.NODE_ENV!=='production') console.log('[UX Telemetry]',payload);
    },flushIntervalMs);
    return ()=>clearInterval(id);
  },[endpointUrl,flushIntervalMs,enabled]);
  
  const track=(type:string,data?:Record<string,any>)=>{ if(!enabled) return; buf.current.push({ type, data, ts:Date.now() }); };
  return { track };
}
