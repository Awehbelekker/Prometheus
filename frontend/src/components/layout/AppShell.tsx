import React, { useEffect, useMemo, useState } from 'react';
import { Box, CssBaseline, ThemeProvider, createTheme, useMediaQuery, IconButton, Tooltip } from '@mui/material';
import { StatusBar } from '../status';
import { OnboardingChecklist } from '../onboarding';
import { CommandPalette } from '../palette';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
// Using relative path to navigation component
import UnifiedSidebar from '../unified/UnifiedSidebar';
import { colors, typographyScale, layout as layoutTokens, spacing } from '../../design/tokens';
import { animation, prefersReducedMotion } from '../../design/animation';
import { useUxTelemetry } from '../../hooks/useUxTelemetry';
import { FeatureFlagsProvider, useFeatureFlags } from '../../context/UserContext';
import { visibleRoutes } from '../../routes/routeMap';
import PerformanceHistoryPanel from '../performance/PerformanceHistoryPanel';
import PlaceholderPanel from '../revolutionary/PlaceholderPanel';
interface AppShellProps { renderMain:(id:string)=>React.ReactNode; initialItem?:string; sidebarVariant?:'legacy'|'modern'|'auto'; menuConfig?: any; }
const InnerShell:React.FC<AppShellProps>=({ renderMain, initialItem='dashboard', sidebarVariant='auto' })=>{
  const prefersDark=useMediaQuery('(prefers-color-scheme: dark)');
  const [mode,setMode]=useState<'light'|'dark'>(prefersDark? 'dark':'light');
  const [current,setCurrent]=useState(initialItem);
  const [paletteOpen,setPaletteOpen]=useState(false);
  const [showOnboarding,setShowOnboarding]=useState(()=>{ try { return localStorage.getItem('onboarding_complete')!=='true'; } catch { return true; } });
  useEffect(()=>{ const handler=(e:KeyboardEvent)=>{ if((e.metaKey||e.ctrlKey) && e.key.toLowerCase()==='k'){ e.preventDefault(); setPaletteOpen(true); } }; window.addEventListener('keydown',handler); return ()=> window.removeEventListener('keydown',handler); },[]);
  const { track }=useUxTelemetry();
  useEffect(()=>{ track('nav_init',{ item: initialItem }); },[initialItem,track]);
  const theme=useMemo(()=>{ const isDark=mode==='dark'; return createTheme({ palette:{ mode, primary:{ main: colors.primary[500] }, secondary:{ main: colors.accent.orange }, background:{ default: isDark? colors.neutral[950]: colors.neutral[50], paper: isDark? colors.neutral[900]:'#ffffff' } }, typography:{ fontFamily: typographyScale.fontFamily }, shape:{ borderRadius:12 }, transitions:{ create:()=> prefersReducedMotion() ? 'none' : `all ${animation.durations.normal}ms ${animation.easing.standard}` } }); },[mode]);
  const { has } = useFeatureFlags();
  const paletteItems = useMemo(()=> visibleRoutes(has).map(r=>({ id:r.id, label:r.label, keywords:r.keywords, group:r.group })),[has]);
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <a href="#main-content" className="skip-link">Skip to content</a>
      <Box sx={{ display:'flex', minHeight:'100vh', background: colors.gradients.subtle }}>
  <UnifiedSidebar selected={current} onSelect={(panelId: string)=>{ setCurrent(panelId); track('panel_open',{ id: panelId }); }} variant={sidebarVariant} />
        <Box component="main" id="main-content" role="main" tabIndex={-1} sx={{ flex:1, outline:'none', display:'flex', flexDirection:'column' }}>
          <Box component="header" role="banner" sx={{ height: layoutTokens.topBarHeight, display:'flex', alignItems:'center', justifyContent:'space-between', px:2, gap:1 }}>
            <StatusBar currentPanel={current} onOpenPalette={()=>setPaletteOpen(true)} />
            <Tooltip title={`Switch to ${mode==='dark'?'light':'dark'} mode`}>
              <IconButton color="primary" onClick={()=>setMode(m=>m==='dark'?'light':'dark')} aria-label="Toggle color scheme">
                {mode==='dark'? <Brightness7Icon />:<Brightness4Icon />}
              </IconButton>
            </Tooltip>
          </Box>
          <Box sx={{ flex:1, p: spacing(4) }}>
            {showOnboarding && <OnboardingChecklist onComplete={()=>{ setShowOnboarding(false); try{ localStorage.setItem('onboarding_complete','true'); }catch{} track('onboarding_complete'); }} onDismiss={()=>{ setShowOnboarding(false); track('onboarding_dismiss'); }} />}
            {renderMain(current)}
            {current==='performance-history' && <PerformanceHistoryPanel />}
            {current==='holographic-ui' && <PlaceholderPanel featureFlag='holographic_ui' title='Holographic UI' description='Immersive multi-dimensional visualization environment for market microstructure and agent collaboration.' />}
            {current==='predictive-oracle' && <PlaceholderPanel featureFlag='predictive_oracle' title='Predictive Oracle' description='Long-horizon probabilistic market trajectory forecasting with uncertainty quantification.' />}
            {current==='nanosecond-exec' && <PlaceholderPanel featureFlag='nanosecond_execution' title='Nanosecond Execution' description='Ultra-low latency execution path leveraging specialized co-location & FPGA acceleration.' />}
            {current==='hierarchical-agents' && <PlaceholderPanel featureFlag='hierarchical_agents' title='Hierarchical Agents' description='Layered agent governance enabling strategic planners and tactical executors with learning feedback loops.' />}
            {current==='multi-agent-orchestrator' && <PlaceholderPanel featureFlag='multi_agent_orchestrator' title='Multi-Agent Orchestrator' description='Dynamic orchestration fabric coordinating specialized agents under global objectives and risk budgets.' />}
          </Box>
        </Box>
      </Box>
  <CommandPalette open={paletteOpen} onClose={()=>setPaletteOpen(false)} onSelect={(id: string)=>{ setCurrent(id); setPaletteOpen(false); track('palette_select',{ id }); }} items={paletteItems} />
    </ThemeProvider>
  );
};
const AppShell:React.FC<AppShellProps>= (props)=> (
  <FeatureFlagsProvider>
    <InnerShell {...props} />
  </FeatureFlagsProvider>
);
export default AppShell;
