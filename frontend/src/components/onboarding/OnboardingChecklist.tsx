import React, { useState } from 'react';
import { Card, CardHeader, CardContent, List, ListItem, ListItemIcon, ListItemText, Checkbox, Button, Collapse, Box, IconButton, Tooltip } from '@mui/material';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import CloseIcon from '@mui/icons-material/Close';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

interface Step { id:string; label:string; description?:string; }
const steps:Step[]=[
  { id:'connect_broker', label:'Connect Broker Account' },
  { id:'select_persona', label:'Select Trading Persona' },
  { id:'review_risk', label:'Review Risk Limits' },
  { id:'run_sim', label:'Run Simulation' },
  { id:'start_trial', label:'Start 48h Trial' }
];
interface Props { onComplete:()=>void; onDismiss:()=>void; }
const OnboardingChecklist:React.FC<Props>=({ onComplete, onDismiss })=>{
  const [open,setOpen]=useState(true);
  const [done,setDone]=useState<Record<string,boolean>>(()=>{ try{ const raw=localStorage.getItem('onboarding_progress'); return raw? JSON.parse(raw): {}; }catch{return{};} });
  const toggle=(id:string)=>{ setDone(d=>{ const next={ ...d, [id]: !d[id] }; try{ localStorage.setItem('onboarding_progress', JSON.stringify(next)); }catch{} if(steps.every(s=> next[s.id])) onComplete(); return next; }); };
  return (<Card sx={{ mb:3, border:'1px solid', borderColor:'divider', position:'relative' }}>
    <CardHeader avatar={<RocketLaunchIcon color='primary' />} title='Quick Start Checklist' subheader='Complete these steps to unlock full trading workflow' action={<Box>
      <Tooltip title={open? 'Collapse':'Expand'}><IconButton size='small' onClick={()=>setOpen(o=>!o)}>{open? <ExpandLessIcon />:<ExpandMoreIcon />}</IconButton></Tooltip>
      <Tooltip title='Dismiss'><IconButton size='small' onClick={onDismiss}><CloseIcon /></IconButton></Tooltip>
    </Box>} />
    <Collapse in={open} timeout={300}>
      <CardContent sx={{ pt:0 }}>
        <List dense>
          {steps.map(s=>(<ListItem key={s.id} disableGutters secondaryAction={<Checkbox edge='end' checked={!!done[s.id]} onChange={()=>toggle(s.id)} />}> <ListItemIcon><Checkbox tabIndex={-1} disableRipple checked={!!done[s.id]} onChange={()=>toggle(s.id)} /></ListItemIcon><ListItemText primary={s.label} /> </ListItem>))}
        </List>
        <Button variant='contained' fullWidth disabled={!steps.every(s=> done[s.id])} onClick={onComplete}>Finish</Button>
      </CardContent>
    </Collapse>
  </Card>);
};
export default OnboardingChecklist;
