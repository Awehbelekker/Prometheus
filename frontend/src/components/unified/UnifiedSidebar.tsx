import React, { useMemo, useState } from 'react';
import { Box, List, ListItemButton, ListItemIcon, ListItemText, Collapse, Chip, Tooltip, IconButton, CircularProgress } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import { tokens } from '../../design/tokens';
import { animation, prefersReducedMotion } from '../../design/animation';
import { useFeatureFlags } from '../../context/UserContext';
import { visibleRoutes, getRouteIcon } from '../../routes/routeMap';

export interface UnifiedSidebarProps { selected:string; onSelect:(id:string)=>void; variant?:'legacy'|'modern'|'auto'; }

const groupPriority=['core','revolutionary','standard','panels'];

// Icon mapping now centralized in routeMap (fallback to DashboardIcon)

const UnifiedSidebar:React.FC<UnifiedSidebarProps>=({ selected,onSelect,variant='auto' })=>{ 
	const [collapsed,setCollapsed]=useState(false); 
	const [openGroups,setOpen]=useState<Record<string,boolean>>({ core:true, revolutionary:true, standard:true, panels:true });
	const { has, loading } = useFeatureFlags();
	const items = useMemo(()=> visibleRoutes(has), [has]);
	const grouped=useMemo(()=>{ const map:Record<string,typeof items>={}; items.forEach(i=>{ const g=i.group||'other'; if(!map[g]) map[g]=[]; map[g].push(i); }); return map; },[items]); 
		const sortedGroups = Array.from(new Set(Object.keys(grouped))).sort((a,b)=> groupPriority.indexOf(a) - groupPriority.indexOf(b));
	const toggleGroup=(g:string)=> setOpen(o=>({ ...o, [g]: !o[g] })); 
	return (<Box component="nav" role="navigation" aria-label="Primary" sx={{ width: collapsed? tokens.layout.sidebarCollapsed: tokens.layout.sidebarWidth, backgroundColor:'#1a1a1a', color:'#fff', borderRight:'1px solid #333', display:'flex', flexDirection:'column', transition: prefersReducedMotion()? 'none' : `width ${animation.durations.normal}ms ${animation.easing.standard}` }}>
		<Box sx={{ display:'flex', alignItems:'center', justifyContent: collapsed? 'center':'space-between', px:2, py:1.5, borderBottom:'1px solid #333' }}>
			{!collapsed && <Box sx={{ fontWeight:700, fontSize:'0.95rem', background:'linear-gradient(45deg,#00d4ff,#ff6b35)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent' }}>PROMETHEUS</Box>}
			<Tooltip title={collapsed? 'Expand sidebar':'Collapse sidebar'}><IconButton size="small" onClick={()=>setCollapsed(c=>!c)} sx={{ color:'#00d4ff' }} aria-label="Toggle sidebar">{collapsed? <MenuIcon />:<ChevronLeftIcon />}</IconButton></Tooltip>
		</Box>
		<Box sx={{ flex:1, overflow:'auto' }}>
			{loading && <Box sx={{ display:'flex', alignItems:'center', justifyContent:'center', py:2 }}><CircularProgress aria-label="Loading" size={18} sx={{ color:'#00d4ff' }} /></Box>}
			{sortedGroups.filter(g=> grouped[g]).map(g=>(
				<Box key={g} sx={{ mt:1 }}>
					<ListItemButton onClick={()=>toggleGroup(g)} sx={{ py:0.75, opacity: collapsed?0:1 }} aria-expanded={openGroups[g]}>
						<ListItemText primary={g.toUpperCase()} primaryTypographyProps={{ variant:'overline', sx:{ letterSpacing:1, color:'#888' } }} />
					</ListItemButton>
					<Collapse in={openGroups[g]} timeout={prefersReducedMotion()? 0: animation.durations.normal} unmountOnExit>
						<List disablePadding>
							  {grouped[g].map(item=>{ const Icon= getRouteIcon(item.id) || DashboardIcon; const sel= selected===item.id; return (
								<li key={item.id}>
									<ListItemButton selected={sel} onClick={()=>onSelect(item.id)} sx={{ pl: collapsed?1:3, '&.Mui-selected':{ backgroundColor:'#272727' } }} aria-current={sel? 'page': undefined}>
										<ListItemIcon sx={{ minWidth: collapsed?40:48, color: sel? '#00d4ff':'#888' }}><Icon /></ListItemIcon>
										{!collapsed && <ListItemText primary={<>{item.label}{item.badge && <Chip size="small" label={item.badge} sx={{ ml:1, height:18, fontSize:'0.6rem' }} />}</>} />}
									</ListItemButton>
								</li>
							);
							  })}
						</List>
					</Collapse>
				</Box>
			))}
		</Box>
		<Box component="footer" sx={{ p:1.5, fontSize:12, color:'#777', textAlign: collapsed? 'center':'left' }}>v1 • Status: Online</Box>
	</Box>); };
export default UnifiedSidebar;
