import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Button,
  Chip,
  Collapse
} from '@mui/material';
import Logo from './Logo';
import {
  Dashboard as DashboardIcon,
  Folder as FolderIcon,
  Memory as AgentsIcon,
  PlayArrow as PlayIcon,
  Settings as SettingsIcon,
  ExpandLess,
  ExpandMore,
  Add as AddIcon,
  Psychology as PsychologyIcon
} from '@mui/icons-material';
import { ROUTE_MAP } from '../routes/routeMap';
import { useUserContext } from '../context/UserContext';

interface Project {
  id: string;
  name: string;
  path: string;
  status: 'active' | 'idle' | 'analyzing';
}

interface SidebarProps {
  selectedItem: string;
  setSelectedItem: (id: string) => void;
  currentUser?: { role: string } | null;
}

const Sidebar: React.FC<SidebarProps> = ({ selectedItem, setSelectedItem, currentUser }) => {
  const [projectsOpen, setProjectsOpen] = useState(true);
  const [projects] = useState<Project[]>([
    { id: '1', name: 'Demo Project', path: '/demo', status: 'active' },
    { id: '2', name: 'AI Chat Bot', path: '/chatbot', status: 'idle' },
  ]);

  const { featuresEnabled } = useUserContext();

  // Map route id patterns to icons (fallback DashboardIcon)
  const iconFor = (id: string) => {
    if (id.includes('oracle')) return DashboardIcon;
    if (id.includes('quantum') || id.includes('neural')) return PlayIcon;
    if (id.includes('agent')) return AgentsIcon;
    if (id.includes('learning')) return PsychologyIcon;
    if (id.includes('health')) return SettingsIcon;
    if (id.includes('pricing')) return SettingsIcon;
    if (id.includes('contact')) return SettingsIcon;
    if (id.includes('workflow')) return PlayIcon;
    return DashboardIcon;
  };

  // Transform ROUTE_MAP into grouped menu structure
  interface MenuEntry { id: string; label: string; badge?: string; icon: any; group?: string; featureFlag?: string; roles?: string[]; }
  const derivedMenu: MenuEntry[] = useMemo(() => {
    return ROUTE_MAP.map((r: { id: string; title: string; badge?: string; group?: string; featureFlag?: string; roles?: string[] }) => ({
      id: r.id,
      label: r.title,
      badge: r.badge,
      icon: iconFor(r.id),
      group: r.group,
      featureFlag: r.featureFlag,
      roles: r.roles
    }));
  }, []);

  // Basic group ordering
  const GROUP_ORDER = ['core','user','agents','revolutionary','trading','ops','admin','investor','marketing'];

  const visibleMenu = useMemo(() => {
    return derivedMenu
      .filter(m => !m.featureFlag || featuresEnabled.includes(m.featureFlag))
      .filter(m => {
        if (m.roles && !m.roles.includes(currentUser?.role || '')) return false;
        return true;
      })
      .sort((a,b) => (GROUP_ORDER.indexOf(a.group||'zzz') - GROUP_ORDER.indexOf(b.group||'zzz')) || a.label.localeCompare(b.label));
  }, [derivedMenu, featuresEnabled, currentUser]);

  const grouped = useMemo(() => {
    const map: Record<string, MenuEntry[]> = {};
    visibleMenu.forEach(m => {
      const g = m.group || 'other';
      if (!map[g]) map[g] = [];
      map[g].push(m);
    });
    return map;
  }, [visibleMenu]);

  const [revolutionaryOpen, setRevolutionaryOpen] = useState<boolean>(() => {
    try {
      const stored = localStorage.getItem('sidebar_revolutionary_open');
      return stored === null ? true : stored === 'true';
    } catch { return true; }
  });
  React.useEffect(() => {
    try { localStorage.setItem('sidebar_revolutionary_open', String(revolutionaryOpen)); } catch {}
  }, [revolutionaryOpen]);
  const toggleRevolutionary = () => setRevolutionaryOpen(o => !o);

  // Keyboard nav: arrow up/down to move selection within flat ordered visibleMenu
  const flatIds = useMemo(() => visibleMenu.map(m => m.id), [visibleMenu]);
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (['ArrowDown','ArrowUp','Home','End'].includes(e.key)) {
      e.preventDefault();
      const idx = flatIds.indexOf(selectedItem);
      let nextIdx = idx;
      if (e.key === 'ArrowDown') nextIdx = (idx + 1) % flatIds.length;
      else if (e.key === 'ArrowUp') nextIdx = (idx - 1 + flatIds.length) % flatIds.length;
      else if (e.key === 'Home') nextIdx = 0; else if (e.key === 'End') nextIdx = flatIds.length -1;
      setSelectedItem(flatIds[nextIdx]);
    }
  };

  // On mount, if stored selection exists, use it (one-time advisory; parent owns state so optional)
  React.useEffect(() => {
    const stored = localStorage.getItem('sidebar_selected_item');
    if (stored && stored !== selectedItem) {
      // Parent manages selectedItem; we could optionally notify by setSelectedItem
      setSelectedItem(stored);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleItemClick = (itemId: string) => {
    try { localStorage.setItem('sidebar_selected_item', itemId); } catch {}
    setSelectedItem(itemId);
  };

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'active': return 'success';
      case 'analyzing': return 'warning';
      default: return 'default';
    }
  };

  // Only show User Management tab for admin
  // (legacy filteredMenuItems removed; dynamic grouping used instead)

  return (
    <Box 
      className="sidebar" 
      sx={{ 
        width: 280,
        height: '100vh',
        backgroundColor: '#1e1e1e',
        color: '#ffffff',
        borderRight: '1px solid #333',
        overflow: 'auto',
      }}
    >
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: '1px solid #333' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <Logo size="small" theme="dark" />
          <Box>
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              PROMETHEUS
            </Typography>
            <Typography variant="body2" sx={{ color: '#888', fontSize: '0.75rem' }}>
              NeuroForge™ Trading Platform
            </Typography>
          </Box>
        </Box>
      </Box>      {/* Navigation */}
      {GROUP_ORDER.map(groupKey => grouped[groupKey] && (
        <Box key={groupKey} sx={{ mt: 1 }}>
          <Box sx={{ display:'flex', alignItems:'center', px:2, cursor: groupKey==='revolutionary' ? 'pointer' : 'default' }}
               onClick={groupKey==='revolutionary'?toggleRevolutionary:undefined}
               role="heading" aria-level={2}
               aria-expanded={groupKey==='revolutionary'?revolutionaryOpen:undefined}>
            <Typography variant="overline" sx={{ flex:1, color: '#888', letterSpacing: 1 }}>
              {groupKey.toUpperCase()}
            </Typography>
            {groupKey==='revolutionary' && (revolutionaryOpen ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />)}
          </Box>
          <List dense role="group" aria-label={groupKey} onKeyDown={handleKeyDown}>
            {groupKey==='revolutionary' && !revolutionaryOpen ? null : grouped[groupKey].map(item => (
              <ListItem key={item.id} disablePadding>
                <ListItemButton
                  selected={selectedItem === item.id}
                  onClick={() => handleItemClick(item.id)}
                  role="menuitemradio"
                  aria-checked={selectedItem === item.id}
                  tabIndex={0}
                  sx={{
                    '&.Mui-selected': { backgroundColor: '#333', '&:hover': { backgroundColor: '#444' } },
                    '&:hover': { backgroundColor: '#2a2a2a' }
                  }}
                >
                  <ListItemIcon sx={{ color: selectedItem === item.id ? '#90caf9' : '#888' }}>
                    <item.icon />
                  </ListItemIcon>
                  <ListItemText
                    primary={<>
                      {item.label}
                      {item.badge && (
                        <Chip
                          label={item.badge}
                          size="small"
                          sx={{ ml: 1, height: 18, fontSize: '0.6rem', backgroundColor: item.badge === 'new' ? '#4caf50' : item.badge === 'AI' ? '#9c27b0' : '#2196f3', color: 'white' }}
                        />
                      )}
                    </>}
                    sx={{ color: selectedItem === item.id ? '#90caf9' : '#ffffff' }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
          <Divider sx={{ borderColor: '#333' }} />
        </Box>
      ))}

      <Divider sx={{ borderColor: '#333', my: 1 }} />

      {/* Projects Section */}
      <Box sx={{ px: 2 }}>
        <ListItemButton
          onClick={() => setProjectsOpen(!projectsOpen)}
          sx={{ px: 0, '&:hover': { backgroundColor: '#2a2a2a' } }}
        >
          <ListItemIcon sx={{ color: '#888' }}>
            <FolderIcon />
          </ListItemIcon>
          <ListItemText
            primary="Projects"
            sx={{ color: '#ffffff' }}
          />
          {projectsOpen ? <ExpandLess /> : <ExpandMore />}
        </ListItemButton>
        <Collapse in={projectsOpen} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {projects.map((project) => (
              <ListItem key={project.id} sx={{ py: 0.5, pl: 4 }}>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Typography variant="body2" sx={{ color: '#ffffff' }}>
                        {project.name}
                      </Typography>
                      <Chip
                        label={project.status}
                        size="small"
                        color={getStatusColor(project.status) as any}
                        sx={{ height: '20px', fontSize: '0.7rem' }}
                      />
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Collapse>
      </Box>

      {/* Import Button */}
      <Box sx={{ px: 2, pb: 2 }}>
        <Button
          startIcon={<AddIcon />}
          variant="outlined"
          size="small"
          fullWidth
          sx={{ 
            mt: 1,
            borderColor: '#555',
            color: '#ffffff',
            '&:hover': {
              borderColor: '#777',
              backgroundColor: '#333'
            }
          }}
        >
          Import Project
        </Button>
      </Box>

      {/* Status Footer */}
      <Box sx={{ mt: 'auto', p: 2, borderTop: '1px solid #333' }}>
        <Typography variant="caption" sx={{ color: '#888' }}>
          System Status: Online
        </Typography>
        <br />
        <Typography variant="caption" sx={{ color: '#888' }}>
          Agents: 3 available
        </Typography>
      </Box>
    </Box>
  );
};

export default Sidebar;
