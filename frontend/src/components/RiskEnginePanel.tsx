import React, { useEffect, useState, useCallback } from 'react';
import { Card, CardContent, Typography, Grid, Chip, LinearProgress, Box, Alert, Table, TableHead, TableRow, TableCell, TableBody, IconButton, Tooltip, Divider, TextField, Pagination, Button, MenuItem, Select, FormControl, InputLabel, Collapse, Switch, FormControlLabel } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import ShieldIcon from '@mui/icons-material/Security';
import HistoryIcon from '@mui/icons-material/History';
import WarningIcon from '@mui/icons-material/WarningAmber';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import CodeIcon from '@mui/icons-material/Code';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { API_ENDPOINTS, apiCall, apiCallText, apiCallBlob } from '../config/api';
import { useSnackbar } from 'notistack';

interface RiskProfile {
  user_id: string;
  persona?: string | null;
  persona_parameters?: any;
  base_risk: { max_position_size: number; max_daily_loss: number; max_leverage: number; };
  effective_risk: { max_position_size: number; max_daily_loss: number; max_leverage: number; };
  risk_multiplier: number;
  position_size_pct: number;
  live_trading_enabled_global: boolean;
  live_trading_admin_allowed: boolean;
  timestamp: string;
}

interface AuditEntry {
  id: string;
  timestamp: string;
  user_id: string;
  action: string;
  details: string;
  level: string;
  extra?: Record<string, any>;
}

const RiskEnginePanel: React.FC = () => {
  const [profile, setProfile] = useState<RiskProfile | null>(null);
  const [audit, setAudit] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [query, setQuery] = useState('');
  const [pendingQuery, setPendingQuery] = useState('');
  const [levels, setLevels] = useState<string[]>([]); // multiselect levels
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [debounceTimer, setDebounceTimer] = useState<any>(null);
  const [exporting, setExporting] = useState(false);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const { enqueueSnackbar } = useSnackbar();
  const [showAdvanced, setShowAdvanced] = useState(false); // progressive disclosure toggle
  const EXPORT_CAP_THRESHOLD = 950; // warn user when over this count

  // Load persisted filters once on mount
  useEffect(()=>{
    try {
      const raw = localStorage.getItem('auditFilters');
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed.query) { setQuery(parsed.query); setPendingQuery(parsed.query); }
        if (Array.isArray(parsed.levels)) setLevels(parsed.levels);
        if (parsed.startDate) setStartDate(parsed.startDate);
        if (parsed.endDate) setEndDate(parsed.endDate);
      }
    } catch { /* ignore */ }
  }, []);

  // Persist filters whenever they change (debounced via existing search debounce for query)
  useEffect(()=>{
    const payload = { query, levels, startDate, endDate };
    try { localStorage.setItem('auditFilters', JSON.stringify(payload)); } catch { /* ignore */ }
  }, [query, levels, startDate, endDate]);
  const [error, setError] = useState<string | null>(null);

  const fetchRisk = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const token = localStorage.getItem('auth_token');
      const data = await apiCall(API_ENDPOINTS.RISK_PROFILE, { headers: { 'Authorization': `Bearer ${token}` }});
      setProfile(data);
    } catch (e:any) { setError(e.message || 'Risk profile failed'); }
    finally { setLoading(false); }
  }, []);

  const fetchAudit = useCallback(async (pageArg: number = page, qArg: string = query, lvl: string[] = levels, sd?: string, ed?: string) => {
    try {
      const token = localStorage.getItem('auth_token');
      const params = new URLSearchParams({ limit: '20', page: String(pageArg) });
      if (qArg) params.append('q', qArg);
      if (lvl.length) params.append('levels', lvl.join(','));
      if (sd) params.append('start', sd);
      if (ed) params.append('end', ed);
      const data = await apiCall(API_ENDPOINTS.AUDIT_RECENT + '?' + params.toString(), { headers: { 'Authorization': `Bearer ${token}` }});
      setAudit(data.logs || []);
      setPages(data.pages || 1);
    } catch { /* ignore */ }
  }, [page, query, levels, startDate, endDate]);

  const handleExport = async (fmt: 'csv'|'json'|'zip') => {
    try {
      setExporting(true);
      const token = localStorage.getItem('auth_token');
      const params = new URLSearchParams();
      if (query) params.append('q', query);
      if (levels.length) params.append('levels', levels.join(','));
      if (startDate) params.append('start', startDate);
      if (endDate) params.append('end', endDate);
      params.append('fmt', fmt);
      const url = API_ENDPOINTS.AUDIT_EXPORT + '?' + params.toString();
      if (fmt === 'zip') {
        const blob = await apiCallBlob(url, { headers: { 'Authorization': `Bearer ${token}` }});
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'audit_export.zip'; a.click();
      } else {
        const textResp = await apiCallText(url, { headers: { 'Authorization': `Bearer ${token}` }});
        if (fmt === 'json') {
          let pretty = textResp;
          try { pretty = JSON.stringify(JSON.parse(textResp), null, 2); } catch {}
          const blob = new Blob([pretty], { type: 'application/json' });
          const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'audit_export.json'; a.click();
        } else {
          const blob = new Blob([textResp], { type: 'text/csv' });
          const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'audit_export.csv'; a.click();
        }
      }
      enqueueSnackbar(`Exported audit logs (${fmt.toUpperCase()})`, { variant: 'success' });
    } finally { setExporting(false); }
  };

  const levelColor = (lvl: string) => {
    switch(lvl){
      case 'error': return 'error';
      case 'warning': return 'warning';
      case 'critical': return 'secondary';
      default: return 'default';
    }
  };

  const toggleExpand = (id: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  useEffect(()=>{ fetchRisk(); fetchAudit(page, query, levels, startDate, endDate); const id = setInterval(()=>{ fetchRisk(); fetchAudit(page, query, levels, startDate, endDate); }, 60000); return ()=> clearInterval(id); }, [fetchRisk, fetchAudit, page, query, levels, startDate, endDate]);

  // Debounce search (300ms)
  useEffect(()=>{
    if (debounceTimer) clearTimeout(debounceTimer);
    const t = setTimeout(()=>{ setQuery(pendingQuery); setPage(1); fetchAudit(1, pendingQuery, levels, startDate, endDate); }, 300);
    setDebounceTimer(t);
    return ()=> clearTimeout(t);
  // eslint-disable-next-line
  }, [pendingQuery]);

  const handleLevelChange = (val: string[]) => {
    setLevels(val);
    setPage(1);
    fetchAudit(1, pendingQuery, val, startDate, endDate);
  };

  const applyDateFilters = () => {
    setPage(1);
    fetchAudit(1, pendingQuery, levels, startDate || undefined, endDate || undefined);
  };

  return (
    <Card sx={{ mb:3 }}>
      <CardContent>
        <Box sx={{ display:'flex', alignItems:'center', justifyContent:'space-between', mb:2 }}>
          <Box sx={{ display:'flex', alignItems:'center', gap:1 }}>
            <ShieldIcon color='primary' />
            <Typography variant='h6' sx={{ fontWeight:'bold' }}>Risk Engine Overview</Typography>
            {profile?.persona && <Chip size='small' color='primary' label={profile.persona.replace('_hrm','').toUpperCase()} />}
            {profile && <Chip size='small' label={`Risk x${profile.risk_multiplier}`} />}
          </Box>
          <Box>
            <Tooltip title='Refresh'>
              <IconButton size='small' onClick={()=>{ fetchRisk(); fetchAudit(); }}><RefreshIcon /></IconButton>
            </Tooltip>
          </Box>
        </Box>
        {loading && <LinearProgress sx={{ mb:2 }} />}
        {error && <Alert severity='error' sx={{ mb:2 }}>{error}</Alert>}
        {profile && (
          <Grid container spacing={2} sx={{ mb:2 }}>
            <Grid item xs={12} md={4}>
              <Card variant='outlined'>
                <CardContent>
                  <Typography variant='caption' color='text.secondary'>Effective Limits</Typography>
                  <Box sx={{ mt:1, display:'flex', flexDirection:'column', gap:0.5 }}>
                    <Typography variant='body2'>Max Position: ${profile.effective_risk.max_position_size.toLocaleString()}</Typography>
                    <Typography variant='body2'>Max Daily Loss: ${profile.effective_risk.max_daily_loss.toLocaleString()}</Typography>
                    <Typography variant='body2'>Max Leverage: {profile.effective_risk.max_leverage.toFixed(2)}x</Typography>
                    <Typography variant='body2'>Position Size %: {(profile.position_size_pct*100).toFixed(1)}%</Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant='outlined'>
                <CardContent>
                  <Typography variant='caption' color='text.secondary'>Base Limits</Typography>
                  <Box sx={{ mt:1, display:'flex', flexDirection:'column', gap:0.5 }}>
                    <Typography variant='body2'>Max Position: ${profile.base_risk.max_position_size.toLocaleString()}</Typography>
                    <Typography variant='body2'>Max Daily Loss: ${profile.base_risk.max_daily_loss.toLocaleString()}</Typography>
                    <Typography variant='body2'>Max Leverage: {profile.base_risk.max_leverage.toFixed(2)}x</Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant='outlined'>
                <CardContent>
                  <Typography variant='caption' color='text.secondary'>Live Trading Access</Typography>
                  <Box sx={{ mt:1, display:'flex', flexDirection:'column', gap:0.5 }}>
                    <Chip size='small' color={profile.live_trading_enabled_global? 'success':'default'} label={`Global: ${profile.live_trading_enabled_global? 'ENABLED':'DISABLED'}`} />
                    <Chip size='small' color={profile.live_trading_admin_allowed? 'success':'warning'} label={profile.live_trading_admin_allowed? 'Admin Live Allowed':'Admin Live Blocked'} />
                    {!profile.live_trading_enabled_global && <Chip size='small' icon={<WarningIcon />} label='Failsafe Active' />}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
        <Divider sx={{ my:2 }} />
  <Box sx={{ display:'flex', alignItems:'center', gap:1, mb:1, flexWrap:'wrap' }}>
          <HistoryIcon fontSize='small' />
          <Typography variant='subtitle1' sx={{ fontWeight:'bold' }}>Recent Audit Activity</Typography>
          <Box sx={{ flexGrow:1 }} />
          <TextField size='small' label='Search' value={pendingQuery} onChange={(e)=>setPendingQuery(e.target.value)} sx={{ minWidth:160 }} />
          <FormControlLabel control={<Switch checked={showAdvanced} onChange={(_,v)=>setShowAdvanced(v)} />} label='Advanced' sx={{ ml:1 }} />
          <Collapse in={showAdvanced} orientation='horizontal' timeout={300} unmountOnExit>
            <Box sx={{ display:'flex', alignItems:'center', gap:1, flexWrap:'wrap', pl:1 }} data-advanced-filters>
              <FormControl size='small' sx={{ minWidth:140 }}>
                <InputLabel id='audit-levels-label'>Levels</InputLabel>
                <Select labelId='audit-levels-label' multiple value={levels} label='Levels'
                  onChange={(e)=>handleLevelChange(typeof e.target.value === 'string'? e.target.value.split(','): e.target.value as string[])}
                  renderValue={(selected)=> selected.join(', ')}>
                  {['info','warning','error','critical'].map(l=> <MenuItem key={l} value={l}>{l}</MenuItem>)}
                </Select>
              </FormControl>
              <TextField size='small' type='datetime-local' label='Start' InputLabelProps={{ shrink:true }} value={startDate} onChange={e=>setStartDate(e.target.value)} />
              <TextField size='small' type='datetime-local' label='End' InputLabelProps={{ shrink:true }} value={endDate} onChange={e=>setEndDate(e.target.value)} />
              <Button variant='outlined' size='small' onClick={applyDateFilters}>Apply</Button>
              <Button variant='text' size='small' onClick={()=>{ setLevels([]); setStartDate(''); setEndDate(''); setPendingQuery(''); setQuery(''); setPage(1); fetchAudit(1,'',[], undefined, undefined); enqueueSnackbar('Audit filters reset', { variant: 'info' }); }}>Reset</Button>
              <Button variant='contained' size='small' disabled={exporting} onClick={()=>handleExport('csv')}>CSV</Button>
              <Button variant='contained' size='small' disabled={exporting} onClick={()=>handleExport('json')}>JSON</Button>
              <Tooltip title={process.env.REACT_APP_ENABLE_AUDIT_ZIP_EXPORT === 'true' ? 'Export as ZIP' : 'ZIP export pending backend support (set REACT_APP_ENABLE_AUDIT_ZIP_EXPORT=true to enable)'}>
                <span>
                  <Button variant='contained' size='small' disabled={exporting || process.env.REACT_APP_ENABLE_AUDIT_ZIP_EXPORT !== 'true'} onClick={()=>handleExport('zip')}>ZIP</Button>
                </span>
              </Tooltip>
            </Box>
          </Collapse>
        </Box>
        {audit.length >= EXPORT_CAP_THRESHOLD && (
          <Alert severity='warning' sx={{ mb:1 }}>
            Displaying {audit.length} entries. Export capped at 1000; refine filters for smaller dataset.
          </Alert>
        )}
        {audit.length === 0 ? (
          <Typography variant='body2' color='text.secondary'>No recent activity</Typography>
        ) : (
          <Table size='small'>
            <TableHead>
              <TableRow>
                <TableCell>Time</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Details</TableCell>
                <TableCell>Persona/Risk</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {audit.map(a => {
                const isOpen = expanded.has(a.id);
                const shortDetails = a.details.length > 100 ? a.details.slice(0,100) + '…' : a.details;
                return (
                  <React.Fragment key={a.id}>
                    <TableRow hover>
                      <TableCell>
                        <Box sx={{ display:'flex', alignItems:'center', gap:0.5 }}>
                          <IconButton size='small' onClick={()=>toggleExpand(a.id)} aria-label={isOpen? 'collapse audit row':'expand audit row'}>
                            {isOpen ? <ExpandLessIcon fontSize='small' /> : <ExpandMoreIcon fontSize='small' />}
                          </IconButton>
                          {new Date(a.timestamp).toLocaleTimeString()}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display:'flex', alignItems:'center', gap:0.5, flexWrap:'wrap' }}>
                          <Chip label={a.level} size='small' color={levelColor(a.level) as any} variant={['info','default'].includes(a.level)?'outlined':'filled'} />
                          <span>{a.action}</span>
                        </Box>
                      </TableCell>
                      <TableCell>{shortDetails}</TableCell>
                      <TableCell>
                        {a.extra?.persona && <Chip size='small' label={a.extra.persona.replace('_hrm','')} sx={{ mr:0.5 }} />}
                        {a.extra?.risk_multiplier && <Chip size='small' label={`x${a.extra.risk_multiplier}`} />}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell colSpan={4} sx={{ p:0, border:0 }}>
                        <Collapse in={isOpen} timeout='auto' unmountOnExit>
                          <Box sx={{ bgcolor:'rgba(0,0,0,0.03)', p:1.5, borderTop:'1px solid rgba(0,0,0,0.06)' }}>
                            <Box sx={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                              <Typography variant='caption' color='text.secondary'>Full Details</Typography>
                              <IconButton size='small' aria-label='copy full details' onClick={()=>{ navigator.clipboard.writeText(a.details); enqueueSnackbar('Details copied', { variant: 'success' }); }}>
                                <ContentCopyIcon fontSize='inherit' />
                              </IconButton>
                            </Box>
                            <Typography variant='body2' sx={{ mb:1, whiteSpace:'pre-wrap' }}>{a.details}</Typography>
                            {a.extra && (
                              <Box sx={{ fontFamily:'monospace', fontSize:'0.7rem', position:'relative' }}>
                                <Box sx={{ display:'flex', alignItems:'center', gap:0.5, mb:0.5 }}>
                                  <CodeIcon fontSize='inherit' /> <Typography variant='caption'>Extra</Typography>
                                </Box>
                                <Box sx={{ position:'absolute', top:2, right:2 }}>
                                  <IconButton size='small' aria-label='copy extra json' onClick={()=>{ navigator.clipboard.writeText(JSON.stringify(a.extra, null, 2)); enqueueSnackbar('Extra JSON copied', { variant: 'success' }); }}>
                                    <ContentCopyIcon fontSize='inherit' />
                                  </IconButton>
                                </Box>
                                <pre style={{ margin:0, maxHeight:150, overflow:'auto', paddingRight:32 }}>{JSON.stringify(a.extra, null, 2)}</pre>
                              </Box>
                            )}
                          </Box>
                        </Collapse>
                      </TableCell>
                    </TableRow>
                  </React.Fragment>
                );
              })}
            </TableBody>
          </Table>
        )}
        <Box sx={{ mt:2, display:'flex', justifyContent:'center' }}>
          <Pagination count={pages} page={page} onChange={(_,p)=>{ setPage(p); fetchAudit(p, query); }} size='small' />
        </Box>
      </CardContent>
    </Card>
  );
};

export default RiskEnginePanel;
