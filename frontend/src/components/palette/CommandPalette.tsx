import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Dialog, DialogContent, TextField, List, ListItemButton, ListItemText, Chip, Box } from '@mui/material';

interface Item { id:string; label:string; keywords?:string[]; group?:string; }
interface Props { open:boolean; onClose:()=>void; onSelect:(id:string)=>void; items?:Item[]; }
const defaultItems:Item[]=[
  { id:'dashboard', label:'Dashboard', keywords:['home','main'], group:'Navigation' },
  { id:'settings', label:'Settings', keywords:['preferences'], group:'Navigation' },
  { id:'risk-engine', label:'Risk Engine', keywords:['risk','limits'], group:'Panels' },
  { id:'agents', label:'Agents', keywords:['bots'], group:'Panels' }
];
function fuzzyScore(q:string, text:string){ if(!q) return 1; q=q.toLowerCase(); text=text.toLowerCase(); let qi=0; let score=0; for(let i=0;i<text.length && qi<q.length;i++){ if(text[i]===q[qi]){ score+=2; qi++; } else score--; } return qi===q.length? score - (text.length - q.length): -Infinity; }
const CommandPalette:React.FC<Props>=({ open,onClose,onSelect, items })=>{ const [query,setQuery]=useState(''); const inputRef=useRef<HTMLInputElement|null>(null); const list = items?.length? items: defaultItems; const results=useMemo(()=> list.map(i=>({ item:i, score: Math.max( fuzzyScore(query,i.label), ...(i.keywords||[]).map(k=>fuzzyScore(query,k)) ) })).filter(r=> r.score>-Infinity/2).sort((a,b)=> b.score-a.score).slice(0,20), [query,list]); useEffect(()=>{ if(open){ setQuery(''); setTimeout(()=> inputRef.current?.focus(), 50); } },[open]); const handleKey=(e:React.KeyboardEvent)=>{ if(e.key==='Escape'){ onClose(); } }; return (<Dialog open={open} onClose={onClose} fullWidth maxWidth='sm' onKeyDown={handleKey} aria-labelledby='command-palette-title'> <DialogContent sx={{ pt:3 }}> <TextField inputRef={inputRef} fullWidth placeholder='Type a command or panel…' value={query} onChange={e=>setQuery(e.target.value)} autoFocus /> <List dense sx={{ maxHeight:300, overflow:'auto' }}> {results.map(r=> <ListItemButton key={r.item.id} onClick={()=>{ onSelect(r.item.id); }}><ListItemText primary={<Box sx={{ display:'flex', alignItems:'center', gap:1 }}><span>{r.item.label}</span>{r.item.group && <Chip size='small' label={r.item.group} />}</Box>} /></ListItemButton>)} {results.length===0 && <Box sx={{ px:2, py:3, textAlign:'center', fontSize:12, color:'text.secondary' }}>No matches</Box>} </List> </DialogContent> </Dialog>); };
export default CommandPalette;
