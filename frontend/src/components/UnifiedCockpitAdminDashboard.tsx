import React, { useState, useEffect, Suspense, lazy, useMemo, useCallback, memo } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  IconButton,
  Badge,
  Chip,
  Divider,
  Collapse,
  Card,
  CardContent,
  Grid,
  Button,
  alpha,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  Tooltip,
  Avatar,
  CircularProgress,
  Checkbox,
  FormControlLabel,
  Menu
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  Notifications as NotificationsIcon,
  TrendingUp as TradingIcon,
  AccountBalance as PortfolioIcon,
  Psychology as AIIcon,
  AdminPanelSettings as AdminIcon,
  Settings as SettingsIcon,
  ExpandLess,
  ExpandMore,
  Menu as MenuIcon,
  ChevronLeft,
  People as UsersIcon,
  Security as SecurityIcon,
  Assessment as ReportsIcon,
  MonitorHeart as MonitorIcon,
  AttachMoney,
  CheckCircle,
  Cancel,
  PlayArrow,
  Visibility,
  Edit,
  Add,
  Refresh,
  Warning,
  Pause,
  Email,
  ContentCopy,
  FileDownload,
  Search,
  Info,
  Error as ErrorIcon
} from '@mui/icons-material';
import TradingCommandCenter from './unified/TradingCommandCenter';
import RealTimeWealthTracker from './RealTimeWealthTracker';
import InternalPaperTrading from './InternalPaperTrading';
import MobileNavigation from './common/MobileNavigation';
import LoadingCard from './common/LoadingCard';
import ErrorBoundary from './common/ErrorBoundary';
import { getApiUrl } from '../config/api';
import { getJsonWithRetry } from '../utils/network';
import { DefaultLoadingFallback } from '../utils/lazyLoad';
import { exportUsers, exportAuditLogs, exportToPDF, exportToExcel } from '../utils/exportData';
import { useAdminWebSocket } from '../hooks/useAdminWebSocket';
import {
  useAdminMetrics,
  useAdminUsers,
  useLiveTradingStatus,
  usePaperTradingSessions,
  useAuditLogs,
  useInvitations,
  useAllocateFunds,
  useSendInvitation
} from '../hooks/useAdminData';
import TradingPermissionsTab from './admin/TradingPermissionsTab';
import SystemMonitoringTab from './admin/SystemMonitoringTab';

// Phase 4: Revolutionary AI & Agent Monitoring Components - Lazy Loaded
const RevolutionaryAIPanel = lazy(() => import('./admin/RevolutionaryAIPanel'));
const HierarchicalAgentMonitor = lazy(() => import('./admin/HierarchicalAgentMonitor'));
const MarketOpportunitiesPanel = lazy(() => import('./admin/MarketOpportunitiesPanel'));


// API Configuration - REAL DATA ONLY (NO MOCK DATA)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const REAL_DATA_API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'; // Use main backend server

/**
 * 🚀 UNIFIED COCKPIT ADMIN DASHBOARD
 *
 * The single, comprehensive admin interface that combines:
 * - TradingCommandCenter header (matches user screenshot exactly)
 * - Cockpit-style sidebar with organized navigation
 * - All admin functionality in one cohesive interface
 * - Real-time data updates and professional design
 */

interface UnifiedCockpitAdminDashboardProps {
  user: {
    id: string;
    username: string;
    email: string;
    role: string;
    tier: 'demo' | 'premium' | 'admin';
  };
  onLogout: () => void;
}

interface NavigationSection {
  id: string;
  label: string;
  icon: React.ElementType;
  badge?: string | number;
  children?: NavigationItem[];
  defaultOpen?: boolean;
}

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ElementType;
  badge?: string | number;
  color?: string;
}

interface AdminMetrics {
  totalUsers: number;
  activeTraders: number;
  totalAllocated: number;
  totalPortfolioValue: number;
  dailyPnL: number;
  systemUptime: number;
  pendingApprovals: number;
  activeSessions: number;
}

interface User {
  id: string;
  username: string;
  email: string;
  name: string;
  status: 'pending' | 'approved' | 'active' | 'suspended';
  tier: 'paper_only' | 'live_approved' | 'admin';
  allocatedFunds: number;
  currentValue: number;
  pnl: number;
  pnlPercentage: number;
  joinDate: string;
  liveTrading: boolean;
  lastActivity: string;
}

const UnifiedCockpitAdminDashboard: React.FC<UnifiedCockpitAdminDashboardProps> = ({
  user,
  onLogout
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedSection, setSelectedSection] = useState('dashboard');
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    core: true,
    trading: true,
    ai: false,
    admin: false,
    settings: false
  });

  // React Query hooks for optimized data fetching
  const { data: adminMetricsData, isLoading: metricsLoading, refetch: refetchMetrics } = useAdminMetrics(user.id);
  const { data: usersData, isLoading: usersLoading, refetch: refetchUsers } = useAdminUsers(user.id);
  const { data: liveTradingStatusData } = useLiveTradingStatus();
  const { data: paperSessionsData } = usePaperTradingSessions();
  const { data: auditLogsData, refetch: refetchAuditLogs } = useAuditLogs(user.id, auditFilters);
  const { data: invitationsData, refetch: refetchInvitations } = useInvitations(user.id);
  const allocateFundsMutation = useAllocateFunds(user.id);
  const sendInvitationMutation = useSendInvitation(user.id);

  // WebSocket for real-time dashboard updates
  const { data: wsMetricsData, isConnected: wsMetricsConnected, error: wsMetricsError } = useAdminWebSocket<AdminMetrics>({
    endpoint: '/ws/admin/dashboard',
    onData: (data) => {
      if (data) {
        setAdminMetrics(data);
      }
    },
    enabled: true
  });

  // Update WebSocket connection state
  useEffect(() => {
    setWsConnected(wsMetricsConnected);
    setWsError(wsMetricsError || null);
  }, [wsMetricsConnected, wsMetricsError]);

  // Sync React Query data to local state (for backward compatibility)
  useEffect(() => {
    if (adminMetricsData) {
      setAdminMetrics(adminMetricsData);
    }
  }, [adminMetricsData]);

  useEffect(() => {
    if (usersData) {
      setUsers(usersData);
    }
  }, [usersData]);

  useEffect(() => {
    if (liveTradingStatusData) {
      setLiveTradingStatus(liveTradingStatusData);
    }
  }, [liveTradingStatusData]);

  useEffect(() => {
    if (paperSessionsData) {
      setPaperSessions(paperSessionsData);
      setLoadingSessions(false);
    }
  }, [paperSessionsData]);

  useEffect(() => {
    if (auditLogsData) {
      setAuditLogs(auditLogsData);
      setLoadingAudit(false);
    }
  }, [auditLogsData]);

  useEffect(() => {
    if (invitationsData) {
      setInvitations(invitationsData);
    }
  }, [invitationsData]);

  // Admin data state (kept for backward compatibility and fallback)
  const [adminMetrics, setAdminMetrics] = useState<AdminMetrics>({
    totalUsers: 0,
    activeTraders: 0,
    totalAllocated: 0,
    totalPortfolioValue: 0,
    dailyPnL: 0,
    systemUptime: 0,
    pendingApprovals: 0,
    activeSessions: 0
  });

  // Enhanced state for consolidated features
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [auditFilters, setAuditFilters] = useState({
    actionType: 'all',
    dateRange: 'last7days',
    userId: ''
  });
  const [auditFilter, setAuditFilter] = useState('all');
  const [auditDateRange, setAuditDateRange] = useState({ start: '', end: '' });
  const [loadingAudit, setLoadingAudit] = useState(false);
  const [invitations, setInvitations] = useState<any[]>([]);
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [inviteForm, setInviteForm] = useState({
    email: '',
    name: '',
    role: 'user',
    tier: 'demo',
    initialBalance: 1000,
    inviteMessage: ''
  });
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [systemMetrics, setSystemMetrics] = useState<any[]>([]);
  const [fundAllocationDialog, setFundAllocationDialog] = useState(false);
  const [permissions, setPermissions] = useState<any[]>([]);
  const [loadingPermissions, setLoadingPermissions] = useState(false);
  const [performanceData, setPerformanceData] = useState<any[]>([]);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [allocationAmount, setAllocationAmount] = useState('');
  const [allocationReason, setAllocationReason] = useState('');

  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Use React Query loading states when available
  const isLoadingData = loading || metricsLoading || usersLoading;
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'error' | 'warning' | 'info'; message: string } | null>(null);

  // State for render functions (moved to top level to fix hooks issue)
  const [userFilter, setUserFilter] = useState('all');
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [selectedUserIds, setSelectedUserIds] = useState<string[]>([]);
  const [editUserDialog, setEditUserDialog] = useState(false);
  const [editUserForm, setEditUserForm] = useState<any>(null);
  
  // Advanced search state
  const [globalSearchQuery, setGlobalSearchQuery] = useState('');
  const [showGlobalSearch, setShowGlobalSearch] = useState(false);
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false);
  const [savedFilters, setSavedFilters] = useState<any[]>([]);
  const [searchHistory, setSearchHistory] = useState<string[]>(() => {
    const saved = localStorage.getItem('admin_search_history');
    return saved ? JSON.parse(saved) : [];
  });
  
  // WebSocket connection state for real-time updates
  const [wsConnected, setWsConnected] = useState(false);
  const [wsError, setWsError] = useState<string | null>(null);
  
  // Export menu state
  const [exportMenuAnchor, setExportMenuAnchor] = useState<null | HTMLElement>(null);
  const [auditExportMenuAnchor, setAuditExportMenuAnchor] = useState<null | HTMLElement>(null);
  
  // Performance Optimization: Memoize filtered users
  const filteredUsers = useMemo(() => {
    return users.filter(u => {
      // Status filter
      if (userFilter !== 'all') {
        if (userFilter === 'pending' && u.status !== 'pending') return false;
        if (userFilter === 'active' && u.status !== 'active') return false;
        if (userFilter === 'live' && !u.liveTrading) return false;
        if (userFilter === 'suspended' && u.status !== 'suspended') return false;
      }

      // Search filter
      if (userSearchQuery) {
        const query = userSearchQuery.toLowerCase();
        const matchesSearch =
          u.username?.toLowerCase().includes(query) ||
          u.email?.toLowerCase().includes(query) ||
          u.name?.toLowerCase().includes(query) ||
          u.id?.toLowerCase().includes(query);
        if (!matchesSearch) return false;
      }

      return true;
    });
  }, [users, userFilter, userSearchQuery]);

  // Performance Optimization: Memoize computed metrics
  const computedMetrics = useMemo(() => {
    return {
      totalUsers: users.length,
      activeUsers: users.filter(u => u.status === 'active').length,
      pendingUsers: users.filter(u => u.status === 'pending').length,
      totalAllocated: users.reduce((sum, u) => sum + (u.allocatedFunds || 0), 0),
      totalPnL: users.reduce((sum, u) => sum + (u.pnl || 0), 0),
    };
  }, [users]);

  // Keyboard Shortcuts Handler with G+key navigation
  useEffect(() => {
    let gKeyPressed = false;
    let gKeyTimeout: NodeJS.Timeout;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in input/textarea
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
        // Allow Ctrl+K and Ctrl+/ even in inputs
        if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
          e.preventDefault();
          setShowGlobalSearch(true);
          return;
        }
        if (e.key === '/' && (e.ctrlKey || e.metaKey)) {
          e.preventDefault();
          setShowKeyboardShortcuts(true);
          return;
        }
        return;
      }

      // Global shortcuts
      if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        setShowGlobalSearch(true);
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        setShowKeyboardShortcuts(true);
        return;
      }

      // G+key navigation shortcuts
      if (e.key === 'g' || e.key === 'G') {
        if (!gKeyPressed) {
          gKeyPressed = true;
          gKeyTimeout = setTimeout(() => {
            gKeyPressed = false;
          }, 1000);
          return;
        }
      }

      if (gKeyPressed && (e.key === 'g' || e.key === 'G')) {
        // Double G - do nothing or could be used for something else
        gKeyPressed = false;
        clearTimeout(gKeyTimeout);
        return;
      }

      if (gKeyPressed) {
        e.preventDefault();
        const key = e.key.toLowerCase();
        switch (key) {
          case 'd':
            setSelectedSection('dashboard');
            break;
          case 'u':
            setSelectedSection('user-management');
            break;
          case 'a':
            setSelectedSection('analytics');
            break;
          case 't':
            setSelectedSection('live-trading');
            break;
          case 'p':
            setSelectedSection('paper-trading');
            break;
          case 'n':
            setSelectedSection('notifications');
            break;
          case 's':
            setSelectedSection('system-health');
            break;
          case 'f':
            setSelectedSection('fund-allocation');
            break;
          case 'l':
            setSelectedSection('audit-logs');
            break;
          case 'm':
            setSelectedSection('user-management');
            break;
        }
        gKeyPressed = false;
        clearTimeout(gKeyTimeout);
        return;
      }

      // Escape to close dialogs
      if (e.key === 'Escape') {
        if (showGlobalSearch) setShowGlobalSearch(false);
        if (showKeyboardShortcuts) setShowKeyboardShortcuts(false);
        if (inviteDialogOpen) setInviteDialogOpen(false);
        if (editUserDialog) setEditUserDialog(false);
        if (fundAllocationDialog) setFundAllocationDialog(false);
      }

      // Ctrl/Cmd + R to refresh (prevent default page reload)
      if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        loadAdminData();
        refetchUsers();
        refetchMetrics();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (gKeyTimeout) clearTimeout(gKeyTimeout);
    };
  }, [showGlobalSearch, showKeyboardShortcuts, inviteDialogOpen, editUserDialog, fundAllocationDialog]);

  // Global Search Handler - Enhanced with multi-section search
  const handleGlobalSearch = useCallback((query: string) => {
    setGlobalSearchQuery(query);
    if (!query) return;

    // Save to search history
    if (query.trim()) {
      const newHistory = [query, ...searchHistory.filter(h => h !== query)].slice(0, 10);
      setSearchHistory(newHistory);
      localStorage.setItem('admin_search_history', JSON.stringify(newHistory));
    }

    // Search across different sections
    const lowerQuery = query.toLowerCase();
    
    // Search users
    const matchingUsers = users.filter(u => 
      u.username?.toLowerCase().includes(lowerQuery) ||
      u.email?.toLowerCase().includes(lowerQuery) ||
      u.name?.toLowerCase().includes(lowerQuery)
    );

    // Search audit logs
    const matchingAuditLogs = auditLogs.filter(log =>
      log.admin_username?.toLowerCase().includes(lowerQuery) ||
      log.action_type?.toLowerCase().includes(lowerQuery) ||
      log.action_details?.toLowerCase().includes(lowerQuery) ||
      log.target_username?.toLowerCase().includes(lowerQuery)
    );

    // Search notifications
    const matchingNotifications = notifications.filter(notif =>
      notif.title?.toLowerCase().includes(lowerQuery) ||
      notif.message?.toLowerCase().includes(lowerQuery) ||
      notif.type?.toLowerCase().includes(lowerQuery)
    );

    // Search paper sessions
    const matchingSessions = paperSessions.filter(session =>
      session.user_name?.toLowerCase().includes(lowerQuery) ||
      session.session_type?.toLowerCase().includes(lowerQuery) ||
      session.status?.toLowerCase().includes(lowerQuery)
    );

    // Navigate to section with most results
    const results = [
      { section: 'user-management', count: matchingUsers.length, query: query },
      { section: 'audit-logs', count: matchingAuditLogs.length, query: query },
      { section: 'notifications', count: matchingNotifications.length, query: query },
      { section: 'paper-trading', count: matchingSessions.length, query: query },
    ].filter(r => r.count > 0).sort((a, b) => b.count - a.count);

    if (results.length > 0) {
      setSelectedSection(results[0].section);
      if (results[0].section === 'user-management') {
        setUserSearchQuery(query);
      }
    }
  }, [users, auditLogs, notifications, paperSessions, searchHistory]);

  const [confirmDialog, setConfirmDialog] = useState<{ open: boolean; title: string; message: string; onConfirm: () => void }>({
    open: false,
    title: '',
    message: '',
    onConfirm: () => {}
  });
  const [analyticsData, setAnalyticsData] = useState({
    totalTrades: 0,
    successRate: 0,
    avgProfit: 0,
    totalVolume: 0,
    activeStrategies: 0,
    systemPerformance: 0,
    userGrowth: 0,
    revenueGrowth: 0
  });
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);
  const [portfolioData, setPortfolioData] = useState<any>(null);
  const [loadingPortfolio, setLoadingPortfolio] = useState(false);
  const [timeRange, setTimeRange] = useState('7d');
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loadingNotifications, setLoadingNotifications] = useState(false);
  const [filter, setFilter] = useState('all');
  const [paperSessions, setPaperSessions] = useState<any[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [aiHealth, setAiHealth] = useState<any>(null);
  const [loadingAI, setLoadingAI] = useState(true);
  const [tafData, setTafData] = useState({

    currentFees: 0,
    newFees: 0,
    feeIncrease: 0,
    affectedTrades: 0,
    totalTrades: 0,
    optimizationPotential: 0
  });
  const [tafLoading, setTafLoading] = useState(true);
  const [liveTradingStatus, setLiveTradingStatus] = useState<{

    isActive: boolean;
    activePositions: number;
    dailyPnL: number;
    winRate: number;
    canActivate: boolean;
  }>({
    isActive: false,
    activePositions: 0,
    dailyPnL: 0,
    winRate: 0,
    canActivate: true
  });

  // Check live trading status
  const [modelCoverage, setModelCoverage] = useState<any>(null);
  const [loadingCoverage, setLoadingCoverage] = useState<boolean>(false);

  const checkLiveTradingStatus = async () => {
    try {
      // In a real implementation, this would check:
      // 1. If live trading service is running
      // 2. If there are active live positions
      // 3. Current P&L and performance metrics
      // 4. If admin has sufficient funds allocated

      // For now, we'll simulate the check based on system state
      // Try primary live-trading endpoint, then fallback if not OK (with retries)
      const retryOpts = { retries: 3, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 } as const;
      let data: any | null = null;
      try {
        data = await getJsonWithRetry(getApiUrl('/api/live-trading/status'), {}, retryOpts);
      } catch {
        try {
          data = await getJsonWithRetry(getApiUrl('/api/trading/live-status'), {}, retryOpts);
        } catch {
          data = null;
        }
      }

      if (data) {
        setLiveTradingStatus({
          isActive: data.isActive || false,
          activePositions: data.activePositions || 0,
          dailyPnL: data.dailyPnL || 0,
          winRate: data.winRate || 0,
          canActivate: data.canActivate ?? true
        });
      } else {
        // Default to inactive status since we're not actually trading with real money yet
        setLiveTradingStatus({
          isActive: false,
          activePositions: 0,
          dailyPnL: 0,
          winRate: 0,
          canActivate: true
        });
      }
    } catch (error) {
      console.log('Live trading status check failed - defaulting to inactive');
      setLiveTradingStatus({
        isActive: false,
        activePositions: 0,
        dailyPnL: 0,
        winRate: 0,
        canActivate: true
      });
    }
  };

  // Send invitation - Use React Query mutation
  const handleSendInvitation = async () => {
    if (!inviteForm.email || !inviteForm.name) return;

    // Use React Query mutation
    sendInvitationMutation.mutate({
      email: inviteForm.email,
      name: inviteForm.name,
      role: inviteForm.role,
      tier: inviteForm.tier,
      initialBalance: inviteForm.initialBalance,
      inviteMessage: inviteForm.inviteMessage
    }, {
      onSuccess: (result) => {
        setAlert({ 
          type: 'success', 
          message: `Invitation sent successfully to ${inviteForm.email}${result.invitation_code ? `. Code: ${result.invitation_code}` : ''}` 
        });
        setInviteDialogOpen(false);
          setShowInviteDialog(false);
          setInviteForm({
            email: '',
            name: '',
            role: 'user',
            tier: 'demo',
            initialBalance: 1000,
            inviteMessage: ''
          });
      },
      onError: (error: any) => {
        setAlert({ type: 'error', message: error?.message || 'Failed to send invitation' });
      }
    });
  };

  // Load admin data on component mount - React Query handles automatic refetching
  // Keep manual loading as fallback for initial load
  useEffect(() => {
    // React Query hooks handle automatic fetching on mount
    // They will automatically refetch based on their configured intervals (30-60 seconds)
    // Manual refetch calls are optional - hooks fetch automatically
    
    // Fallback: Also call manual load functions for compatibility
    const loadAllData = async () => {
      await loadAdminData();
      await checkLiveTradingStatus();
      await loadInvitations();
    };

    loadAllData();
  }, []);

  // Paper trading sessions are now handled by React Query hook (usePaperTradingSessions)
  // This effect is kept for backward compatibility but React Query handles the fetching
  useEffect(() => {
    // React Query hook handles fetching automatically
    // This is just for initial state setup
    if (!paperSessionsData) {
      setLoadingSessions(true);
    }
  }, [paperSessionsData]);

  // Load TAF analysis data
  const loadTAFAnalysis = async () => {
    try {
      setTafLoading(true);
      const response = await getJsonWithRetry(getApiUrl('/api/admin/taf-analysis'), {
        headers: { 'X-Admin-ID': user.id }
      });
      if (response?.success) {
        setTafData({
          currentFees: response.current_fees || 0,
          newFees: response.new_fees || 0,
          feeIncrease: response.fee_increase || 0,
          affectedTrades: response.affected_trades || 0,
          totalTrades: response.total_trades || 0,
          optimizationPotential: response.optimization_potential || 0
        });
      }
      } catch (error) {
        console.error('Error fetching TAF analysis:', error);
    } finally {
        setTafLoading(false);
      }
    };

  useEffect(() => {
    if (selectedSection === 'taf-analysis') {
      loadTAFAnalysis();
    }
  }, [selectedSection]);

  // Enhanced data loading functions for consolidated features
  const loadAuditData = async () => {
    try {
      setLoadingAudit(true);
      // Use React Query refetch if available
      if (refetchAuditLogs) {
        await refetchAuditLogs();
      } else {
        // Fallback to manual API call
      const response = await getJsonWithRetry(getApiUrl('/api/admin/audit-logs'), {
        headers: { 'X-Admin-ID': user.id }
      });
      if (response?.success) {
        setAuditLogs(response.logs || []);
        }
      }
    } catch (error) {
      console.error('Failed to load audit logs:', error);
    } finally {
      setLoadingAudit(false);
    }
  };

  const loadInvitations = async () => {
    try {
      // Use React Query refetch if available
      if (refetchInvitations) {
        await refetchInvitations();
      } else {
        // Fallback to manual API call
      const response = await getJsonWithRetry(getApiUrl('/api/admin/invitations'), {
        headers: { 'X-Admin-ID': user.id }
      });
      if (response?.success) {
        setInvitations(response.invitations || []);
        }
      }
    } catch (error) {
      console.error('Failed to load invitations:', error);
    }
  };

  const loadSystemHealthData = async () => {
    try {
      const response = await getJsonWithRetry(getApiUrl('/api/admin/system-health'), {
        headers: { 'X-Admin-ID': user.id }
      });
      if (response?.success) {
        setSystemHealth(response.health);
        setSystemMetrics(response.metrics || []);
      }
    } catch (error) {
      console.error('Failed to load system health:', error);
    }
  };

  const loadAdminData = async () => {
    try {
      setLoading(true);

      // Load admin dashboard metrics (with retries + fallbacks)
      const retryOpts = { retries: 3, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 } as const;
      let dashboardData: any | null = null;
      try {
        dashboardData = await getJsonWithRetry(getApiUrl('/api/public/admin/dashboard'), {}, retryOpts);
      } catch {
        try {
          dashboardData = await getJsonWithRetry(getApiUrl('/api/admin/dashboard'), { headers: { 'X-Admin-ID': user.id } }, retryOpts);
        } catch {
          try {
            dashboardData = await getJsonWithRetry(getApiUrl('/api/admin/dashboard-summary'), { headers: { 'X-Admin-ID': user.id } }, retryOpts);
          } catch {
            dashboardData = null;
          }
        }
      }

      if (dashboardData) {
        setAdminMetrics({
          totalUsers: dashboardData.total_users || 0,
          activeTraders: dashboardData.active_traders || 0,
          totalAllocated: dashboardData.total_allocated_funds || 0,
          totalPortfolioValue: dashboardData.total_portfolio_value || 0,
          dailyPnL: dashboardData.daily_pnl || 0,
          systemUptime: dashboardData.system_uptime || 0,
          pendingApprovals: dashboardData.pending_approvals || 0,
          activeSessions: dashboardData.active_sessions || 0
        });
      }

      // Load users data (with retries + fallback)
      let usersData: any | null = null;
      try {
        usersData = await getJsonWithRetry(getApiUrl('/api/public/admin/users'), {}, retryOpts);
      } catch {
        try {
          usersData = await getJsonWithRetry(getApiUrl('/api/admin/users'), { headers: { 'X-Admin-ID': user.id } }, retryOpts);
        } catch {
          usersData = null;
        }
      }

      if (usersData) {
        setUsers(Array.isArray(usersData) ? usersData : (usersData.users || []));
      }

    } catch (error) {
      console.error('Failed to load admin data:', error);
      setAlert({ type: 'error', message: 'Failed to load admin data' });
    } finally {
      setLoading(false);
    }
  };

  const handleAllocateFunds = async () => {
    if (!selectedUser || !allocationAmount) return;

      setLoading(true);
    // Use React Query mutation
    allocateFundsMutation.mutate({
      userId: selectedUser.id,
            amount: parseFloat(allocationAmount),
            reason: allocationReason
    }, {
      onSuccess: () => {
        setAlert({ type: 'success', message: `$${allocationAmount} allocated to ${selectedUser.username}` });
        setFundAllocationDialog(false);
        setAllocationAmount('');
        setAllocationReason('');
        setLoading(false);
      },
      onError: (error: any) => {
        setAlert({ type: 'error', message: error?.message || 'Failed to allocate funds' });
      setLoading(false);
    }
    });
  };

  // Navigation structure matching the user's screenshot requirements
  const navigationSections: NavigationSection[] = [
    {
      id: 'core',
      label: 'Core',
      icon: DashboardIcon,
      defaultOpen: true,
      children: [
        { id: 'dashboard', label: 'Dashboard', icon: DashboardIcon },
        { id: 'analytics', label: 'Analytics', icon: AnalyticsIcon },
        { id: 'notifications', label: 'Notifications', icon: NotificationsIcon, badge: 3 }
      ]
    },
    {
      id: 'trading',
      label: 'Trading',
      icon: TradingIcon,
      defaultOpen: true,
      children: [
        { id: 'paper-trading', label: 'Paper Trading', icon: TradingIcon },
        { id: 'live-trading', label: 'Live Trading', icon: TradingIcon, badge: 'LIVE', color: '#4caf50' },
        { id: 'portfolio', label: 'Portfolio', icon: PortfolioIcon }
      ]
    },
    {
      id: 'ai',
      label: 'AI & Advanced',
      icon: AIIcon,
      children: [
        { id: 'ai-systems', label: 'AI Systems', icon: AIIcon, badge: 'ACTIVE', color: '#9c27b0' },
        { id: 'revolutionary-ai', label: 'Revolutionary AI', icon: AIIcon, badge: 'NEW', color: '#00d4ff' },
        { id: 'hierarchical-agents', label: 'Hierarchical Agents', icon: AIIcon, badge: '17', color: '#9c27b0' },
        { id: 'market-opportunities', label: 'Market Opportunities', icon: ReportsIcon, badge: 'LIVE', color: '#4caf50' },
        { id: 'taf-analysis', label: 'TAF Fee Analysis', icon: ReportsIcon, badge: 'NEW', color: '#ff9800' },
        { id: 'strategy-management', label: 'Strategy Management', icon: ReportsIcon }
      ]
    },
    {
      id: 'admin',
      label: 'Administration',
      icon: AdminIcon,
      children: [
        { id: 'user-management', label: 'User Management', icon: UsersIcon, badge: 12 },
        { id: 'user-invitations', label: 'User Invitations', icon: Add, badge: invitations.filter(inv => inv.status === 'active').length },
        { id: 'fund-allocation', label: 'Fund Allocation', icon: PortfolioIcon },
        { id: 'permissions', label: 'Permissions', icon: SecurityIcon }
      ]
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: SettingsIcon,
      children: [
        { id: 'system-config', label: 'System Config', icon: SettingsIcon },
        { id: 'security', label: 'Security', icon: SecurityIcon },
        { id: 'audit-logs', label: 'Audit Logs', icon: ReportsIcon },
        { id: 'monitoring', label: 'System Monitoring', icon: MonitorIcon },
        { id: 'system-health', label: 'System Health', icon: MonitorIcon }
      ]
    }
  ];

  const toggleSection = (sectionId: string) => {
    setOpenSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  const handleItemSelect = (itemId: string) => {
    setSelectedSection(itemId);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercentage = (value: number | undefined) => {
    if (value === undefined || value === null || isNaN(value)) {
      return '0.00%';
    }
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  // Helper functions for consolidated features
  const getActionTypeColor = (actionType: string) => {
    switch (actionType) {
      case 'user_management': return '#4caf50';
      case 'fund_allocation': return '#ff9800';
      case 'trading_control': return '#f44336';
      case 'system_config': return '#9c27b0';
      default: return '#607d8b';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'approved': return 'success';
      case 'rejected': return 'error';
      case 'active': return 'success';
      default: return 'default';
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'admin': return '#f44336';
      case 'premium': return '#ff9800';
      case 'demo': return '#4caf50';
      default: return '#607d8b';
    }
  };

  const renderMainContent = () => {
    switch (selectedSection) {
      case 'dashboard':
        return renderDashboard();
      case 'user-management':
        return renderUserManagement();
      case 'user-invitations':
        return renderUserInvitations();
      case 'fund-allocation':
        return renderFundAllocation();
      case 'analytics':
        return renderAnalytics();
      case 'notifications':
        return renderNotifications();
      case 'live-trading':
        return renderLiveTrading();
      case 'paper-trading':
        return renderPaperTrading();
      case 'portfolio':
        return renderPortfolio();
      case 'ai-systems':
        return renderAISystems();
      // Phase 4: Revolutionary AI & Agent Monitoring - Lazy Loaded
      case 'revolutionary-ai':
        return (
          <Suspense fallback={<DefaultLoadingFallback />}>
            <RevolutionaryAIPanel />
          </Suspense>
        );
      case 'hierarchical-agents':
        return (
          <Suspense fallback={<DefaultLoadingFallback />}>
            <HierarchicalAgentMonitor />
          </Suspense>
        );
      case 'market-opportunities':
        return (
          <Suspense fallback={<DefaultLoadingFallback />}>
            <MarketOpportunitiesPanel />
          </Suspense>
        );
      case 'taf-analysis':
        return renderTAFAnalysis();
      case 'strategy-management':
        return renderStrategyManagement();
      case 'permissions':
        return renderPermissions();
      case 'system-config':
        return renderSystemConfig();
      case 'monitoring':
        return renderSystemMonitoring();
      case 'security':
        return renderSecurity();
      case 'audit-logs':
        return renderAuditLogs();
      case 'user-invitations':
        return renderUserInvitations();
      case 'system-health':
        return renderSystemHealth();
      default:
        return renderPlaceholder();
    }
  };

  const renderDashboard = () => {
    // Show skeleton loading if data is loading
    if (isLoadingData) {
      return (
    <Box>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {[1, 2, 3, 4].map((i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <Card sx={{
                  background: 'rgba(26, 26, 46, 0.8)',
                  border: '1px solid rgba(0, 212, 255, 0.2)',
                  borderRadius: 3,
                  animation: 'pulse 2s ease-in-out infinite',
                  '@keyframes pulse': {
                    '0%, 100%': { opacity: 1 },
                    '50%': { opacity: 0.6 }
                  }
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ height: 20, width: '60%', backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: 1, mb: 2 }} />
                        <Box sx={{ height: 32, width: '80%', backgroundColor: 'rgba(255, 255, 255, 0.15)', borderRadius: 1 }} />
                      </Box>
                      <Box sx={{ width: 40, height: 40, borderRadius: '50%', backgroundColor: 'rgba(255, 255, 255, 0.1)' }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
            <CircularProgress sx={{ color: '#00d4ff' }} />
          </Box>
        </Box>
      );
    }

    return (
      <Box role="region" aria-label="Admin Dashboard">
      {alert && (
          <Alert 
            severity={alert.type} 
            sx={{ 
              mb: 3,
              borderRadius: 2,
              animation: 'slideDown 0.3s ease-out',
              '@keyframes slideDown': {
                from: {
                  opacity: 0,
                  transform: 'translateY(-10px)'
                },
                to: {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              }
            }} 
            onClose={() => setAlert(null)}
          >
          {alert.message}
        </Alert>
      )}

      {/* Admin Metrics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }} role="group" aria-label="Admin Statistics">
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{
            background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)',
              border: '1px solid rgba(76, 175, 80, 0.3)',
              borderRadius: 3,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              animation: 'fadeInUp 0.6s ease-out',
              '@keyframes fadeInUp': {
                from: {
                  opacity: 0,
                  transform: 'translateY(20px)'
                },
                to: {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              },
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 12px 40px rgba(76, 175, 80, 0.3)',
                borderColor: 'rgba(76, 175, 80, 0.5)'
              }
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                    <Typography variant="h6" sx={{ color: '#4caf50', mb: 1, fontWeight: 600 }}>
                    Total Users
                  </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: 'white', fontFamily: 'monospace' }} aria-label={`${adminMetrics.totalUsers} total users`}>
                    {adminMetrics.totalUsers}
                  </Typography>
                </Box>
                  <UsersIcon sx={{ color: '#4caf50', fontSize: 40 }} aria-hidden="true" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{
            background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              borderRadius: 3,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              animation: 'fadeInUp 0.6s ease-out 0.1s both',
              '@keyframes fadeInUp': {
                from: {
                  opacity: 0,
                  transform: 'translateY(20px)'
                },
                to: {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              },
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 12px 40px rgba(0, 212, 255, 0.3)',
                borderColor: 'rgba(0, 212, 255, 0.5)'
              }
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                    <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1, fontWeight: 600 }}>
                    Total Allocated
                  </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: 'white', fontFamily: 'monospace' }} aria-label={`Total allocated funds: ${formatCurrency(adminMetrics.totalAllocated)}`}>
                    {formatCurrency(adminMetrics.totalAllocated)}
                  </Typography>
                </Box>
                  <AttachMoney sx={{ color: '#00d4ff', fontSize: 40 }} aria-hidden="true" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{
            background: 'linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(156, 39, 176, 0.05) 100%)',
              border: '1px solid rgba(156, 39, 176, 0.3)',
              borderRadius: 3,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              animation: 'fadeInUp 0.6s ease-out 0.2s both',
              '@keyframes fadeInUp': {
                from: {
                  opacity: 0,
                  transform: 'translateY(20px)'
                },
                to: {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              },
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 12px 40px rgba(156, 39, 176, 0.3)',
                borderColor: 'rgba(156, 39, 176, 0.5)'
              }
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                    <Typography variant="h6" sx={{ color: '#9c27b0', mb: 1, fontWeight: 600 }}>
                    Daily P&L
                  </Typography>
                  <Typography variant="h4" sx={{
                    fontWeight: 700,
                      color: adminMetrics.dailyPnL >= 0 ? '#4caf50' : '#f44336',
                      fontFamily: 'monospace'
                    }} aria-label={`Daily profit and loss: ${formatCurrency(adminMetrics.dailyPnL)}`}>
                    {formatCurrency(adminMetrics.dailyPnL)}
                  </Typography>
                </Box>
                  <TradingIcon sx={{ color: '#9c27b0', fontSize: 40 }} aria-hidden="true" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{
            background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%)',
              border: '1px solid rgba(255, 152, 0, 0.3)',
              borderRadius: 3,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              animation: 'fadeInUp 0.6s ease-out 0.3s both',
              '@keyframes fadeInUp': {
                from: {
                  opacity: 0,
                  transform: 'translateY(20px)'
                },
                to: {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              },
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 12px 40px rgba(255, 152, 0, 0.3)',
                borderColor: 'rgba(255, 152, 0, 0.5)'
              }
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6" sx={{ color: '#ff9800', mb: 1, fontWeight: 600 }}>
                    Pending Approvals
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: 'white', fontFamily: 'monospace' }} aria-label={`${adminMetrics.pendingApprovals} pending user approvals`}>
                    {adminMetrics.pendingApprovals}
                  </Typography>
                </Box>
                <Warning sx={{ color: '#ff9800', fontSize: 40 }} aria-hidden="true" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Card sx={{
        backgroundColor: 'rgba(26, 26, 46, 0.8)',
        border: '1px solid rgba(0, 212, 255, 0.2)',
          borderRadius: 3,
          mb: 3,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            borderColor: 'rgba(0, 212, 255, 0.4)',
            boxShadow: '0 4px 16px rgba(0, 212, 255, 0.15)'
          }
      }}>
        <CardContent>
            <Typography variant="h6" sx={{ color: '#00d4ff', mb: 3, fontWeight: 700 }}>
              ⚡ Quick Actions
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<UsersIcon />}
                onClick={() => setSelectedSection('user-management')}
                sx={{
                  borderColor: '#00d4ff',
                  color: '#00d4ff',
                    borderRadius: 2,
                    py: 1.5,
                    fontWeight: 600,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: 'rgba(0, 212, 255, 0.1)',
                      borderColor: '#00d4ff',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 4px 12px rgba(0, 212, 255, 0.3)'
                    }
                  }}
                  aria-label="Navigate to user management"
              >
                Manage Users
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<AttachMoney />}
                onClick={() => setSelectedSection('fund-allocation')}
                sx={{
                  borderColor: '#4caf50',
                  color: '#4caf50',
                    borderRadius: 2,
                    py: 1.5,
                    fontWeight: 600,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: 'rgba(76, 175, 80, 0.1)',
                      borderColor: '#4caf50',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 4px 12px rgba(76, 175, 80, 0.3)'
                    }
                  }}
                  aria-label="Navigate to fund allocation"
              >
                Allocate Funds
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<AnalyticsIcon />}
                onClick={() => setSelectedSection('analytics')}
                sx={{
                  borderColor: '#9c27b0',
                  color: '#9c27b0',
                    borderRadius: 2,
                    py: 1.5,
                    fontWeight: 600,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: 'rgba(156, 39, 176, 0.1)',
                      borderColor: '#9c27b0',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 4px 12px rgba(156, 39, 176, 0.3)'
                    }
                  }}
                  aria-label="Navigate to analytics"
              >
                View Analytics
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadAdminData}
                  disabled={isLoadingData}
                sx={{
                  borderColor: '#ff9800',
                  color: '#ff9800',
                    borderRadius: 2,
                    py: 1.5,
                    fontWeight: 600,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 152, 0, 0.1)',
                      borderColor: '#ff9800',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 4px 12px rgba(255, 152, 0, 0.3)'
                    },
                    '&:disabled': {
                      borderColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'rgba(255, 255, 255, 0.3)'
                    }
                  }}
                  aria-label="Refresh dashboard data"
              >
                Refresh Data
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );

  const renderFundAllocation = () => (
    <Box>
      {alert && (
        <Alert severity={alert.type} sx={{ mb: 3 }} onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      <Card sx={{
        backgroundColor: 'rgba(26, 26, 46, 0.8)',
        border: '1px solid rgba(0, 212, 255, 0.2)'
      }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ color: '#00d4ff' }}>
              💰 Fund Allocation Management
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => {
                if (users.length > 0) {
                  setSelectedUser(users[0]);
                  setFundAllocationDialog(true);
                }
              }}
              sx={{ background: 'linear-gradient(45deg, #00d4ff, #0099cc)' }}
            >
              Allocate Funds
            </Button>
          </Box>

          {isLoadingData && <LinearProgress sx={{ mb: 2 }} />}

          <TableContainer component={Paper} sx={{ background: 'rgba(42, 42, 42, 0.5)' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: '#aaa' }}>User</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Status</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Allocated</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Current Value</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>P&L</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Live Trading</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: user.tier === 'admin' ? '#9c27b0' : '#00d4ff' }}>
                          {user.username.charAt(0).toUpperCase()}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600, color: 'white' }}>
                            {user.username}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                            {user.email}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.status.toUpperCase()}
                        size="small"
                        sx={{
                          backgroundColor: user.status === 'active' ? '#4caf50' : '#ff9800',
                          color: '#fff',
                          fontWeight: 500
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography sx={{ color: 'white', fontWeight: 600 }}>
                        {formatCurrency(user.allocatedFunds)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography sx={{ color: 'white' }}>
                        {formatCurrency(user.currentValue)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography sx={{
                          color: user.pnl >= 0 ? '#4caf50' : '#f44336',
                          fontWeight: 600
                        }}>
                          {formatCurrency(user.pnl)}
                        </Typography>
                        <Typography variant="caption" sx={{
                          color: user.pnlPercentage >= 0 ? '#4caf50' : '#f44336'
                        }}>
                          {formatPercentage(user.pnlPercentage)}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.liveTrading ? 'ACTIVE' : 'PAPER ONLY'}
                        size="small"
                        sx={{
                          backgroundColor: user.liveTrading ? '#4caf50' : '#ff9800',
                          color: '#fff',
                          fontWeight: 500
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Allocate Funds">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedUser(user);
                              setFundAllocationDialog(true);
                            }}
                            sx={{ color: '#00d4ff' }}
                          >
                            <AttachMoney />
                          </IconButton>
                        </Tooltip>
                        {user.allocatedFunds > 0 && !user.liveTrading && (
                          <Tooltip title="Activate Live Trading">
                            <IconButton
                              size="small"
                              sx={{ color: '#4caf50' }}
                            >
                              <PlayArrow />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="View Details">
                          <IconButton size="small" sx={{ color: '#ff9800' }}>
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Fund Allocation Dialog */}
      <Dialog
        open={fundAllocationDialog}
        onClose={() => setFundAllocationDialog(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(26, 26, 46, 0.95)',
            border: '1px solid rgba(0, 212, 255, 0.3)'
          }
        }}
      >
        <DialogTitle sx={{ color: '#00d4ff' }}>
          💰 Allocate Funds to {selectedUser?.username}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Allocation Amount ($)"
              type="number"
              value={allocationAmount}
              onChange={(e) => setAllocationAmount(e.target.value)}
              sx={{
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                  '&:hover fieldset': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                  '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                },
                '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' }
              }}
            />
            <TextField
              fullWidth
              label="Reason for Allocation"
              multiline
              rows={3}
              value={allocationReason}
              onChange={(e) => setAllocationReason(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                  '&:hover fieldset': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                  '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                },
                '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' }
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFundAllocationDialog(false)} sx={{ color: '#aaa' }}>
            Cancel
          </Button>
          <Button
            onClick={handleAllocateFunds}
            variant="contained"
            disabled={!allocationAmount || loading}
            sx={{ background: 'linear-gradient(45deg, #00d4ff, #0099cc)' }}
          >
            Allocate Funds
          </Button>
        </DialogActions>
      </Dialog>

      {/* Enhanced Fund Allocation Dialog */}
      <Dialog
        open={fundAllocationDialog}
        onClose={() => setFundAllocationDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 3,
            animation: 'dialogSlideIn 0.3s ease-out',
            '@keyframes dialogSlideIn': {
              from: {
                opacity: 0,
                transform: 'scale(0.9) translateY(-20px)'
              },
              to: {
                opacity: 1,
                transform: 'scale(1) translateY(0)'
              }
            }
          }
        }}
      >
        <DialogTitle sx={{ color: '#00d4ff', fontWeight: 700 }}>
          💰 Fund Allocation - {selectedUser?.username || selectedUser?.name}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            {/* User Information */}
            <Grid item xs={12}>
              <Card sx={{ background: 'rgba(0, 212, 255, 0.1)', border: '1px solid rgba(0, 212, 255, 0.3)', mb: 2 }}>
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" sx={{ color: '#aaa', mb: 0.5 }}>User Details</Typography>
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                        {selectedUser?.username || selectedUser?.name}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#aaa' }}>
                        {selectedUser?.email}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" sx={{ color: '#aaa', mb: 0.5 }}>Current Tier</Typography>
                      <Chip
                        label={(selectedUser?.tier || 'demo').toUpperCase()}
                        sx={{
                          backgroundColor: getTierColor(selectedUser?.tier || 'demo'),
                          color: 'white',
                          fontWeight: 600
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" sx={{ color: '#aaa', mb: 0.5 }}>Current Allocation</Typography>
                      <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                        {formatCurrency(selectedUser?.allocatedFunds || selectedUser?.current_allocation || 0)}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Allocation Amount */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Allocation Amount"
                type="number"
                value={allocationAmount}
                onChange={(e) => setAllocationAmount(e.target.value)}
                InputProps={{
                  startAdornment: <Typography sx={{ color: '#00d4ff', mr: 1 }}>$</Typography>
                }}
                helperText="Enter the amount to allocate to this user"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    '& fieldset': { borderColor: 'rgba(0, 212, 255, 0.3)' }
                  }
                }}
              />
            </Grid>

            {/* Risk Parameters */}
            <Grid item xs={12} md={6}>
              <TextField
                select
                fullWidth
                label="Risk Level"
                defaultValue="moderate"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    '& fieldset': { borderColor: 'rgba(0, 212, 255, 0.3)' }
                  }
                }}
              >
                <MenuItem value="conservative">Conservative (2% daily limit)</MenuItem>
                <MenuItem value="moderate">Moderate (5% daily limit)</MenuItem>
                <MenuItem value="aggressive">Aggressive (10% daily limit)</MenuItem>
              </TextField>
            </Grid>

            {/* Allocation Reason */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Allocation Reason"
                value={allocationReason}
                onChange={(e) => setAllocationReason(e.target.value)}
                placeholder="Provide a reason for this fund allocation..."
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    '& fieldset': { borderColor: 'rgba(0, 212, 255, 0.3)' }
                  }
                }}
              />
            </Grid>

            {/* Trading Permissions */}
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>
                Trading Permissions
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Card sx={{ background: 'rgba(76, 175, 80, 0.1)', border: '1px solid rgba(76, 175, 80, 0.3)', textAlign: 'center', p: 2 }}>
                    <Typography variant="body2" sx={{ color: '#4caf50', fontWeight: 600 }}>
                      Paper Trading
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>
                      Always Available
                    </Typography>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card sx={{ background: 'rgba(255, 152, 0, 0.1)', border: '1px solid rgba(255, 152, 0, 0.3)', textAlign: 'center', p: 2 }}>
                    <Typography variant="body2" sx={{ color: '#ff9800', fontWeight: 600 }}>
                      Live Trading
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>
                      Requires Allocation
                    </Typography>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card sx={{ background: 'rgba(156, 39, 176, 0.1)', border: '1px solid rgba(156, 39, 176, 0.3)', textAlign: 'center', p: 2 }}>
                    <Typography variant="body2" sx={{ color: '#9c27b0', fontWeight: 600 }}>
                      Advanced Features
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>
                      Premium Tier Only
                    </Typography>
                  </Card>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFundAllocationDialog(false)} sx={{ color: '#aaa' }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleAllocateFunds}
            disabled={loading || !allocationAmount}
            sx={{
              background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
              '&:hover': { background: 'linear-gradient(45deg, #0099cc, #007aa3)' }
            }}
          >
            {loading || allocateFundsMutation?.isPending ? 'Allocating...' : `Allocate ${allocationAmount ? formatCurrency(parseFloat(allocationAmount)) : '$0'}`}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  // Memoized filtered users calculation - moved outside render function for performance
  const filteredUsers = useMemo(() => {
    return users.filter(u => {
      // Status filter
      if (userFilter !== 'all') {
        if (userFilter === 'pending' && u.status !== 'pending') return false;
        if (userFilter === 'active' && u.status !== 'active') return false;
        if (userFilter === 'live' && !u.liveTrading) return false;
        if (userFilter === 'suspended' && u.status !== 'suspended') return false;
      }

      // Search filter
      if (userSearchQuery) {
        const query = userSearchQuery.toLowerCase();
        const matchesSearch = 
          u.username?.toLowerCase().includes(query) ||
          u.email?.toLowerCase().includes(query) ||
          u.name?.toLowerCase().includes(query) ||
          u.id?.toLowerCase().includes(query);
        if (!matchesSearch) return false;
      }

      return true;
    });
  }, [users, userFilter, userSearchQuery]);

  // Memoized helper function
  const getTierColor = useCallback((tier: string) => {
    switch (tier) {
      case 'admin': return '#9c27b0';
      case 'live_approved': return '#4caf50';
      case 'paper_only': return '#ff9800';
      default: return '#00d4ff';
    }
  }, []);

  const renderUserManagement = () => {

    const handleApproveUser = async (userId: string, username?: string) => {
      setConfirmDialog({
        open: true,
        title: 'Approve User',
        message: `Are you sure you want to approve ${username || 'this user'}? This will grant them access to the platform.`,
        onConfirm: async () => {
      try {
        setLoading(true);
        const retryOpts = { retries: 3, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 } as const;
        try {
          await getJsonWithRetry(getApiUrl('/api/admin/approve-user'), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Admin-ID': user.id
            },
            body: JSON.stringify({ user_id: userId })
          }, retryOpts);

              setAlert({ type: 'success', message: `User ${username || 'approved'} successfully approved` });
          loadAdminData();
              refetchUsers();
        } catch (err) {
          setAlert({ type: 'error', message: (err as any)?.message || 'Failed to approve user' });
        }
      } catch (error) {
        setAlert({ type: 'error', message: 'Failed to approve user' });
      } finally {
        setLoading(false);
            setConfirmDialog({ open: false, title: '', message: '', onConfirm: () => {} });
          }
        }
      });
    };

    const handleRejectUser = async (userId: string, username?: string) => {
      setConfirmDialog({
        open: true,
        title: 'Reject User',
        message: `Are you sure you want to reject ${username || 'this user'}? This action cannot be undone.`,
        onConfirm: async () => {
      try {
        setLoading(true);
        const retryOpts = { retries: 3, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 } as const;
        try {
          await getJsonWithRetry(getApiUrl('/api/admin/reject-user'), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Admin-ID': user.id
            },
            body: JSON.stringify({ user_id: userId })
          }, retryOpts);

              setAlert({ type: 'success', message: `User ${username || 'rejected'} successfully rejected` });
          loadAdminData();
              refetchUsers();
        } catch (err) {
          setAlert({ type: 'error', message: (err as any)?.message || 'Failed to reject user' });
        }
      } catch (error) {
        setAlert({ type: 'error', message: 'Failed to reject user' });
      } finally {
        setLoading(false);
            setConfirmDialog({ open: false, title: '', message: '', onConfirm: () => {} });
      }
        }
      });
    };

    const handleInviteUser = async () => {
      if (!inviteForm.email || !inviteForm.name) return;

      try {
        setLoading(true);
        const retryOpts = { retries: 3, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 } as const;
        try {
          const result = await getJsonWithRetry(getApiUrl('/api/admin/invite-user'), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Admin-ID': user.id
            },
            body: JSON.stringify({
              email: inviteForm.email,
              name: inviteForm.name,
              tier: inviteForm.tier,
              initial_balance: inviteForm.initialBalance
            })
          }, retryOpts);

          setAlert({
            type: 'success',
            message: `Invitation sent to ${inviteForm.email}. Code: ${result.invitation_code}`
          });
          setInviteDialogOpen(false);
          setInviteForm({ email: '', name: '', role: 'user', tier: 'demo', initialBalance: 1000, inviteMessage: '' });
          loadAdminData();
        } catch (err) {
          setAlert({ type: 'error', message: (err as any)?.message || 'Failed to send invitation' });
        }
      } catch (error) {
        setAlert({ type: 'error', message: 'Failed to send invitation' });
      } finally {
        setLoading(false);
      }
    };

    return (
      <Box>
        {alert && (
          <Alert 
            severity={alert.type} 
            sx={{ 
              mb: 3,
              borderRadius: 2,
              animation: 'slideDown 0.3s ease-out',
              '@keyframes slideDown': {
                from: {
                  opacity: 0,
                  transform: 'translateY(-10px)'
                },
                to: {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              }
            }} 
            onClose={() => setAlert(null)}
          >
            {alert.message}
          </Alert>
        )}

        <Card sx={{
          backgroundColor: 'rgba(26, 26, 46, 0.8)',
          border: '1px solid rgba(0, 212, 255, 0.2)',
          borderRadius: 2,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: '0 8px 24px rgba(0, 212, 255, 0.15)',
            borderColor: 'rgba(0, 212, 255, 0.4)',
            transform: 'translateY(-2px)'
          }
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
              <Box>
                <Typography variant="h5" sx={{ color: '#00d4ff', fontWeight: 600, mb: 0.5 }}>
                👥 User Management & Approvals
              </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                  {filteredUsers.length} of {users.length} users {userSearchQuery || userFilter !== 'all' ? '(filtered)' : ''}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                {/* Search Box */}
                <TextField
                  size="small"
                  placeholder="Search users..."
                  value={userSearchQuery}
                  onChange={(e) => setUserSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: <Search sx={{ color: 'rgba(255, 255, 255, 0.5)', mr: 1 }} />
                  }}
                  sx={{
                    minWidth: 200,
                    '& .MuiOutlinedInput-root': {
                      color: 'white',
                      '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                      '&:hover fieldset': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                      '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                    },
                    '& .MuiInputBase-input::placeholder': { color: 'rgba(255, 255, 255, 0.5)' }
                  }}
                />
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Filter</InputLabel>
                  <Select
                    value={userFilter}
                    onChange={(e) => setUserFilter(e.target.value)}
                    sx={{
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                      '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                      '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' }
                    }}
                  >
                    <MenuItem value="all">All Users</MenuItem>
                    <MenuItem value="pending">Pending</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="live">Live Trading</MenuItem>
                    <MenuItem value="suspended">Suspended</MenuItem>
                  </Select>
                </FormControl>
                <Box>
                  <Button
                    variant="outlined"
                    startIcon={<FileDownload />}
                    onClick={(e) => setExportMenuAnchor(e.currentTarget)}
                    disabled={filteredUsers.length === 0}
                    sx={{
                      borderColor: '#4caf50',
                      color: '#4caf50',
                      transition: 'all 0.2s ease',
                      '&:hover': { 
                        borderColor: '#4caf50', 
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 4px 8px rgba(76, 175, 80, 0.3)'
                      },
                      '&:disabled': {
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        color: 'rgba(255, 255, 255, 0.3)'
                      }
                    }}
                  >
                    Export
                  </Button>
                  <Menu
                    anchorEl={exportMenuAnchor}
                    open={Boolean(exportMenuAnchor)}
                    onClose={() => setExportMenuAnchor(null)}
                    PaperProps={{
                      sx: {
                        backgroundColor: 'rgba(26, 26, 46, 0.95)',
                        border: '1px solid rgba(0, 212, 255, 0.3)',
                        mt: 1
                      }
                    }}
                  >
                    <MenuItem onClick={() => { exportUsers(filteredUsers, 'csv'); setExportMenuAnchor(null); }} sx={{ color: 'white' }}>
                      Export as CSV
                    </MenuItem>
                    <MenuItem onClick={() => { exportUsers(filteredUsers, 'json'); setExportMenuAnchor(null); }} sx={{ color: 'white' }}>
                      Export as JSON
                    </MenuItem>
                    <MenuItem onClick={async () => { 
                      const formatted = filteredUsers.map(u => ({
                        'User ID': u.id,
                        'Username': u.username,
                        'Email': u.email,
                        'Status': u.status,
                        'Tier': u.tier,
                        'Allocated Funds': u.allocatedFunds,
                        'P&L': u.pnl
                      }));
                      await exportToPDF(formatted, `prometheus-users-${new Date().toISOString().slice(0, 10)}`, 'User Export');
                      setExportMenuAnchor(null);
                    }} sx={{ color: 'white' }}>
                      Export as PDF
                    </MenuItem>
                    <MenuItem onClick={async () => { 
                      const formatted = filteredUsers.map(u => ({
                        'User ID': u.id,
                        'Username': u.username,
                        'Email': u.email,
                        'Status': u.status,
                        'Tier': u.tier,
                        'Allocated Funds': u.allocatedFunds,
                        'P&L': u.pnl
                      }));
                      await exportToExcel(formatted, `prometheus-users-${new Date().toISOString().slice(0, 10)}`);
                      setExportMenuAnchor(null);
                    }} sx={{ color: 'white' }}>
                      Export as Excel
                    </MenuItem>
                  </Menu>
                </Box>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setInviteDialogOpen(true)}
                  sx={{ 
                    background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #0099cc, #007aa3)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 6px 12px rgba(0, 212, 255, 0.4)'
                    }
                  }}
                >
                  Invite User
                </Button>
              </Box>
            </Box>

            {isLoadingData && (
              <LinearProgress 
                sx={{ 
                  mb: 2,
                  height: 4,
                  borderRadius: 2,
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    background: 'linear-gradient(90deg, #00d4ff, #0099cc)',
                    borderRadius: 2
                  }
                }} 
              />
            )}

            {/* Bulk Actions */}
            {selectedUserIds.length > 0 && (
              <Box 
                sx={{ 
                  mb: 2, 
                  p: 2, 
                  backgroundColor: 'rgba(0, 212, 255, 0.1)', 
                  borderRadius: 2, 
                  border: '1px solid rgba(0, 212, 255, 0.3)',
                  animation: 'slideDown 0.3s ease-out',
                  '@keyframes slideDown': {
                    from: {
                      opacity: 0,
                      transform: 'translateY(-10px)'
                    },
                    to: {
                      opacity: 1,
                      transform: 'translateY(0)'
                    }
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                  <Chip 
                    label={`${selectedUserIds.length} user(s) selected`}
                    sx={{ 
                      backgroundColor: 'rgba(0, 212, 255, 0.2)',
                      color: '#00d4ff',
                      fontWeight: 600
                    }}
                  />
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<CheckCircle />}
                    onClick={() => {
                      setConfirmDialog({
                        open: true,
                        title: 'Approve Selected Users',
                        message: `Are you sure you want to approve ${selectedUserIds.length} user(s)? This will grant them access to the platform.`,
                        onConfirm: async () => {
                          try {
                            setLoading(true);
                            await Promise.all(selectedUserIds.map(id => 
                              getJsonWithRetry(getApiUrl('/api/admin/approve-user'), {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json', 'X-Admin-ID': user.id },
                                body: JSON.stringify({ user_id: id })
                              })
                            ));
                            setAlert({ type: 'success', message: `Approved ${selectedUserIds.length} user(s) successfully` });
                            setSelectedUserIds([]);
                            refetchUsers();
                          } catch (error) {
                            setAlert({ type: 'error', message: 'Failed to approve users' });
                          } finally {
                            setLoading(false);
                            setConfirmDialog({ open: false, title: '', message: '', onConfirm: () => {} });
                          }
                        }
                      });
                    }}
                    sx={{ 
                      borderColor: '#4caf50', 
                      color: '#4caf50',
                      transition: 'all 0.2s ease',
                      '&:hover': { 
                        borderColor: '#4caf50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 4px 8px rgba(76, 175, 80, 0.3)'
                      }
                    }}
                  >
                    Approve Selected
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<Cancel />}
                    onClick={() => {
                      setConfirmDialog({
                        open: true,
                        title: 'Reject Selected Users',
                        message: `Are you sure you want to reject ${selectedUserIds.length} user(s)? This action cannot be undone.`,
                        onConfirm: async () => {
                          try {
                            setLoading(true);
                            await Promise.all(selectedUserIds.map(id => 
                              getJsonWithRetry(getApiUrl('/api/admin/reject-user'), {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json', 'X-Admin-ID': user.id },
                                body: JSON.stringify({ user_id: id })
                              })
                            ));
                            setAlert({ type: 'success', message: `Rejected ${selectedUserIds.length} user(s) successfully` });
                            setSelectedUserIds([]);
                            refetchUsers();
                          } catch (error) {
                            setAlert({ type: 'error', message: 'Failed to reject users' });
                          } finally {
                            setLoading(false);
                            setConfirmDialog({ open: false, title: '', message: '', onConfirm: () => {} });
                          }
                        }
                      });
                    }}
                    sx={{ 
                      borderColor: '#f44336', 
                      color: '#f44336',
                      transition: 'all 0.2s ease',
                      '&:hover': { 
                        borderColor: '#f44336',
                        backgroundColor: 'rgba(244, 67, 54, 0.1)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 4px 8px rgba(244, 67, 54, 0.3)'
                      }
                    }}
                  >
                    Reject Selected
                  </Button>
                  <Button
                    size="small"
                    variant="text"
                    onClick={() => setSelectedUserIds([])}
                    sx={{ 
                      color: '#aaa',
                      transition: 'all 0.2s ease',
                      '&:hover': { 
                        color: '#fff',
                        backgroundColor: 'rgba(255, 255, 255, 0.05)'
                      }
                    }}
                  >
                    Clear Selection
                  </Button>
                </Box>
              </Box>
            )}

            <TableContainer 
              component={Paper} 
              sx={{ 
                background: 'rgba(42, 42, 42, 0.5)',
                borderRadius: 2,
                overflow: 'hidden',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}
            >
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: 'rgba(0, 212, 255, 0.05)' }}>
                    <TableCell padding="checkbox" sx={{ color: '#aaa', fontWeight: 600 }}>
                      <Checkbox
                        indeterminate={selectedUserIds.length > 0 && selectedUserIds.length < filteredUsers.length}
                        checked={filteredUsers.length > 0 && selectedUserIds.length === filteredUsers.length}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedUserIds(filteredUsers.map(u => u.id));
                          } else {
                            setSelectedUserIds([]);
                          }
                        }}
                        sx={{ 
                          color: '#00d4ff', 
                          '&.Mui-checked': { color: '#00d4ff' },
                          transition: 'all 0.2s ease'
                        }}
                      />
                    </TableCell>
                    <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>User</TableCell>
                    <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>Status</TableCell>
                    <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>Tier</TableCell>
                    <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>Allocated</TableCell>
                    <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>P&L</TableCell>
                    <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>Last Activity</TableCell>
                    <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredUsers.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} sx={{ textAlign: 'center', py: 6 }}>
                        <Box sx={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          gap: 2,
                          animation: 'fadeIn 0.5s ease-out',
                          '@keyframes fadeIn': {
                            from: { opacity: 0 },
                            to: { opacity: 1 }
                          }
                        }}>
                          <Box sx={{
                            width: 64,
                            height: 64,
                            borderRadius: '50%',
                            backgroundColor: 'rgba(0, 212, 255, 0.1)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            mb: 1
                          }}>
                            <UsersIcon sx={{ fontSize: 32, color: 'rgba(0, 212, 255, 0.5)' }} />
                          </Box>
                          <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 600 }}>
                            No users found
                          </Typography>
                          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                            {userSearchQuery || userFilter !== 'all' 
                              ? 'Try adjusting your search or filter criteria'
                              : 'No users match the current criteria'}
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ) : (
                      filteredUsers.map((u, index) => (
                        <TableRow
                          key={u.id}
                          hover
                          sx={{
                            transition: 'all 0.2s ease',
                            animation: `fadeInRow 0.3s ease-out ${index * 0.03}s both`,
                            '@keyframes fadeInRow': {
                              from: {
                                opacity: 0,
                                transform: 'translateX(-10px)'
                              },
                              to: {
                                opacity: 1,
                                transform: 'translateX(0)'
                              }
                            },
                            '&:hover': {
                              backgroundColor: 'rgba(0, 212, 255, 0.05)',
                              transform: 'scale(1.001)',
                              boxShadow: '0 2px 8px rgba(0, 212, 255, 0.1)'
                            }
                          }}
                        >
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedUserIds.includes(u.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedUserIds([...selectedUserIds, u.id]);
                            } else {
                              setSelectedUserIds(selectedUserIds.filter(id => id !== u.id));
                            }
                          }}
                          sx={{ color: '#00d4ff', '&.Mui-checked': { color: '#00d4ff' } }}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Avatar 
                            sx={{ 
                              bgcolor: getTierColor(u.tier),
                              width: 40,
                              height: 40,
                              transition: 'all 0.2s ease',
                              '&:hover': {
                                transform: 'scale(1.1)',
                                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
                              }
                            }}
                          >
                            {u.username.charAt(0).toUpperCase()}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 600, color: 'white', mb: 0.5 }}>
                              {u.username}
                            </Typography>
                            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                              {u.email}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={u.status.toUpperCase()}
                          size="small"
                          sx={{
                            backgroundColor: u.status === 'active' ? '#4caf50' :
                                           u.status === 'pending' ? '#ff9800' : '#f44336',
                            color: '#fff',
                            fontWeight: 500
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={u.tier.replace('_', ' ').toUpperCase()}
                          size="small"
                          sx={{
                            backgroundColor: getTierColor(u.tier),
                            color: '#fff',
                            fontWeight: 500
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography sx={{ 
                          color: 'white', 
                          fontWeight: 600,
                          fontFamily: 'monospace'
                        }}>
                          {formatCurrency(u.allocatedFunds)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box>
                        <Typography sx={{
                          color: u.pnl >= 0 ? '#4caf50' : '#f44336',
                            fontWeight: 700,
                            fontFamily: 'monospace',
                            fontSize: '0.95rem'
                        }}>
                            {formatCurrency(u.pnl)}
                        </Typography>
                          <Typography variant="caption" sx={{
                            color: u.pnl >= 0 ? 'rgba(76, 175, 80, 0.8)' : 'rgba(244, 67, 54, 0.8)',
                            fontWeight: 500
                          }}>
                            {formatPercentage(u.pnlPercentage)}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" sx={{ 
                          color: 'rgba(255, 255, 255, 0.7)',
                          fontStyle: u.lastActivity ? 'normal' : 'italic'
                        }}>
                          {u.lastActivity || 'Never'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          {u.status === 'pending' && (
                            <>
                              <Tooltip title="Approve User" arrow>
                                <IconButton
                                  size="small"
                                  onClick={() => handleApproveUser(u.id, u.username)}
                                  sx={{ 
                                    color: '#4caf50',
                                    transition: 'all 0.2s ease',
                                    '&:hover': { 
                                      backgroundColor: 'rgba(76, 175, 80, 0.1)',
                                      transform: 'scale(1.1)'
                                    }
                                  }}
                                >
                                  <CheckCircle />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Reject User" arrow>
                                <IconButton
                                  size="small"
                                  onClick={() => handleRejectUser(u.id, u.username)}
                                  sx={{ 
                                    color: '#f44336',
                                    transition: 'all 0.2s ease',
                                    '&:hover': { 
                                      backgroundColor: 'rgba(244, 67, 54, 0.1)',
                                      transform: 'scale(1.1)'
                                    }
                                  }}
                                >
                                  <Cancel />
                                </IconButton>
                              </Tooltip>
                            </>
                          )}
                          <Tooltip title="Allocate Funds" arrow>
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedUser(u);
                                setFundAllocationDialog(true);
                              }}
                              sx={{ 
                                color: '#00d4ff',
                                transition: 'all 0.2s ease',
                                '&:hover': { 
                                  backgroundColor: 'rgba(0, 212, 255, 0.1)',
                                  transform: 'scale(1.1)'
                                }
                              }}
                            >
                              <AttachMoney />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="View Details" arrow>
                            <IconButton 
                              size="small" 
                              sx={{ 
                                color: '#ff9800',
                                transition: 'all 0.2s ease',
                                '&:hover': { 
                                  backgroundColor: 'rgba(255, 152, 0, 0.1)',
                                  transform: 'scale(1.1)'
                                }
                              }}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit User" arrow>
                            <IconButton 
                              size="small" 
                              sx={{ 
                                color: '#9c27b0',
                                transition: 'all 0.2s ease',
                                '&:hover': { 
                                  backgroundColor: 'rgba(156, 39, 176, 0.1)',
                                  transform: 'scale(1.1)'
                                }
                              }}
                              onClick={() => {
                                setEditUserForm({
                                  id: u.id,
                                  username: u.username,
                                  email: u.email,
                                  name: u.name,
                                  tier: u.tier,
                                  status: u.status
                                });
                                setEditUserDialog(true);
                              }}
                            >
                              <Edit />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        {/* Edit User Dialog */}
        <Dialog
          open={editUserDialog}
          onClose={() => {
            setEditUserDialog(false);
            setEditUserForm(null);
          }}
          maxWidth="sm"
          fullWidth
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(26, 26, 46, 0.95)',
            border: '1px solid rgba(156, 39, 176, 0.3)',
            borderRadius: 3,
            animation: 'dialogSlideIn 0.3s ease-out',
            '@keyframes dialogSlideIn': {
              from: {
                opacity: 0,
                transform: 'scale(0.9) translateY(-20px)'
              },
              to: {
                opacity: 1,
                transform: 'scale(1) translateY(0)'
              }
            }
          }
        }}
      >
        <DialogTitle sx={{ color: '#9c27b0', fontWeight: 700 }}>
          ✏️ Edit User
        </DialogTitle>
          <DialogContent>
            {editUserForm && (
              <Box sx={{ pt: 2 }}>
                <TextField
                  fullWidth
                  label="Username"
                  value={editUserForm.username}
                  onChange={(e) => setEditUserForm({ ...editUserForm, username: e.target.value })}
                  sx={{
                    mb: 3,
                    '& .MuiOutlinedInput-root': { color: 'white', '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' } },
                    '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' }
                  }}
                />
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={editUserForm.email}
                  onChange={(e) => setEditUserForm({ ...editUserForm, email: e.target.value })}
                  sx={{
                    mb: 3,
                    '& .MuiOutlinedInput-root': { color: 'white', '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' } },
                    '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' }
                  }}
                />
                <TextField
                  fullWidth
                  label="Name"
                  value={editUserForm.name || ''}
                  onChange={(e) => setEditUserForm({ ...editUserForm, name: e.target.value })}
                  sx={{
                    mb: 3,
                    '& .MuiOutlinedInput-root': { color: 'white', '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' } },
                    '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' }
                  }}
                />
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Tier</InputLabel>
                  <Select
                    value={editUserForm.tier}
                    onChange={(e) => setEditUserForm({ ...editUserForm, tier: e.target.value })}
                    label="Tier"
                    sx={{
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                      '& .MuiSvgIcon-root': { color: 'rgba(255, 255, 255, 0.7)' }
                    }}
                  >
                    <MenuItem value="demo">Demo</MenuItem>
                    <MenuItem value="paper_only">Paper Only</MenuItem>
                    <MenuItem value="live_approved">Live Approved</MenuItem>
                    <MenuItem value="admin">Admin</MenuItem>
                  </Select>
                </FormControl>
                <FormControl fullWidth>
                  <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Status</InputLabel>
                  <Select
                    value={editUserForm.status}
                    onChange={(e) => setEditUserForm({ ...editUserForm, status: e.target.value })}
                    label="Status"
                    sx={{
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                      '& .MuiSvgIcon-root': { color: 'rgba(255, 255, 255, 0.7)' }
                    }}
                  >
                    <MenuItem value="pending">Pending</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="suspended">Suspended</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => {
              setEditUserDialog(false);
              setEditUserForm(null);
            }} sx={{ color: '#aaa' }}>
              Cancel
            </Button>
            <Button
              onClick={async () => {
                if (!editUserForm) return;
                try {
                  setLoading(true);
                  await getJsonWithRetry(getApiUrl(`/api/admin/users/${editUserForm.id}`), {
                    method: 'PUT',
                    headers: {
                      'Content-Type': 'application/json',
                      'X-Admin-ID': user.id
                    },
                    body: JSON.stringify({
                      username: editUserForm.username,
                      email: editUserForm.email,
                      name: editUserForm.name,
                      tier: editUserForm.tier,
                      status: editUserForm.status
                    })
                  });
                  setAlert({ type: 'success', message: 'User updated successfully' });
                  setEditUserDialog(false);
                  setEditUserForm(null);
                  refetchUsers();
                } catch (error) {
                  setAlert({ type: 'error', message: 'Failed to update user' });
                } finally {
                  setLoading(false);
                }
              }}
              variant="contained"
              disabled={!editUserForm || loading}
              sx={{ background: 'linear-gradient(45deg, #9c27b0, #7b1fa2)' }}
            >
              Save Changes
            </Button>
          </DialogActions>
        </Dialog>

        {/* User Invitation Dialog */}
        <Dialog
          open={inviteDialogOpen}
          onClose={() => setInviteDialogOpen(false)}
          maxWidth="sm"
          fullWidth
          PaperProps={{
            sx: {
              backgroundColor: 'rgba(26, 26, 46, 0.95)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 3,
            animation: 'dialogSlideIn 0.3s ease-out',
            '@keyframes dialogSlideIn': {
              from: {
                opacity: 0,
                transform: 'scale(0.9) translateY(-20px)'
              },
              to: {
                opacity: 1,
                transform: 'scale(1) translateY(0)'
              }
            }
          }
        }}
      >
        <DialogTitle sx={{ color: '#00d4ff', fontWeight: 700 }}>
            👥 Invite New User
          </DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <TextField
                fullWidth
                label="Email Address"
                type="email"
                value={inviteForm.email}
                onChange={(e) => setInviteForm(prev => ({ ...prev, email: e.target.value }))}
                sx={{
                  mb: 3,
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '&:hover fieldset': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                    '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                  },
                  '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' }
                }}
              />
              <TextField
                fullWidth
                label="Full Name"
                value={inviteForm.name}
                onChange={(e) => setInviteForm(prev => ({ ...prev, name: e.target.value }))}
                sx={{
                  mb: 3,
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '&:hover fieldset': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                    '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                  },
                  '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' }
                }}
              />
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>User Tier</InputLabel>
                <Select
                  value={inviteForm.tier}
                  onChange={(e) => setInviteForm(prev => ({ ...prev, tier: e.target.value }))}
                  sx={{
                    color: 'white',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' }
                  }}
                >
                  <MenuItem value="paper_only">Paper Trading Only</MenuItem>
                  <MenuItem value="live_approved">Live Trading Approved</MenuItem>
                  <MenuItem value="admin">Administrator</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Initial Balance ($)"
                type="number"
                value={inviteForm.initialBalance}
                onChange={(e) => setInviteForm(prev => ({ ...prev, initialBalance: parseFloat(e.target.value) || 0 }))}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '&:hover fieldset': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                    '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                  },
                  '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' }
                }}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setInviteDialogOpen(false)} sx={{ color: '#aaa' }}>
              Cancel
            </Button>
            <Button
              onClick={handleInviteUser}
              variant="contained"
              disabled={!inviteForm.email || !inviteForm.name || loading}
              sx={{ background: 'linear-gradient(45deg, #00d4ff, #0099cc)' }}
            >
              Send Invitation
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    );
  };

  const renderUserInvitations = () => {
    const getStatusColor = (status: string) => {
      switch (status) {
        case 'active': return '#00d4ff';
        case 'used': return '#4caf50';
        case 'expired': return '#f44336';
        case 'revoked': return '#ff9800';
        default: return '#666';
      }
    };

    const getStatusIcon = (status: string) => {
      switch (status) {
        case 'active': return <PlayArrow />;
        case 'used': return <CheckCircle />;
        case 'expired': return <Warning />;
        case 'revoked': return <Cancel />;
        default: return <Visibility />;
      }
    };

    const getTierColor = (tier: string) => {
      return tier === 'pool_investor' ? '#ff6b35' : '#00d4ff';
    };

    return (
      <Box>
        {alert && (
          <Alert severity={alert.type} sx={{ mb: 3 }} onClose={() => setAlert(null)}>
            {alert.message}
          </Alert>
        )}

        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
            🎯 User Invitations Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setShowInviteDialog(true)}
            sx={{
              background: 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)',
              color: '#000',
              fontWeight: 600,
              '&:hover': {
                background: 'linear-gradient(135deg, #0099cc 0%, #007399 100%)'
              }
            }}
          >
            Send Invitation
          </Button>
        </Box>

        {/* Invitations Table */}
        <Card sx={{ background: 'rgba(26, 26, 46, 0.95)', border: '1px solid rgba(0, 212, 255, 0.2)' }}>
          <CardContent>
            <TableContainer component={Paper} sx={{ background: 'rgba(42, 42, 42, 0.5)' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: '#aaa' }}>Email</TableCell>
                    <TableCell sx={{ color: '#aaa' }}>Name</TableCell>
                    <TableCell sx={{ color: '#aaa' }}>Tier</TableCell>
                    <TableCell sx={{ color: '#aaa' }}>Status</TableCell>
                    <TableCell sx={{ color: '#aaa' }}>Allocated Funds</TableCell>
                    <TableCell sx={{ color: '#aaa' }}>Created</TableCell>
                    <TableCell sx={{ color: '#aaa' }}>Expires</TableCell>
                    <TableCell sx={{ color: '#aaa' }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {invitations.map((invitation) => (
                    <TableRow key={invitation.code} hover>
                      <TableCell>
                        <Typography sx={{ color: 'white', fontWeight: 600 }}>
                          {invitation.email}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography sx={{ color: 'white' }}>
                          {invitation.invited_name || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={invitation.user_tier.replace('_', ' ').toUpperCase()}
                          sx={{
                            backgroundColor: `${getTierColor(invitation.user_tier)}20`,
                            color: getTierColor(invitation.user_tier),
                            fontWeight: 600,
                            border: `1px solid ${getTierColor(invitation.user_tier)}`
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getStatusIcon(invitation.status)}
                          <Typography sx={{ color: getStatusColor(invitation.status), fontWeight: 600 }}>
                            {invitation.status.toUpperCase()}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography sx={{ color: 'white', fontWeight: 600 }}>
                          {formatCurrency(invitation.allocated_capital)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                          {new Date(invitation.created_at).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                          {invitation.expires_at ? new Date(invitation.expires_at).toLocaleDateString() : 'Never'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="View Details">
                            <IconButton size="small" sx={{ color: '#00d4ff' }}>
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          {invitation.status === 'active' && (
                            <Tooltip title="Revoke Invitation">
                              <IconButton size="small" sx={{ color: '#f44336' }}>
                                <Cancel />
                              </IconButton>
                            </Tooltip>
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        {/* Invitation Dialog */}
        <Dialog
          open={showInviteDialog}
          onClose={() => setShowInviteDialog(false)}
          maxWidth="md"
          fullWidth
          PaperProps={{
            sx: {
              background: 'rgba(26, 26, 46, 0.95)',
              border: '1px solid rgba(0, 212, 255, 0.2)'
            }
          }}
        >
          <DialogTitle sx={{ color: 'white' }}>
            🎯 Send User Invitation
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={3} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Email Address"
                  value={inviteForm.email}
                  onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                  sx={{
                    '& .MuiOutlinedInput-root': { color: 'white' },
                    '& .MuiInputLabel-root': { color: '#aaa' }
                  }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Full Name"
                  value={inviteForm.name}
                  onChange={(e) => setInviteForm({ ...inviteForm, name: e.target.value })}
                  sx={{
                    '& .MuiOutlinedInput-root': { color: 'white' },
                    '& .MuiInputLabel-root': { color: '#aaa' }
                  }}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowInviteDialog(false)} sx={{ color: '#aaa' }}>
              Cancel
            </Button>
            <Button
              onClick={handleSendInvitation}
              variant="contained"
              sx={{
                background: 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)',
                color: '#000'
              }}
            >
              Send Invitation
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    );
  };

  const loadAnalytics = async () => {
    try {
      setLoadingAnalytics(true);
      const response = await getJsonWithRetry(getApiUrl(`/api/admin/analytics?timeRange=${timeRange}`), {
        headers: { 'X-Admin-ID': user.id }
      });
      if (response?.success) {
        setAnalyticsData({
          totalTrades: response.total_trades || 0,
          successRate: response.success_rate || 0,
          avgProfit: response.avg_profit || 0,
          totalVolume: response.total_volume || 0,
          activeStrategies: response.active_strategies || 0,
          systemPerformance: response.system_performance || 0,
          userGrowth: response.user_growth || 0,
          revenueGrowth: response.revenue_growth || 0
        });
      }
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  useEffect(() => {
    if (selectedSection === 'analytics') {
      loadAnalytics();
    }
  }, [timeRange, selectedSection]);

  const renderAnalytics = () => {
    if (loadingAnalytics) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress sx={{ color: '#00d4ff' }} />
        </Box>
      );
    }

    return (
      <Box>
        {alert && (
          <Alert severity={alert.type} sx={{ mb: 3 }} onClose={() => setAlert(null)}>
            {alert.message}
          </Alert>
        )}

        {/* Analytics Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Box>
            <Typography variant="h4" sx={{ color: 'white', fontWeight: 700, mb: 0.5 }}>
            📊 Advanced Analytics
          </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
              Comprehensive trading performance metrics and insights
            </Typography>
          </Box>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              sx={{
                color: 'white',
                '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' }
              }}
            >
              <MenuItem value="24h">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last 90 Days</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Performance Metrics */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)',
              border: '1px solid rgba(76, 175, 80, 0.3)',
              borderRadius: 2,
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 24px rgba(76, 175, 80, 0.2)',
                borderColor: 'rgba(76, 175, 80, 0.5)'
              }
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h6" sx={{ color: '#4caf50', mb: 1 }}>
                      Total Trades
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                      {analyticsData.totalTrades.toLocaleString()}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#4caf50' }}>
                      +12.5% from last period
                    </Typography>
                  </Box>
                  <TradingIcon sx={{ color: '#4caf50', fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              borderRadius: 2,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              cursor: 'pointer',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 24px rgba(0, 212, 255, 0.2)',
                borderColor: 'rgba(0, 212, 255, 0.5)',
                background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 212, 255, 0.08) 100%)'
              }
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1 }}>
                      Success Rate
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                      {analyticsData.successRate.toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#00d4ff' }}>
                      +2.3% from last period
                    </Typography>
                  </Box>
                  <AnalyticsIcon sx={{ color: '#00d4ff', fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(156, 39, 176, 0.05) 100%)',
              border: '1px solid rgba(156, 39, 176, 0.3)',
              borderRadius: 2,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              cursor: 'pointer',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 24px rgba(156, 39, 176, 0.2)',
                borderColor: 'rgba(156, 39, 176, 0.5)',
                background: 'linear-gradient(135deg, rgba(156, 39, 176, 0.15) 0%, rgba(156, 39, 176, 0.08) 100%)'
              }
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h6" sx={{ color: '#9c27b0', mb: 1 }}>
                      Avg Profit
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                      {formatCurrency(analyticsData.avgProfit)}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#9c27b0' }}>
                      +8.7% from last period
                    </Typography>
                  </Box>
                  <AttachMoney sx={{ color: '#9c27b0', fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%)',
              border: '1px solid rgba(255, 152, 0, 0.3)',
              borderRadius: 2,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              cursor: 'pointer',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 24px rgba(255, 152, 0, 0.2)',
                borderColor: 'rgba(255, 152, 0, 0.5)',
                background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.15) 0%, rgba(255, 152, 0, 0.08) 100%)'
              }
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h6" sx={{ color: '#ff9800', mb: 1 }}>
                      Trading Volume
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                      {formatCurrency(analyticsData.totalVolume)}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#ff9800' }}>
                      +15.2% from last period
                    </Typography>
                  </Box>
                  <PortfolioIcon sx={{ color: '#ff9800', fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Analytics Sections */}
        <Grid container spacing={3}>
          {/* Real-Time Wealth Tracking */}
          <Grid item xs={12} md={6}>
            <RealTimeWealthTracker
              portfolioValue={adminMetrics.totalPortfolioValue || 100000}
              isLiveTrading={liveTradingStatus.isActive}
            />
          </Grid>

          {/* User Activity */}
          <Grid item xs={12} md={6}>
            <Card sx={{
              backgroundColor: 'rgba(26, 26, 46, 0.8)',
              border: '1px solid rgba(76, 175, 80, 0.2)',
              height: '400px'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#4caf50', mb: 3 }}>
                  👥 User Activity
                </Typography>
                <Box sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '300px',
                  border: '2px dashed rgba(76, 175, 80, 0.3)',
                  borderRadius: 2
                }}>
                  <Typography sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                    👥 User Activity Chart Placeholder
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* System Health */}
          <Grid item xs={12} md={6}>
            <Card sx={{
              backgroundColor: 'rgba(26, 26, 46, 0.8)',
              border: '1px solid rgba(156, 39, 176, 0.2)',
              height: '400px'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#9c27b0', mb: 3 }}>
                  🔧 System Health
                </Typography>
                <Box sx={{ p: 2 }}>
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography sx={{ color: 'white' }}>CPU Usage</Typography>
                      <Typography sx={{ color: '#4caf50' }}>23%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={23}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        '& .MuiLinearProgress-bar': { backgroundColor: '#4caf50' }
                      }}
                    />
                  </Box>
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography sx={{ color: 'white' }}>Memory Usage</Typography>
                      <Typography sx={{ color: '#ff9800' }}>67%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={67}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        '& .MuiLinearProgress-bar': { backgroundColor: '#ff9800' }
                      }}
                    />
                  </Box>
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography sx={{ color: 'white' }}>API Response Time</Typography>
                      <Typography sx={{ color: '#00d4ff' }}>45ms</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={15}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        '& .MuiLinearProgress-bar': { backgroundColor: '#00d4ff' }
                      }}
                    />
                  </Box>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography sx={{ color: 'white' }}>Database Load</Typography>
                      <Typography sx={{ color: '#4caf50' }}>12%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={12}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        '& .MuiLinearProgress-bar': { backgroundColor: '#4caf50' }
                      }}
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} md={6}>
            <Card sx={{
              backgroundColor: 'rgba(26, 26, 46, 0.8)',
              border: '1px solid rgba(255, 152, 0, 0.2)',
              height: '400px'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#ff9800', mb: 3 }}>
                  🕒 Recent Activity
                </Typography>
                <Box sx={{ maxHeight: '320px', overflow: 'auto' }}>
                  {[
                    { time: '2 min ago', action: 'User john_doe placed buy order for AAPL', type: 'trade' },
                    { time: '5 min ago', action: 'New user registration: jane_smith', type: 'user' },
                    { time: '8 min ago', action: 'Fund allocation: $5,000 to mike_wilson', type: 'fund' },
                    { time: '12 min ago', action: 'AI strategy optimization completed', type: 'system' },
                    { time: '15 min ago', action: 'Live trading session started', type: 'trade' },
                    { time: '18 min ago', action: 'System backup completed successfully', type: 'system' }
                  ].map((activity, index) => (
                    <Box key={index} sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 2,
                      p: 2,
                      mb: 1,
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      borderRadius: 1,
                      border: '1px solid rgba(255, 255, 255, 0.1)'
                    }}>
                      <Box sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        backgroundColor: activity.type === 'trade' ? '#4caf50' :
                                        activity.type === 'user' ? '#00d4ff' :
                                        activity.type === 'fund' ? '#ff9800' : '#9c27b0'
                      }} />
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          {activity.action}
                        </Typography>
                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                          {activity.time}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderNotifications = () => {

    const getNotificationIcon = (type: string) => {
      switch (type) {
        case 'success': return '✅';
        case 'warning': return '⚠️';
        case 'error': return '❌';
        case 'info': return 'ℹ️';
        default: return '📢';
      }
    };

    const getNotificationColor = (type: string) => {
      switch (type) {
        case 'success': return '#4caf50';
        case 'warning': return '#ff9800';
        case 'error': return '#f44336';
        case 'info': return '#2196f3';
        default: return '#00d4ff';
      }
    };

    const getCategoryColor = (category: string) => {
      switch (category) {
        case 'trading': return '#4caf50';
        case 'market': return '#ff9800';
        case 'user': return '#2196f3';
        case 'system': return '#9c27b0';
        default: return '#00d4ff';
      }
    };

    const filteredNotifications = notifications.filter(n => {
      if (filter === 'all') return true;
      if (filter === 'unread') return !n.read;
      return n.category === filter;
    });

    const markAsRead = (id: string) => {
      markNotificationAsRead(id);
    };

    const markAllAsRead = () => {
      markAllNotificationsAsRead();
    };

    return (
      <Box>
        {/* Notification Stats */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%)',
              border: '1px solid rgba(33, 150, 243, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#2196f3', mb: 1 }}>
                  Total Notifications
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {notifications.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%)',
              border: '1px solid rgba(255, 152, 0, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#ff9800', mb: 1 }}>
                  Unread
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {notifications.filter(n => !n.read).length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%)',
              border: '1px solid rgba(244, 67, 54, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#f44336', mb: 1 }}>
                  Critical Alerts
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {notifications.filter(n => n.type === 'error').length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)',
              border: '1px solid rgba(76, 175, 80, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#4caf50', mb: 1 }}>
                  Trading Alerts
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {notifications.filter(n => n.category === 'trading').length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Notifications Management */}
        <Card sx={{
          backgroundColor: 'rgba(26, 26, 46, 0.8)',
          border: '1px solid rgba(0, 212, 255, 0.2)'
        }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                📢 System Notifications
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Filter</InputLabel>
                  <Select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    sx={{
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                      '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                      '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' }
                    }}
                  >
                    <MenuItem value="all">All Notifications</MenuItem>
                    <MenuItem value="unread">Unread Only</MenuItem>
                    <MenuItem value="trading">Trading</MenuItem>
                    <MenuItem value="market">Market</MenuItem>
                    <MenuItem value="user">User</MenuItem>
                    <MenuItem value="system">System</MenuItem>
                  </Select>
                </FormControl>
                <Button
                  variant="outlined"
                  onClick={markAllAsRead}
                  sx={{ color: '#00d4ff', borderColor: '#00d4ff' }}
                >
                  Mark All Read
                </Button>
              </Box>
            </Box>

            <Box sx={{ maxHeight: 600, overflow: 'auto' }}>
              {filteredNotifications.map((notification) => (
                <Card
                  key={notification.id}
                  sx={{
                    mb: 2,
                    backgroundColor: notification.read ? 'rgba(42, 42, 42, 0.3)' : 'rgba(0, 212, 255, 0.05)',
                    border: `1px solid ${notification.read ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 212, 255, 0.2)'}`,
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: 'rgba(0, 212, 255, 0.1)'
                    }
                  }}
                  onClick={() => markAsRead(notification.id)}
                >
                  <CardContent sx={{ py: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                      <Typography sx={{ fontSize: '1.5rem' }}>
                        {getNotificationIcon(notification.type)}
                      </Typography>
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                          <Typography variant="subtitle1" sx={{
                            color: 'white',
                            fontWeight: notification.read ? 400 : 600
                          }}>
                            {notification.title}
                          </Typography>
                          <Chip
                            label={notification.category.toUpperCase()}
                            size="small"
                            sx={{
                              backgroundColor: getCategoryColor(notification.category),
                              color: 'white',
                              fontSize: '0.7rem'
                            }}
                          />
                          {!notification.read && (
                            <Chip
                              label="NEW"
                              size="small"
                              sx={{
                                backgroundColor: '#f44336',
                                color: 'white',
                                fontSize: '0.7rem'
                              }}
                            />
                          )}
                        </Box>
                        <Typography variant="body2" sx={{
                          color: notification.read ? '#aaa' : 'rgba(255, 255, 255, 0.9)',
                          mb: 1
                        }}>
                          {notification.message}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#888' }}>
                          {notification.timestamp.toLocaleString()}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}
              {filteredNotifications.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography sx={{ color: '#aaa' }}>
                    No notifications found for the selected filter.
                  </Typography>
                </Box>
              )}
              {notifications.length === 0 && (
                <Box sx={{
                  textAlign: 'center',
                  py: 6,
                  animation: 'fadeIn 0.5s ease-out',
                  '@keyframes fadeIn': {
                    from: { opacity: 0 },
                    to: { opacity: 1 }
                  }
                }}>
                  <NotificationsIcon sx={{
                    fontSize: 64,
                    color: 'rgba(255, 255, 255, 0.3)',
                    mb: 2,
                    animation: 'float 3s ease-in-out infinite',
                    '@keyframes float': {
                      '0%, 100%': { transform: 'translateY(0px)' },
                      '50%': { transform: 'translateY(-10px)' }
                    }
                  }} />
                  <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1, fontWeight: 600 }}>
                    No notifications found
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                    No notifications found for the selected filter.
                  </Typography>
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  };

  const renderLiveTrading = () => (
    <Box>
      <Card sx={{
        backgroundColor: 'rgba(26, 26, 46, 0.8)',
        border: '1px solid rgba(76, 175, 80, 0.2)'
      }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ color: '#4caf50' }}>
              📈 Live Trading Control Center
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Chip
                label={liveTradingStatus.isActive ? "LIVE TRADING ACTIVE" : "LIVE TRADING INACTIVE"}
                sx={{
                  backgroundColor: liveTradingStatus.isActive ? '#4caf50' : '#ff9800',
                  color: 'white',
                  fontWeight: 600,
                  animation: liveTradingStatus.isActive ? 'pulse 2s infinite' : 'none'
                }}
              />
              {liveTradingStatus.isActive ? (
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<Warning />}
                  sx={{ background: 'linear-gradient(45deg, #f44336, #d32f2f)' }}
                >
                  Emergency Stop
                </Button>
              ) : (
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<PlayArrow />}
                  disabled={!liveTradingStatus.canActivate}
                  sx={{
                    background: liveTradingStatus.canActivate
                      ? 'linear-gradient(45deg, #4caf50, #388e3c)'
                      : 'rgba(255, 255, 255, 0.12)'
                  }}
                >
                  {liveTradingStatus.canActivate ? 'Activate Live Trading' : 'Setup Required'}
                </Button>
              )}
            </Box>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card sx={{ backgroundColor: 'rgba(76, 175, 80, 0.1)', border: '1px solid rgba(76, 175, 80, 0.3)' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#4caf50', mb: 2 }}>Active Positions</Typography>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 700 }}>
                    {liveTradingStatus.activePositions}
                  </Typography>
                  <Typography variant="caption" sx={{ color: liveTradingStatus.isActive ? '#4caf50' : '#ff9800' }}>
                    {liveTradingStatus.isActive ? 'Live trading active' : 'No live positions'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card sx={{ backgroundColor: 'rgba(0, 212, 255, 0.1)', border: '1px solid rgba(0, 212, 255, 0.3)' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>Daily P&L</Typography>
                  <Typography variant="h3" sx={{
                    color: liveTradingStatus.dailyPnL >= 0 ? '#4caf50' : '#f44336',
                    fontWeight: 700
                  }}>
                    {liveTradingStatus.dailyPnL >= 0 ? '+' : ''}${liveTradingStatus.dailyPnL.toFixed(2)}
                  </Typography>
                  <Typography variant="caption" sx={{
                    color: liveTradingStatus.isActive ? '#4caf50' : '#ff9800'
                  }}>
                    {liveTradingStatus.isActive ? 'Live trading P&L' : 'No live trading'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card sx={{ backgroundColor: 'rgba(156, 39, 176, 0.1)', border: '1px solid rgba(156, 39, 176, 0.3)' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#9c27b0', mb: 2 }}>Win Rate</Typography>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 700 }}>
                    {liveTradingStatus.winRate.toFixed(1)}%
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#9c27b0' }}>
                    {liveTradingStatus.isActive ? 'Live trading performance' : 'No live data'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" sx={{ color: 'white', mb: 2 }}>Risk Management Controls</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Max Daily Loss ($)"
                  defaultValue="5000"
                  size="small"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: 'white',
                      '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                      '&:hover fieldset': { borderColor: 'rgba(244, 67, 54, 0.5)' },
                      '&.Mui-focused fieldset': { borderColor: '#f44336' }
                    },
                    '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' }
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Max Position Size (%)"
                  defaultValue="2.5"
                  size="small"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: 'white',
                      '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                      '&:hover fieldset': { borderColor: 'rgba(255, 152, 0, 0.5)' },
                      '&.Mui-focused fieldset': { borderColor: '#ff9800' }
                    },
                    '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' }
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  sx={{
                    borderColor: '#ff9800',
                    color: '#ff9800',
                    '&:hover': { backgroundColor: 'rgba(255, 152, 0, 0.1)' }
                  }}
                >
                  Update Limits
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  sx={{
                    borderColor: '#f44336',
                    color: '#f44336',
                    '&:hover': { backgroundColor: 'rgba(244, 67, 54, 0.1)' }
                  }}
                >
                  Pause Trading
                </Button>
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  const renderPaperTrading = () => {

    return (
      <Box>
        {/* Internal Paper Trading Component */}
        <Box sx={{ mb: 4 }}>
          <InternalPaperTrading />
        </Box>

        {/* Paper Trading Sessions Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%)',
              border: '1px solid rgba(33, 150, 243, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#2196f3', mb: 1 }}>
                  Active Sessions
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {paperSessions.filter(s => s.status === 'active').length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)',
              border: '1px solid rgba(76, 175, 80, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#4caf50', mb: 1 }}>
                  Completed Today
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {paperSessions.filter(s => s.status === 'completed' &&
                    new Date(s.end_time).toDateString() === new Date().toDateString()).length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%)',
              border: '1px solid rgba(255, 152, 0, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#ff9800', mb: 1 }}>
                  Avg Return
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {paperSessions.length > 0 ?
                    `${(paperSessions.reduce((acc, s) => acc + (s.return_percentage || 0), 0) / paperSessions.length).toFixed(2)}%` :
                    '0.00%'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(156, 39, 176, 0.05) 100%)',
              border: '1px solid rgba(156, 39, 176, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#9c27b0', mb: 1 }}>
                  Total Volume
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  ${paperSessions.reduce((acc, s) => acc + (s.total_volume || 0), 0).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Active Paper Trading Sessions Table */}
        <Card sx={{
          backgroundColor: 'rgba(26, 26, 46, 0.8)',
          border: '1px solid rgba(0, 212, 255, 0.2)'
        }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                📊 Internal Paper Trading Sessions
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => {
                    setAlert({
                      type: 'info',
                      message: 'Paper trading session creation interface will be implemented in the next update. For now, sessions are managed through the backend API.'
                    });
                  }}
                  sx={{ background: 'linear-gradient(45deg, #4caf50, #388e3c)' }}
                >
                  Start New Session
                </Button>
                <Button
                  variant="contained"
                  startIcon={<Refresh />}
                  onClick={() => window.location.reload()}
                  sx={{ background: 'linear-gradient(45deg, #00d4ff, #0099cc)' }}
                >
                  Refresh
                </Button>
              </Box>
            </Box>

            {loadingSessions ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow key="paper-sessions-header">
                      <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>User</TableCell>
                      <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Session Type</TableCell>
                      <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Status</TableCell>
                      <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Start Capital</TableCell>
                      <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Current Value</TableCell>
                      <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>P&L</TableCell>
                      <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Duration</TableCell>
                      <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {paperSessions.map((session) => (
                      <TableRow key={session.session_id} hover>
                        <TableCell sx={{ color: 'white' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Avatar sx={{ width: 32, height: 32, bgcolor: '#2196f3' }}>
                              {session.user_name?.charAt(0) || 'U'}
                            </Avatar>
                            {session.user_name || session.user_id}
                          </Box>
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>
                          <Chip
                            label={session.session_type?.replace('_', ' ').toUpperCase() || 'CUSTOM'}
                            size="small"
                            sx={{
                              backgroundColor: session.session_type === 'QUICK_24H' ? '#4caf50' :
                                             session.session_type === 'EXTENDED_48H' ? '#ff9800' :
                                             session.session_type === 'FULL_WEEK' ? '#f44336' : '#9c27b0',
                              color: 'white'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={session.status?.toUpperCase() || 'UNKNOWN'}
                            size="small"
                            sx={{
                              backgroundColor: session.status === 'active' ? '#4caf50' :
                                             session.status === 'completed' ? '#2196f3' :
                                             session.status === 'paused' ? '#ff9800' : '#f44336',
                              color: 'white'
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>
                          ${session.starting_capital?.toLocaleString() || '0'}
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>
                          ${session.current_value?.toLocaleString() || '0'}
                        </TableCell>
                        <TableCell>
                          <Typography
                            sx={{
                              color: (session.profit_loss || 0) >= 0 ? '#4caf50' : '#f44336',
                              fontWeight: 600
                            }}
                          >
                            {(session.profit_loss || 0) >= 0 ? '+' : ''}
                            ${session.profit_loss?.toLocaleString() || '0'}
                            {session.return_percentage && ` (${session.return_percentage.toFixed(2)}%)`}
                          </Typography>
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>
                          {session.start_time ?
                            `${Math.floor((new Date().getTime() - new Date(session.start_time).getTime()) / (1000 * 60 * 60))}h` :
                            'N/A'}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Tooltip title="View Details">
                              <IconButton size="small" sx={{ color: '#00d4ff' }}>
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            {session.status === 'active' && (
                              <Tooltip title="Pause Session">
                                <IconButton size="small" sx={{ color: '#ff9800' }}>
                                  <Pause />
                                </IconButton>
                              </Tooltip>
                            )}
                            {session.status === 'paused' && (
                              <Tooltip title="Resume Session">
                                <IconButton size="small" sx={{ color: '#4caf50' }}>
                                  <PlayArrow />
                                </IconButton>
                              </Tooltip>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                    {paperSessions.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={8} sx={{ textAlign: 'center', color: '#aaa', py: 4 }}>
                          <Box sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            gap: 2,
                            py: 4,
                            animation: 'fadeIn 0.5s ease-out',
                            '@keyframes fadeIn': {
                              from: { opacity: 0 },
                              to: { opacity: 1 }
                            }
                          }}>
                            <TradingIcon sx={{
                              fontSize: 48,
                              color: 'rgba(255, 255, 255, 0.3)',
                              animation: 'float 3s ease-in-out infinite',
                              '@keyframes float': {
                                '0%, 100%': { transform: 'translateY(0px)' },
                                '50%': { transform: 'translateY(-10px)' }
                              }
                            }} />
                            <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 600 }}>
                              No paper trading sessions found
                            </Typography>
                            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                              Users can start sessions from their dashboard.
                            </Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </Box>
    );
  };

  // Load AI health data - moved outside render function
  useEffect(() => {
    if (selectedSection === 'ai-systems') {
      const fetchAIHealth = async () => {
        try {
          // Try AI health endpoint; fallback to generic health (with retries)
          const retryOpts = { retries: 3, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 } as const;
          let data: any | null = null;
          try {
            data = await getJsonWithRetry(getApiUrl('/api/ai/status'), {}, retryOpts);
          } catch {
            try {
              data = await getJsonWithRetry(getApiUrl('/api/ai-trading/health'), {}, retryOpts);
            } catch {
              try {
                data = await getJsonWithRetry(getApiUrl('/health'), {}, retryOpts);
              } catch {
                data = null;
              }
            }
          }
          if (data) {
            setAiHealth(data);
          }
        } catch (error) {
          console.error('Failed to fetch AI health:', error);
        } finally {
          setLoadingAI(false);
        }
      };


      const fetchModelCoverage = async () => {
        try {
          setLoadingCoverage(true);
          const retryOpts = { retries: 3, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 } as const;
          const data = await getJsonWithRetry(getApiUrl('/api/revolutionary/ai/model-coverage'), {}, retryOpts);
          setModelCoverage(data);
        } catch (error) {
          console.error('Failed to fetch model coverage:', error);
        } finally {
          setLoadingCoverage(false);
        }
      };

      fetchAIHealth();
      fetchModelCoverage();
      const i1 = setInterval(fetchAIHealth, 30000);
      const i2 = setInterval(fetchModelCoverage, 60000);
      return () => { clearInterval(i1); clearInterval(i2); };
    }
  }, [selectedSection]);

  const renderAISystems = () => {

    return (
      <Box>
        {/* AI Systems Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(156, 39, 176, 0.05) 100%)',
              border: '1px solid rgba(156, 39, 176, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#9c27b0', mb: 1 }}>
                  AI Service Status
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {loadingAI ? '...' : aiHealth?.ai_trading_service === 'healthy' ? '✅ ONLINE' : '❌ OFFLINE'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)',
              border: '1px solid rgba(76, 175, 80, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#4caf50', mb: 1 }}>
                  GPT-OSS 20B
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {loadingAI ? '...' : aiHealth?.gpt_oss_20b ? '✅ READY' : '❌ DOWN'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%)',
              border: '1px solid rgba(33, 150, 243, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#2196f3', mb: 1 }}>
                  GPT-OSS 120B
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {loadingAI ? '...' : aiHealth?.gpt_oss_120b ? '✅ READY' : '❌ DOWN'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%)',
              border: '1px solid rgba(255, 152, 0, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#ff9800', mb: 1 }}>
                  Active Services
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {loadingAI ? '...' : aiHealth?.services ?
                    Object.values(aiHealth.services).filter(Boolean).length : '0'}/4
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* AI Services Status Table */}
        <Card sx={{
          backgroundColor: 'rgba(26, 26, 46, 0.8)',
          border: '1px solid rgba(156, 39, 176, 0.2)',
          mb: 3
        }}>
          <CardContent>
            <Typography variant="h6" sx={{ color: '#9c27b0', mb: 3, fontWeight: 600 }}>
              🤖 AI Trading Services Status
            </Typography>

            {loadingAI ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Service</TableCell>
                      <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Status</TableCell>
                      <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Model</TableCell>
                      <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Last Check</TableCell>
                      <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow key="sentiment-analysis" hover>
                      <TableCell sx={{ color: 'white' }}>Sentiment Analysis</TableCell>
                      <TableCell>
                        <Chip
                          label={aiHealth?.services?.sentiment_analysis ? 'ACTIVE' : 'INACTIVE'}
                          size="small"
                          sx={{
                            backgroundColor: aiHealth?.services?.sentiment_analysis ? '#4caf50' : '#f44336',
                            color: 'white'
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ color: 'white' }}>GPT-OSS 20B</TableCell>
                      <TableCell sx={{ color: 'white' }}>
                        {aiHealth?.timestamp ? new Date(aiHealth.timestamp).toLocaleTimeString() : 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Button size="small" variant="outlined" sx={{ color: '#9c27b0', borderColor: '#9c27b0' }}>
                          Test
                        </Button>
                      </TableCell>
                    </TableRow>
                    <TableRow key="strategy-generation" hover>
                      <TableCell sx={{ color: 'white' }}>Strategy Generation</TableCell>
                      <TableCell>
                        <Chip
                          label={aiHealth?.services?.strategy_generation ? 'ACTIVE' : 'INACTIVE'}
                          size="small"
                          sx={{
                            backgroundColor: aiHealth?.services?.strategy_generation ? '#4caf50' : '#f44336',
                            color: 'white'
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ color: 'white' }}>GPT-OSS 120B</TableCell>
                      <TableCell sx={{ color: 'white' }}>
                        {aiHealth?.timestamp ? new Date(aiHealth.timestamp).toLocaleTimeString() : 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Button size="small" variant="outlined" sx={{ color: '#9c27b0', borderColor: '#9c27b0' }}>
                          Test
                        </Button>
                      </TableCell>
                    </TableRow>
                    <TableRow key="technical-analysis" hover>
                      <TableCell sx={{ color: 'white' }}>Technical Analysis</TableCell>
                      <TableCell>
                        <Chip
                          label={aiHealth?.services?.technical_analysis ? 'ACTIVE' : 'INACTIVE'}
                          size="small"
                          sx={{
                            backgroundColor: aiHealth?.services?.technical_analysis ? '#4caf50' : '#f44336',
                            color: 'white'
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ color: 'white' }}>GPT-OSS 20B</TableCell>
                      <TableCell sx={{ color: 'white' }}>
                        {aiHealth?.timestamp ? new Date(aiHealth.timestamp).toLocaleTimeString() : 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Button size="small" variant="outlined" sx={{ color: '#9c27b0', borderColor: '#9c27b0' }}>
                          Test
                        </Button>
                      </TableCell>
                    </TableRow>
                    <TableRow key="risk-assessment" hover>
                      <TableCell sx={{ color: 'white' }}>Risk Assessment</TableCell>
                      <TableCell>
                        <Chip
                          label={aiHealth?.services?.risk_assessment ? 'ACTIVE' : 'INACTIVE'}
                          size="small"
                          sx={{
                            backgroundColor: aiHealth?.services?.risk_assessment ? '#4caf50' : '#f44336',
                            color: 'white'
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ color: 'white' }}>GPT-OSS 120B</TableCell>
                      <TableCell sx={{ color: 'white' }}>
                        {aiHealth?.timestamp ? new Date(aiHealth.timestamp).toLocaleTimeString() : 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Button size="small" variant="outlined" sx={{ color: '#9c27b0', borderColor: '#9c27b0' }}>
                          Test
                        </Button>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>

        {/* AI Performance Metrics */}
        <Card sx={{
          backgroundColor: 'rgba(26, 26, 46, 0.8)',
          border: '1px solid rgba(156, 39, 176, 0.2)'
        }}>
          <CardContent>
            <Typography variant="h6" sx={{ color: '#9c27b0', mb: 3, fontWeight: 600 }}>
              📊 AI Performance Metrics
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Box sx={{ p: 2, border: '1px solid rgba(156, 39, 176, 0.2)', borderRadius: 2 }}>
                  <Typography variant="subtitle1" sx={{ color: '#9c27b0', mb: 2 }}>
                    Model Response Times
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography sx={{ color: 'white' }}>GPT-OSS 20B:</Typography>
                    <Typography sx={{ color: '#4caf50' }}>~2.3s</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography sx={{ color: 'white' }}>GPT-OSS 120B:</Typography>
                    <Typography sx={{ color: '#ff9800' }}>~8.7s</Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ p: 2, border: '1px solid rgba(156, 39, 176, 0.2)', borderRadius: 2 }}>
                  <Typography variant="subtitle1" sx={{ color: '#9c27b0', mb: 2 }}>
                    Accuracy Metrics
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography sx={{ color: 'white' }}>Sentiment Analysis:</Typography>
                    <Typography sx={{ color: '#4caf50' }}>94.2%</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography sx={{ color: 'white' }}>Technical Analysis:</Typography>
                    <Typography sx={{ color: '#4caf50' }}>91.8%</Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Box>
    );
  };

  const renderTAFAnalysis = () => {
    if (tafLoading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress sx={{ color: '#00d4ff' }} />
        </Box>
      );
    }

    return (
      <Box>
        {alert && (
          <Alert severity={alert.type} sx={{ mb: 3 }} onClose={() => setAlert(null)}>
            {alert.message}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* TAF Impact Overview */}
          <Grid item xs={12}>
            <Card sx={{
              background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
              border: '1px solid #00d4ff',
              borderRadius: 2
            }}>
              <CardContent>
                <Typography variant="h5" sx={{ color: '#00d4ff', mb: 3, display: 'flex', alignItems: 'center' }}>
                  🏛️ FINRA TAF Fee Impact Analysis
                  <Chip
                    label="Oct 4, 2025"
                    size="small"
                    sx={{ ml: 2, backgroundColor: '#ff9800', color: 'white' }}
                  />
                </Typography>

                <Grid container spacing={3}>
                  <Grid item xs={12} md={3}>
                    <Card sx={{ background: 'rgba(76, 175, 80, 0.1)', border: '1px solid #4caf50' }}>
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ color: '#4caf50', fontWeight: 'bold' }}>
                          ${tafData.currentFees.toFixed(2)}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white' }}>
                          Current Structure
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={3}>
                    <Card sx={{ background: 'rgba(244, 67, 54, 0.1)', border: '1px solid #f44336' }}>
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ color: '#f44336', fontWeight: 'bold' }}>
                          ${tafData.newFees.toFixed(2)}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white' }}>
                          New Structure
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={3}>
                    <Card sx={{ background: 'rgba(255, 152, 0, 0.1)', border: '1px solid #ff9800' }}>
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ color: '#ff9800', fontWeight: 'bold' }}>
                          +${tafData.feeIncrease.toFixed(2)}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white' }}>
                          Fee Increase
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={3}>
                    <Card sx={{ background: 'rgba(0, 212, 255, 0.1)', border: '1px solid #00d4ff' }}>
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ color: '#00d4ff', fontWeight: 'bold' }}>
                          {((tafData.feeIncrease / tafData.currentFees) * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white' }}>
                          Impact
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Trade Analysis */}
          <Grid item xs={12} md={6}>
            <Card sx={{
              background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
              border: '1px solid #9c27b0',
              borderRadius: 2,
              height: '100%'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#9c27b0', mb: 2 }}>
                  📊 Trade Impact Analysis
                </Typography>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" sx={{ color: 'white', mb: 1 }}>
                    Affected Trades (&gt;50K shares)
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={(tafData.affectedTrades / tafData.totalTrades) * 100}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'rgba(255,255,255,0.1)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: '#f44336'
                      }
                    }}
                  />
                  <Typography variant="caption" sx={{ color: 'white' }}>
                    {tafData.affectedTrades} of {tafData.totalTrades} trades ({((tafData.affectedTrades / tafData.totalTrades) * 100).toFixed(1)}%)
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2" sx={{ color: 'white' }}>
                    Total Trades Analyzed:
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#00d4ff', fontWeight: 'bold' }}>
                    {tafData.totalTrades.toLocaleString()}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" sx={{ color: 'white' }}>
                    Optimization Potential:
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#4caf50', fontWeight: 'bold' }}>
                    ${tafData.optimizationPotential.toFixed(2)}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Recommendations */}
          <Grid item xs={12} md={6}>
            <Card sx={{
              background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
              border: '1px solid #4caf50',
              borderRadius: 2,
              height: '100%'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#4caf50', mb: 2 }}>
                  💡 Optimization Recommendations
                </Typography>

                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <span style={{ fontSize: '16px' }}>⚠️</span>
                    </ListItemIcon>
                    <ListItemText
                      primary="High Impact Detected"
                      secondary="Consider order splitting for trades >50,000 shares"
                      primaryTypographyProps={{ color: 'white', fontSize: '14px' }}
                      secondaryTypographyProps={{ color: '#ccc', fontSize: '12px' }}
                    />
                  </ListItem>

                  <ListItem>
                    <ListItemIcon>
                      <span style={{ fontSize: '16px' }}>🔧</span>
                    </ListItemIcon>
                    <ListItemText
                      primary="Algorithm Updates"
                      secondary="Implement TAF cost calculations in trading logic"
                      primaryTypographyProps={{ color: 'white', fontSize: '14px' }}
                      secondaryTypographyProps={{ color: '#ccc', fontSize: '12px' }}
                    />
                  </ListItem>

                  <ListItem>
                    <ListItemIcon>
                      <span style={{ fontSize: '16px' }}>📈</span>
                    </ListItemIcon>
                    <ListItemText
                      primary="Monitor Thresholds"
                      secondary="Stay under 50,000 share threshold when possible"
                      primaryTypographyProps={{ color: 'white', fontSize: '14px' }}
                      secondaryTypographyProps={{ color: '#ccc', fontSize: '12px' }}
                    />
                  </ListItem>

                  <ListItem>
                    <ListItemIcon>
                      <span style={{ fontSize: '16px' }}>🤖</span>
                    </ListItemIcon>
                    <ListItemText
                      primary="Automated Optimization"
                      secondary="Deploy TAF-optimized trading engine"
                      primaryTypographyProps={{ color: 'white', fontSize: '14px' }}
                      secondaryTypographyProps={{ color: '#ccc', fontSize: '12px' }}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const loadPortfolio = async () => {
    try {
      setLoadingPortfolio(true);
      const response = await getJsonWithRetry(getApiUrl('/api/admin/portfolio'), {
        headers: { 'X-Admin-ID': user.id }
      });
      if (response?.success) {
        setPortfolioData({
          totalValue: response.total_value || 0,
          activePositions: response.active_positions || 0,
          riskScore: response.risk_score || 0,
          monthlyReturn: response.monthly_return || 0,
          sectors: response.sectors || 0
        });
      }
    } catch (error) {
      console.error('Failed to load portfolio:', error);
    } finally {
      setLoadingPortfolio(false);
    }
  };

  useEffect(() => {
    if (selectedSection === 'portfolio') {
      loadPortfolio();
    }
  }, [selectedSection]);

  const renderPortfolio = () => {
    if (loadingPortfolio) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress sx={{ color: '#00d4ff' }} />
        </Box>
      );
    }

    return (
    <Box>
      <Card sx={{
        backgroundColor: 'rgba(26, 26, 46, 0.8)',
        border: '1px solid rgba(0, 212, 255, 0.2)'
      }}>
        <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ color: '#00d4ff' }}>
            💼 Portfolio Management
          </Typography>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadPortfolio}
                sx={{
                  borderColor: '#00d4ff',
                  color: '#00d4ff',
                  '&:hover': { backgroundColor: 'rgba(0, 212, 255, 0.1)' }
                }}
              >
                Refresh
              </Button>
            </Box>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card sx={{ backgroundColor: 'rgba(76, 175, 80, 0.1)', border: '1px solid rgba(76, 175, 80, 0.3)' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#4caf50', mb: 2 }}>Total Portfolio Value</Typography>
                    <Typography variant="h3" sx={{ color: 'white', fontWeight: 700 }}>
                      {portfolioData ? formatCurrency(portfolioData.totalValue) : '$0'}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#4caf50' }}>
                      {portfolioData?.monthlyReturn ? `${portfolioData.monthlyReturn >= 0 ? '+' : ''}${portfolioData.monthlyReturn.toFixed(1)}% this month` : 'No data'}
                    </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card sx={{ backgroundColor: 'rgba(33, 150, 243, 0.1)', border: '1px solid rgba(33, 150, 243, 0.3)' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#2196f3', mb: 2 }}>Active Positions</Typography>
                    <Typography variant="h3" sx={{ color: 'white', fontWeight: 700 }}>
                      {portfolioData?.activePositions || 0}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#2196f3' }}>
                      {portfolioData?.sectors ? `Across ${portfolioData.sectors} sectors` : 'No positions'}
                    </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card sx={{ backgroundColor: 'rgba(255, 152, 0, 0.1)', border: '1px solid rgba(255, 152, 0, 0.3)' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#ff9800', mb: 2 }}>Risk Score</Typography>
                    <Typography variant="h3" sx={{ color: 'white', fontWeight: 700 }}>
                      {portfolioData?.riskScore ? `${portfolioData.riskScore.toFixed(1)}/10` : 'N/A'}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#ff9800' }}>
                      {portfolioData?.riskScore ? (portfolioData.riskScore < 5 ? 'Low risk' : portfolioData.riskScore < 8 ? 'Moderate risk' : 'High risk') : 'No data'}
                    </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
  };

  const [strategies, setStrategies] = useState<any[]>([]);
  const [loadingStrategies, setLoadingStrategies] = useState(false);
  const [systemConfig, setSystemConfig] = useState<any>(null);
  const [loadingConfig, setLoadingConfig] = useState(false);
  const [securitySettings, setSecuritySettings] = useState<any>(null);
  const [loadingSecurity, setLoadingSecurity] = useState(false);

  const loadStrategies = async () => {
    try {
      setLoadingStrategies(true);
      const response = await getJsonWithRetry(getApiUrl('/api/admin/strategies'), {
        headers: { 'X-Admin-ID': user.id }
      });
      if (response?.success) {
        setStrategies(response.strategies || []);
      }
    } catch (error) {
      console.error('Failed to load strategies:', error);
    } finally {
      setLoadingStrategies(false);
    }
  };

  useEffect(() => {
    if (selectedSection === 'strategy-management') {
      loadStrategies();
    }
  }, [selectedSection]);

  const renderStrategyManagement = () => {
    if (loadingStrategies) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress sx={{ color: '#9c27b0' }} />
        </Box>
      );
    }

    return (
    <Box>
        {alert && (
          <Alert severity={alert.type} sx={{ mb: 3 }} onClose={() => setAlert(null)}>
            {alert.message}
          </Alert>
        )}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" sx={{ color: '#9c27b0', fontWeight: 600 }}>
            🧠 Strategy Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAlert({ type: 'info', message: 'Strategy creation interface coming soon' })}
            sx={{ background: 'linear-gradient(45deg, #9c27b0, #7b1fa2)' }}
          >
            New Strategy
          </Button>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(156, 39, 176, 0.05) 100%)',
              border: '1px solid rgba(156, 39, 176, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#9c27b0', mb: 1 }}>
                  Active Strategies
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {strategies.filter(s => s.status === 'active').length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)',
              border: '1px solid rgba(76, 175, 80, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#4caf50', mb: 1 }}>
                  Total Strategies
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {strategies.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%)',
              border: '1px solid rgba(0, 212, 255, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1 }}>
                  Avg Performance
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {strategies.length > 0 
                    ? `${(strategies.reduce((sum, s) => sum + (s.performance || 0), 0) / strategies.length).toFixed(1)}%`
                    : '0%'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

      <Card sx={{
        backgroundColor: 'rgba(26, 26, 46, 0.8)',
          border: '1px solid rgba(156, 39, 176, 0.2)',
          mt: 3
      }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: '#9c27b0', mb: 3 }}>
              Trading Strategies
          </Typography>
            {strategies.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: '#9c27b0' }}>Strategy Name</TableCell>
                      <TableCell sx={{ color: '#9c27b0' }}>Status</TableCell>
                      <TableCell sx={{ color: '#9c27b0' }}>Performance</TableCell>
                      <TableCell sx={{ color: '#9c27b0' }}>Last Updated</TableCell>
                      <TableCell sx={{ color: '#9c27b0' }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {strategies.map((strategy) => (
                      <TableRow key={strategy.id} hover>
                        <TableCell sx={{ color: 'white' }}>{strategy.name}</TableCell>
                        <TableCell>
                          <Chip
                            label={strategy.status?.toUpperCase() || 'UNKNOWN'}
                            size="small"
                            sx={{
                              backgroundColor: strategy.status === 'active' ? '#4caf50' : '#ff9800',
                              color: 'white'
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>
                          {strategy.performance ? `${strategy.performance.toFixed(2)}%` : 'N/A'}
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>
                          {strategy.last_updated ? formatDate(strategy.last_updated) : 'N/A'}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Tooltip title="Edit Strategy">
                              <IconButton size="small" sx={{ color: '#9c27b0' }}>
                                <Edit />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="View Details">
                              <IconButton size="small" sx={{ color: '#00d4ff' }}>
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography sx={{ color: 'rgba(255, 255, 255, 0.6)', textAlign: 'center', py: 4 }}>
                No strategies found. Create your first trading strategy to get started.
          </Typography>
            )}
        </CardContent>
      </Card>
    </Box>
  );
  };

  const loadPermissions = async () => {
    try {
      setLoadingPermissions(true);
      const response = await getJsonWithRetry(getApiUrl('/api/admin/permissions'), {
        headers: { 'X-Admin-ID': user.id }
      });
      if (response?.success) {
        setPermissions(response.permissions || []);
      }
    } catch (error) {
      console.error('Failed to load permissions:', error);
    } finally {
      setLoadingPermissions(false);
    }
  };

  const handleApproveTrading = async (targetUser: any) => {
    try {
      await getJsonWithRetry(getApiUrl('/api/admin/approve-trading'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-ID': user.id
        },
        body: JSON.stringify({ user_id: targetUser.user_id || targetUser.id })
      });
      setAlert({ type: 'success', message: `Approved ${targetUser.username} for live trading` });
      loadPermissions();
      refetchUsers();
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to approve trading permission' });
    }
  };

  const handleRevokeTrading = async (targetUser: any) => {
    try {
      await getJsonWithRetry(getApiUrl('/api/admin/revoke-trading'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-ID': user.id
        },
        body: JSON.stringify({ user_id: targetUser.user_id || targetUser.id })
      });
      setAlert({ type: 'success', message: `Revoked trading permission for ${targetUser.username}` });
      loadPermissions();
      refetchUsers();
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to revoke trading permission' });
    }
  };

  const handleUpdatePermission = async (permission: any, updates: any) => {
    try {
      await getJsonWithRetry(getApiUrl(`/api/admin/permissions/${permission.permission_id}`), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-ID': user.id
        },
        body: JSON.stringify(updates)
      });
      setAlert({ type: 'success', message: 'Permission updated successfully' });
      loadPermissions();
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to update permission' });
    }
  };

  const handleRevokePermission = async (permission: any) => {
    try {
      await getJsonWithRetry(getApiUrl(`/api/admin/permissions/${permission.permission_id}`), {
        method: 'DELETE',
        headers: { 'X-Admin-ID': user.id }
      });
      setAlert({ type: 'success', message: 'Permission revoked successfully' });
      loadPermissions();
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to revoke permission' });
    }
  };

  const renderPermissions = () => {
    // Map users to the format expected by TradingPermissionsTab
    const mappedUsers = users.map(u => ({
      user_id: u.id,
      username: u.username,
      email: u.email,
      role: u.tier || 'user',
      live_trading_approved: u.liveTrading || false,
      max_allocation: u.allocatedFunds || 0,
      current_allocation: u.currentValue || 0,
      is_active: u.status === 'active'
    }));

    return (
      <TradingPermissionsTab
        permissions={permissions}
        users={mappedUsers}
        onApproveTrading={handleApproveTrading}
        onRevokeTrading={handleRevokeTrading}
        onUpdatePermission={handleUpdatePermission}
        onRevokePermission={handleRevokePermission}
        loading={loadingPermissions || usersLoading}
        formatDate={formatDate}
        getStatusIcon={(status: string) => {
          switch (status) {
            case 'active': return <CheckCircle sx={{ color: '#4caf50' }} />;
            case 'pending': return <Warning sx={{ color: '#ff9800' }} />;
            case 'expired': return <ErrorIcon sx={{ color: '#f44336' }} />;
            default: return <Info sx={{ color: '#2196f3' }} />;
          }
        }}
        showAlert={(type, message) => setAlert({ type, message })}
      />
    );
  };

  const loadSystemConfig = async () => {
    try {
      setLoadingConfig(true);
      const response = await getJsonWithRetry(getApiUrl('/api/admin/system-config'), {
        headers: { 'X-Admin-ID': user.id }
      });
      if (response?.success) {
        setSystemConfig(response.config || {});
      }
    } catch (error) {
      console.error('Failed to load system config:', error);
    } finally {
      setLoadingConfig(false);
    }
  };

  useEffect(() => {
    if (selectedSection === 'system-config') {
      loadSystemConfig();
    }
  }, [selectedSection]);

  const renderSystemConfig = () => {
    if (loadingConfig) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress sx={{ color: '#607d8b' }} />
        </Box>
      );
    }

    return (
    <Box>
        {alert && (
          <Alert severity={alert.type} sx={{ mb: 3 }} onClose={() => setAlert(null)}>
            {alert.message}
          </Alert>
        )}

        <Typography variant="h5" sx={{ color: '#607d8b', mb: 3, fontWeight: 600 }}>
          ⚙️ System Configuration
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
      <Card sx={{
        backgroundColor: 'rgba(26, 26, 46, 0.8)',
              border: '1px solid rgba(96, 125, 139, 0.2)'
      }}>
        <CardContent>
                <Typography variant="h6" sx={{ color: '#607d8b', mb: 3 }}>
                  Trading Parameters
          </Typography>
                <TextField
                  fullWidth
                  label="Max Daily Loss ($)"
                  type="number"
                  defaultValue={systemConfig?.max_daily_loss || 5000}
                  sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: 'white' } }}
                />
                <TextField
                  fullWidth
                  label="Max Position Size (%)"
                  type="number"
                  defaultValue={systemConfig?.max_position_size || 2.5}
                  sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: 'white' } }}
                />
                <TextField
                  fullWidth
                  label="Risk Multiplier"
                  type="number"
                  defaultValue={systemConfig?.risk_multiplier || 1.0}
                  sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: 'white' } }}
                />
                <Button
                  variant="contained"
                  onClick={async () => {
                    try {
                      setLoading(true);
                      await getJsonWithRetry(getApiUrl('/api/admin/system-config'), {
                        method: 'PUT',
                        headers: {
                          'Content-Type': 'application/json',
                          'X-Admin-ID': user.id
                        },
                        body: JSON.stringify(systemConfig)
                      });
                      setAlert({ type: 'success', message: 'Trading parameters updated successfully' });
                      loadSystemConfig();
                    } catch (error) {
                      setAlert({ type: 'error', message: 'Failed to update trading parameters' });
                    } finally {
                      setLoading(false);
                    }
                  }}
                  sx={{ background: 'linear-gradient(45deg, #607d8b, #455a64)' }}
                >
                  Save Trading Parameters
                </Button>
        </CardContent>
      </Card>
          </Grid>

          <Grid item xs={12} md={6}>
      <Card sx={{
        backgroundColor: 'rgba(26, 26, 46, 0.8)',
        border: '1px solid rgba(96, 125, 139, 0.2)'
      }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: '#607d8b', mb: 3 }}>
                  API Settings
          </Typography>
                <TextField
                  fullWidth
                  label="API Rate Limit (requests/min)"
                  type="number"
                  defaultValue={systemConfig?.api_rate_limit || 100}
                  sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: 'white' } }}
                />
                <TextField
                  fullWidth
                  label="WebSocket Timeout (seconds)"
                  type="number"
                  defaultValue={systemConfig?.ws_timeout || 30}
                  sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: 'white' } }}
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      defaultChecked={systemConfig?.enable_websocket || true}
                      sx={{ color: '#607d8b', '&.Mui-checked': { color: '#607d8b' } }}
                    />
                  }
                  label="Enable WebSocket Connections"
                  sx={{ color: 'white', mb: 2 }}
                />
                <Button
                  variant="contained"
                  onClick={async () => {
                    try {
                      setLoading(true);
                      await getJsonWithRetry(getApiUrl('/api/admin/system-config'), {
                        method: 'PUT',
                        headers: {
                          'Content-Type': 'application/json',
                          'X-Admin-ID': user.id
                        },
                        body: JSON.stringify(systemConfig)
                      });
                      setAlert({ type: 'success', message: 'API settings updated successfully' });
                      loadSystemConfig();
                    } catch (error) {
                      setAlert({ type: 'error', message: 'Failed to update API settings' });
                    } finally {
                      setLoading(false);
                    }
                  }}
                  sx={{ background: 'linear-gradient(45deg, #607d8b, #455a64)' }}
                >
                  Save API Settings
                </Button>
        </CardContent>
      </Card>
          </Grid>
        </Grid>
    </Box>
  );
  };

  const handleSystemAction = async (action: string, params?: any) => {
    try {
      if (action === 'refresh_metrics') {
        await loadSystemHealthData();
        setAlert({ type: 'success', message: 'System metrics refreshed' });
      } else {
        const response = await getJsonWithRetry(getApiUrl(`/api/admin/system/${action}`), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Admin-ID': user.id
          },
          body: JSON.stringify(params || {})
        });
        if (response?.success) {
          setAlert({ type: 'success', message: `System action '${action}' completed successfully` });
          loadSystemHealthData();
        }
      }
    } catch (error) {
      setAlert({ type: 'error', message: `Failed to execute system action: ${action}` });
    }
  };

  const renderSystemMonitoring = () => {
    return (
      <SystemMonitoringTab
        systemHealth={systemHealth}
        systemMetrics={systemMetrics}
        performanceData={performanceData}
        onSystemAction={handleSystemAction}
        loading={loading}
        formatDate={formatDate}
        showAlert={(type, message) => setAlert({ type, message })}
      />
    );
  };

  const loadSecuritySettings = async () => {
    try {
      setLoadingSecurity(true);
      const response = await getJsonWithRetry(getApiUrl('/api/admin/security-settings'), {
        headers: { 'X-Admin-ID': user.id }
      });
      if (response?.success) {
        setSecuritySettings(response.settings || {});
      }
    } catch (error) {
      console.error('Failed to load security settings:', error);
    } finally {
      setLoadingSecurity(false);
    }
  };

  useEffect(() => {
    if (selectedSection === 'security') {
      loadSecuritySettings();
    }
  }, [selectedSection]);

  const renderSecurity = () => {
    if (loadingSecurity) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress sx={{ color: '#f44336' }} />
        </Box>
      );
    }

    return (
    <Box>
        {alert && (
          <Alert severity={alert.type} sx={{ mb: 3 }} onClose={() => setAlert(null)}>
            {alert.message}
          </Alert>
        )}

        <Typography variant="h5" sx={{ color: '#f44336', mb: 3, fontWeight: 600 }}>
          🔒 Security & Access Control
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
      <Card sx={{
        backgroundColor: 'rgba(26, 26, 46, 0.8)',
              border: '1px solid rgba(244, 67, 54, 0.2)'
      }}>
        <CardContent>
                <Typography variant="h6" sx={{ color: '#f44336', mb: 3 }}>
                  Authentication Settings
          </Typography>
                <FormControlLabel
                  control={
                    <Checkbox
                      defaultChecked={securitySettings?.require_2fa || false}
                      sx={{ color: '#f44336', '&.Mui-checked': { color: '#f44336' } }}
                    />
                  }
                  label="Require Two-Factor Authentication"
                  sx={{ color: 'white', mb: 2, display: 'block' }}
                />
                <TextField
                  fullWidth
                  label="Session Timeout (minutes)"
                  type="number"
                  defaultValue={securitySettings?.session_timeout || 60}
                  sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: 'white' } }}
                />
                <TextField
                  fullWidth
                  label="Max Login Attempts"
                  type="number"
                  defaultValue={securitySettings?.max_login_attempts || 5}
                  sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: 'white' } }}
                />
                <Button
                  variant="contained"
                  onClick={async () => {
                    try {
                      setLoading(true);
                      await getJsonWithRetry(getApiUrl('/api/admin/security-settings'), {
                        method: 'PUT',
                        headers: {
                          'Content-Type': 'application/json',
                          'X-Admin-ID': user.id
                        },
                        body: JSON.stringify(securitySettings)
                      });
                      setAlert({ type: 'success', message: 'Authentication settings updated successfully' });
                      loadSecuritySettings();
                    } catch (error) {
                      setAlert({ type: 'error', message: 'Failed to update authentication settings' });
                    } finally {
                      setLoading(false);
                    }
                  }}
                  sx={{ background: 'linear-gradient(45deg, #f44336, #d32f2f)' }}
                >
                  Save Authentication Settings
                </Button>
        </CardContent>
      </Card>
          </Grid>

          <Grid item xs={12} md={6}>
      <Card sx={{
        backgroundColor: 'rgba(26, 26, 46, 0.8)',
        border: '1px solid rgba(244, 67, 54, 0.2)'
      }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: '#f44336', mb: 3 }}>
                  Access Control
          </Typography>
                <FormControlLabel
                  control={
                    <Checkbox
                      defaultChecked={securitySettings?.ip_whitelist_enabled || false}
                      sx={{ color: '#f44336', '&.Mui-checked': { color: '#f44336' } }}
                    />
                  }
                  label="Enable IP Whitelist"
                  sx={{ color: 'white', mb: 2, display: 'block' }}
                />
                <TextField
                  fullWidth
                  label="Allowed IP Addresses (comma-separated)"
                  multiline
                  rows={3}
                  defaultValue={securitySettings?.allowed_ips || ''}
                  sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: 'white' } }}
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      defaultChecked={securitySettings?.audit_logging || true}
                      sx={{ color: '#f44336', '&.Mui-checked': { color: '#f44336' } }}
                    />
                  }
                  label="Enable Audit Logging"
                  sx={{ color: 'white', mb: 2, display: 'block' }}
                />
                <Button
                  variant="contained"
                  onClick={async () => {
                    try {
                      setLoading(true);
                      await getJsonWithRetry(getApiUrl('/api/admin/security-settings'), {
                        method: 'PUT',
                        headers: {
                          'Content-Type': 'application/json',
                          'X-Admin-ID': user.id
                        },
                        body: JSON.stringify(securitySettings)
                      });
                      setAlert({ type: 'success', message: 'Access control settings updated successfully' });
                      loadSecuritySettings();
                    } catch (error) {
                      setAlert({ type: 'error', message: 'Failed to update access control settings' });
                    } finally {
                      setLoading(false);
                    }
                  }}
                  sx={{ background: 'linear-gradient(45deg, #f44336, #d32f2f)' }}
                >
                  Save Access Control
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Card sx={{
          backgroundColor: 'rgba(26, 26, 46, 0.8)',
          border: '1px solid rgba(244, 67, 54, 0.2)',
          mt: 3
        }}>
          <CardContent>
            <Typography variant="h6" sx={{ color: '#f44336', mb: 3 }}>
              Security Monitoring
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Card sx={{ backgroundColor: 'rgba(244, 67, 54, 0.1)', border: '1px solid rgba(244, 67, 54, 0.3)' }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ color: '#f44336', mb: 1 }}>
                      Failed Login Attempts (24h)
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                      {securitySettings?.failed_logins_24h || 0}
          </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card sx={{ backgroundColor: 'rgba(255, 152, 0, 0.1)', border: '1px solid rgba(255, 152, 0, 0.3)' }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ color: '#ff9800', mb: 1 }}>
                      Active Sessions
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                      {securitySettings?.active_sessions || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card sx={{ backgroundColor: 'rgba(76, 175, 80, 0.1)', border: '1px solid rgba(76, 175, 80, 0.3)' }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ color: '#4caf50', mb: 1 }}>
                      Security Status
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                      {securitySettings?.security_status === 'secure' ? '✅ SECURE' : '⚠️ REVIEW'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
        </CardContent>
      </Card>
    </Box>
  );
  };

  const renderAuditLogs = () => (
    <Box>
      <Typography variant="h5" sx={{ color: '#00d4ff', mb: 3, fontWeight: 600 }}>
        📋 Audit Logs & Compliance
      </Typography>

      {/* Audit Filter Controls */}
      <Card sx={{
        background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%)',
        border: '1px solid rgba(0, 212, 255, 0.3)',
        mb: 3
      }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                select
                fullWidth
                label="Filter by Action"
                value={auditFilter}
                onChange={(e) => setAuditFilter(e.target.value)}
                size="small"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    '& fieldset': { borderColor: 'rgba(0, 212, 255, 0.3)' }
                  }
                }}
              >
                <MenuItem value="all">All Actions</MenuItem>
                <MenuItem value="user_management">User Management</MenuItem>
                <MenuItem value="fund_allocation">Fund Allocation</MenuItem>
                <MenuItem value="trading_control">Trading Control</MenuItem>
                <MenuItem value="system_config">System Config</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                type="date"
                label="Start Date"
                value={auditDateRange.start}
                onChange={(e) => setAuditDateRange(prev => ({ ...prev, start: e.target.value }))}
                size="small"
                InputLabelProps={{ shrink: true }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    '& fieldset': { borderColor: 'rgba(0, 212, 255, 0.3)' }
                  }
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                type="date"
                label="End Date"
                value={auditDateRange.end}
                onChange={(e) => setAuditDateRange(prev => ({ ...prev, end: e.target.value }))}
                size="small"
                InputLabelProps={{ shrink: true }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    '& fieldset': { borderColor: 'rgba(0, 212, 255, 0.3)' }
                  }
                }}
              />
            </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Box>
                    <Button
                      variant="outlined"
                      startIcon={<FileDownload />}
                      onClick={(e) => setAuditExportMenuAnchor(e.currentTarget)}
                      disabled={auditLogs.length === 0}
                      sx={{
                        borderColor: '#4caf50',
                        color: '#4caf50',
                        transition: 'all 0.2s ease',
                        '&:hover': { 
                          borderColor: '#4caf50', 
                          backgroundColor: 'rgba(76, 175, 80, 0.1)',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 4px 8px rgba(76, 175, 80, 0.3)'
                        },
                        '&:disabled': {
                          borderColor: 'rgba(255, 255, 255, 0.1)',
                          color: 'rgba(255, 255, 255, 0.3)'
                        }
                      }}
                    >
                      Export
                    </Button>
                    <Menu
                      anchorEl={auditExportMenuAnchor}
                      open={Boolean(auditExportMenuAnchor)}
                      onClose={() => setAuditExportMenuAnchor(null)}
                      PaperProps={{
                        sx: {
                          backgroundColor: 'rgba(26, 26, 46, 0.95)',
                          border: '1px solid rgba(0, 212, 255, 0.3)',
                          mt: 1
                        }
                      }}
                    >
                      <MenuItem onClick={() => {
                        const filteredLogs = auditLogs.filter(log => {
                          if (auditFilter !== 'all' && log.action_type !== auditFilter) return false;
                          if (auditDateRange.start && new Date(log.timestamp) < new Date(auditDateRange.start)) return false;
                          if (auditDateRange.end && new Date(log.timestamp) > new Date(auditDateRange.end)) return false;
                          return true;
                        });
                        exportAuditLogs(filteredLogs, 'csv');
                        setAuditExportMenuAnchor(null);
                      }} sx={{ color: 'white' }}>
                        Export as CSV
                      </MenuItem>
                      <MenuItem onClick={() => {
                        const filteredLogs = auditLogs.filter(log => {
                          if (auditFilter !== 'all' && log.action_type !== auditFilter) return false;
                          if (auditDateRange.start && new Date(log.timestamp) < new Date(auditDateRange.start)) return false;
                          if (auditDateRange.end && new Date(log.timestamp) > new Date(auditDateRange.end)) return false;
                          return true;
                        });
                        exportAuditLogs(filteredLogs, 'json');
                        setAuditExportMenuAnchor(null);
                      }} sx={{ color: 'white' }}>
                        Export as JSON
                      </MenuItem>
                      <MenuItem onClick={async () => {
                        const filteredLogs = auditLogs.filter(log => {
                          if (auditFilter !== 'all' && log.action_type !== auditFilter) return false;
                          if (auditDateRange.start && new Date(log.timestamp) < new Date(auditDateRange.start)) return false;
                          if (auditDateRange.end && new Date(log.timestamp) > new Date(auditDateRange.end)) return false;
                          return true;
                        });
                        const formatted = filteredLogs.map(log => ({
                          'Timestamp': log.timestamp,
                          'Admin': log.admin_username,
                          'Action': log.action_type,
                          'Details': log.action_details,
                          'Target': log.target_username || log.target_user_id,
                          'Result': log.result,
                          'IP Address': log.ip_address
                        }));
                        await exportToPDF(formatted, `prometheus-audit-logs-${new Date().toISOString().slice(0, 10)}`, 'Audit Logs Export');
                        setAuditExportMenuAnchor(null);
                      }} sx={{ color: 'white' }}>
                        Export as PDF
                      </MenuItem>
                      <MenuItem onClick={async () => {
                        const filteredLogs = auditLogs.filter(log => {
                          if (auditFilter !== 'all' && log.action_type !== auditFilter) return false;
                          if (auditDateRange.start && new Date(log.timestamp) < new Date(auditDateRange.start)) return false;
                          if (auditDateRange.end && new Date(log.timestamp) > new Date(auditDateRange.end)) return false;
                          return true;
                        });
                        const formatted = filteredLogs.map(log => ({
                          'Timestamp': log.timestamp,
                          'Admin': log.admin_username,
                          'Action': log.action_type,
                          'Details': log.action_details,
                          'Target': log.target_username || log.target_user_id,
                          'Result': log.result,
                          'IP Address': log.ip_address
                        }));
                        await exportToExcel(formatted, `prometheus-audit-logs-${new Date().toISOString().slice(0, 10)}`);
                        setAuditExportMenuAnchor(null);
                      }} sx={{ color: 'white' }}>
                        Export as Excel
                      </MenuItem>
                    </Menu>
                  </Box>
              <Button
                fullWidth
                variant="contained"
                startIcon={<Refresh />}
                onClick={loadAuditData}
                sx={{
                  background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                  '&:hover': { background: 'linear-gradient(45deg, #0099cc, #007aa3)' }
                }}
              >
                  Refresh
              </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Audit Logs Table */}
      <Card sx={{
        background: 'rgba(26, 26, 26, 0.95)',
        border: '1px solid rgba(0, 212, 255, 0.3)'
      }}>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Timestamp</TableCell>
                  <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Admin</TableCell>
                  <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Action</TableCell>
                  <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Target</TableCell>
                  <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Details</TableCell>
                  <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Result</TableCell>
                  <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>IP Address</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {auditLogs.length > 0 ? auditLogs.map((log) => (
                  <TableRow key={log.log_id} hover>
                    <TableCell sx={{ color: 'white' }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell sx={{ color: 'white' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Avatar sx={{ width: 24, height: 24, bgcolor: '#00d4ff', fontSize: '0.75rem' }}>
                          {log.admin_username?.charAt(0).toUpperCase()}
                        </Avatar>
                        {log.admin_username}
                      </Box>
                    </TableCell>
                    <TableCell sx={{ color: 'white' }}>
                      <Chip
                        label={log.action_type.replace('_', ' ').toUpperCase()}
                        size="small"
                        sx={{
                          backgroundColor: getActionTypeColor(log.action_type),
                          color: 'white',
                          fontWeight: 500
                        }}
                      />
                    </TableCell>
                    <TableCell sx={{ color: 'white' }}>
                      {log.target_username || log.target_user_id || '-'}
                    </TableCell>
                    <TableCell sx={{ color: 'white', maxWidth: 200 }}>
                      <Typography variant="body2" sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>
                        {log.action_details}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={log.result.toUpperCase()}
                        size="small"
                        color={log.result === 'success' ? 'success' : log.result === 'failure' ? 'error' : 'warning'}
                        sx={{ fontWeight: 500 }}
                      />
                    </TableCell>
                    <TableCell sx={{ color: 'white', fontSize: '0.75rem' }}>
                      {log.ip_address}
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={7} sx={{ textAlign: 'center', color: '#aaa', py: 4 }}>
                      <Box sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: 2,
                        py: 4,
                        animation: 'fadeIn 0.5s ease-out',
                        '@keyframes fadeIn': {
                          from: { opacity: 0 },
                          to: { opacity: 1 }
                        }
                      }}>
                        {loadingAudit ? (
                          <>
                            <CircularProgress sx={{ color: '#00d4ff' }} />
                            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                              Loading audit logs...
                            </Typography>
                          </>
                        ) : (
                          <>
                            <Assessment sx={{
                              fontSize: 48,
                              color: 'rgba(255, 255, 255, 0.3)',
                              animation: 'float 3s ease-in-out infinite',
                              '@keyframes float': {
                                '0%, 100%': { transform: 'translateY(0px)' },
                                '50%': { transform: 'translateY(-10px)' }
                              }
                            }} />
                            <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 600 }}>
                              No audit logs found
                            </Typography>
                            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                              Audit logs will appear here as actions are performed.
                            </Typography>
                          </>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );

  const renderPlaceholder = () => (
    <Card sx={{
      backgroundColor: 'rgba(26, 26, 46, 0.8)',
      border: '1px solid rgba(0, 212, 255, 0.2)',
      borderRadius: 3,
      animation: 'fadeIn 0.5s ease-out',
      '@keyframes fadeIn': {
        from: { opacity: 0 },
        to: { opacity: 1 }
      }
    }}>
      <CardContent sx={{ p: 4, textAlign: 'center' }}>
        <Box sx={{
          width: 80,
          height: 80,
          borderRadius: '50%',
          backgroundColor: 'rgba(0, 212, 255, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mx: 'auto',
          mb: 3
        }}>
          <SettingsIcon sx={{ fontSize: 40, color: '#00d4ff' }} />
        </Box>
        <Typography variant="h5" sx={{ color: '#00d4ff', mb: 2, fontWeight: 700 }}>
          {selectedSection.replace('-', ' ').toUpperCase()} PANEL
        </Typography>
        <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 2 }}>
          This section will contain the full {selectedSection.replace('-', ' ')} functionality.
        </Typography>
        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
          Implementation in progress...
        </Typography>
      </CardContent>
    </Card>
  );

  const renderSidebarContent = () => (
    <Box sx={{ width: 280, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Sidebar Header */}
      <Box sx={{
        p: 2,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
          <Typography variant="h6" sx={{
            color: '#00d4ff',
            fontWeight: 700,
            fontSize: '1.1rem'
          }}>
            🚀 ADMIN COCKPIT
          </Typography>
          {/* WebSocket Connection Status */}
          <Tooltip title={wsConnected ? 'Real-time updates connected' : wsError || 'Connecting to real-time updates...'} arrow>
            <Box sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: wsConnected ? '#4caf50' : '#ff9800',
              animation: wsConnected ? 'none' : 'pulse 2s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': { opacity: 1 },
                '50%': { opacity: 0.5 }
              }
            }} />
          </Tooltip>
        </Box>
        <IconButton
          onClick={() => setSidebarOpen(false)}
          sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
        >
          <ChevronLeft />
        </IconButton>
      </Box>

      {/* Navigation Sections */}
      <Box sx={{ flex: 1, overflow: 'auto', py: 1 }}>
        {navigationSections.map((section) => (
          <Box key={section.id}>
            <ListItem
              button
              onClick={() => toggleSection(section.id)}
              sx={{
                px: 2,
                py: 1,
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.05)'
                }
              }}
            >
              <ListItemIcon sx={{ color: '#00d4ff', minWidth: 40 }}>
                <section.icon />
              </ListItemIcon>
              <ListItemText
                primary={section.label}
                primaryTypographyProps={{
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  color: 'rgba(255, 255, 255, 0.9)'
                }}
              />
              {section.badge && (
                <Badge badgeContent={section.badge} color="error" sx={{ mr: 1 }} />
              )}
              {openSections[section.id] ? <ExpandLess sx={{ color: '#00d4ff' }} /> : <ExpandMore sx={{ color: '#00d4ff' }} />}
            </ListItem>

            <Collapse in={openSections[section.id]} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                {section.children?.map((item) => (
                  <ListItem
                    key={item.id}
                    button
                    selected={selectedSection === item.id}
                    onClick={() => handleItemSelect(item.id)}
                    sx={{
                      pl: 4,
                      py: 0.5,
                      '&.Mui-selected': {
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        borderRight: '3px solid #00d4ff',
                        '&:hover': {
                          backgroundColor: 'rgba(0, 212, 255, 0.15)'
                        }
                      },
                      '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)'
                      }
                    }}
                  >
                    <ListItemIcon sx={{ color: item.color || 'rgba(255, 255, 255, 0.7)', minWidth: 36 }}>
                      <item.icon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={item.label}
                      primaryTypographyProps={{
                        fontSize: '0.85rem',
                        color: selectedSection === item.id ? '#00d4ff' : 'rgba(255, 255, 255, 0.8)'
                      }}
                    />
                    {item.badge && (
                      <Chip
                        label={item.badge}
                        size="small"
                        sx={{
                          height: 18,
                          fontSize: '0.7rem',
                          backgroundColor: item.color || '#ff9800',
                          color: 'white',
                          fontWeight: 600
                        }}
                      />
                    )}
                  </ListItem>
                ))}
              </List>
            </Collapse>
          </Box>
        ))}
      </Box>

      {/* Sidebar Footer */}
      <Box sx={{
        p: 2,
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        backgroundColor: 'rgba(0, 0, 0, 0.2)'
      }}>
        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
          PROMETHEUS v3.0.0
        </Typography>
        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)', display: 'block' }}>
          Enterprise Admin Portal
        </Typography>
      </Box>
    </Box>
  );

  return (
    <ErrorBoundary>
      <MobileNavigation user={{
        id: user.id,
        name: user.username || user.email.split('@')[0],
        email: user.email,
        role: user.role || 'user'
      }} onLogout={onLogout} />
      <Box sx={{
        display: 'flex',
        minHeight: '100vh',
        backgroundColor: '#0a0a0a'
      }}>
        {/* Sidebar */}
        <Drawer
          variant="persistent"
          anchor="left"
          open={sidebarOpen}
          sx={{
            display: { xs: 'none', md: 'block' },
            width: sidebarOpen ? 280 : 0,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: 280,
              boxSizing: 'border-box',
              backgroundColor: 'rgba(26, 26, 46, 0.95)',
              borderRight: '1px solid rgba(0, 212, 255, 0.2)',
              backdropFilter: 'blur(10px)'
            }
          }}
      >
        {renderSidebarContent()}
      </Drawer>

      {/* Main Content Area */}
      <Box sx={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        marginLeft: sidebarOpen ? 0 : 0,
        transition: 'margin-left 0.3s ease'
      }}>
        {/* Header - TradingCommandCenter (Contextual - Only for Trading Tabs) */}
        {['paper-trading', 'live-trading', 'portfolio'].includes(selectedSection) && (
          <Box sx={{ p: 3, pb: 0 }}>
            <TradingCommandCenter user={user} onLogout={onLogout} />
          </Box>
        )}

        {/* Main Content */}
        <Box sx={{ flex: 1, p: 3 }}>
          {!sidebarOpen && (
            <IconButton
              onClick={() => setSidebarOpen(true)}
              sx={{
                position: 'fixed',
                top: 20,
                left: 20,
                zIndex: 1000,
                backgroundColor: 'rgba(0, 212, 255, 0.1)',
                color: '#00d4ff',
                '&:hover': {
                  backgroundColor: 'rgba(0, 212, 255, 0.2)'
                }
              }}
            >
              <MenuIcon />
            </IconButton>
          )}

          {/* Dynamic Content Based on Selection */}
          <Box>
            <Typography variant="h4" sx={{
              color: 'white',
              fontWeight: 600,
              mb: 1,
              textTransform: 'capitalize'
            }}>
              {selectedSection.replace('-', ' ')}
            </Typography>
            <Typography variant="subtitle1" sx={{
              color: 'rgba(255, 255, 255, 0.7)',
              mb: 3
            }}>
              {getPageDescription(selectedSection)}
            </Typography>

            {/* Dynamic Content Based on Selection */}
            {renderMainContent()}
          </Box>
        </Box>
      </Box>

      {/* Global Search Dialog */}
      <Dialog
        open={showGlobalSearch}
        onClose={() => setShowGlobalSearch(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(26, 26, 46, 0.95)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 3,
            animation: 'dialogSlideIn 0.3s ease-out',
            '@keyframes dialogSlideIn': {
              from: { opacity: 0, transform: 'scale(0.9) translateY(-20px)' },
              to: { opacity: 1, transform: 'scale(1) translateY(0)' }
            }
          }
        }}
      >
        <DialogTitle sx={{ color: '#00d4ff', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Search sx={{ fontSize: 24 }} />
          Global Search
          <Chip label="Ctrl+K" size="small" sx={{ ml: 'auto', backgroundColor: 'rgba(0, 212, 255, 0.2)', color: '#00d4ff' }} />
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            autoFocus
            placeholder="Search users, emails, or navigate to sections..."
            value={globalSearchQuery}
            onChange={(e) => {
              const query = e.target.value;
              setGlobalSearchQuery(query);
              handleGlobalSearch(query);
            }}
            sx={{
              mt: 2,
              '& .MuiOutlinedInput-root': {
                color: 'white',
                fontSize: '1.1rem',
                '& fieldset': { borderColor: 'rgba(0, 212, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
              },
              '& .MuiInputBase-input::placeholder': { color: 'rgba(255, 255, 255, 0.5)' }
            }}
            InputProps={{
              startAdornment: <Search sx={{ color: 'rgba(255, 255, 255, 0.5)', mr: 1 }} />
            }}
          />
          {globalSearchQuery && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1, fontWeight: 600 }}>
                Search Results:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                <Chip
                  label={`${filteredUsers.length} user(s)`}
                  sx={{ backgroundColor: 'rgba(0, 212, 255, 0.2)', color: '#00d4ff' }}
                />
                <Chip
                  label={`${auditLogs.filter(log => 
                    log.admin_username?.toLowerCase().includes(globalSearchQuery.toLowerCase()) ||
                    log.action_type?.toLowerCase().includes(globalSearchQuery.toLowerCase())
                  ).length} audit log(s)`}
                  sx={{ backgroundColor: 'rgba(156, 39, 176, 0.2)', color: '#9c27b0' }}
                />
                <Chip
                  label={`${notifications.filter(n => 
                    n.title?.toLowerCase().includes(globalSearchQuery.toLowerCase()) ||
                    n.message?.toLowerCase().includes(globalSearchQuery.toLowerCase())
                  ).length} notification(s)`}
                  sx={{ backgroundColor: 'rgba(255, 152, 0, 0.2)', color: '#ff9800' }}
                />
              </Box>
            </Box>
          )}
          
          {/* Search History */}
          {!globalSearchQuery && searchHistory.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1, fontWeight: 600 }}>
                Recent Searches:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {searchHistory.slice(0, 5).map((historyItem, idx) => (
                  <Chip
                    key={idx}
                    label={historyItem}
                    onClick={() => {
                      setGlobalSearchQuery(historyItem);
                      handleGlobalSearch(historyItem);
                    }}
                    onDelete={() => {
                      const newHistory = searchHistory.filter((_, i) => i !== idx);
                      setSearchHistory(newHistory);
                      localStorage.setItem('admin_search_history', JSON.stringify(newHistory));
                    }}
                    sx={{
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'rgba(255, 255, 255, 0.8)',
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'rgba(0, 212, 255, 0.2)',
                        color: '#00d4ff'
                      }
                    }}
                  />
                ))}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowGlobalSearch(false)} sx={{ color: '#aaa' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Keyboard Shortcuts Help Dialog */}
      <Dialog
        open={showKeyboardShortcuts}
        onClose={() => setShowKeyboardShortcuts(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(26, 26, 46, 0.95)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 3,
            animation: 'dialogSlideIn 0.3s ease-out',
            '@keyframes dialogSlideIn': {
              from: { opacity: 0, transform: 'scale(0.9) translateY(-20px)' },
              to: { opacity: 1, transform: 'scale(1) translateY(0)' }
            }
          }
        }}
      >
        <DialogTitle sx={{ color: '#00d4ff', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
          ⌨️ Keyboard Shortcuts
          <Chip label="Ctrl+/" size="small" sx={{ ml: 'auto', backgroundColor: 'rgba(0, 212, 255, 0.2)', color: '#00d4ff' }} />
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" sx={{ color: '#00d4ff', mb: 2, fontWeight: 600 }}>
              Navigation
            </Typography>
            {[
              { keys: 'Ctrl/Cmd + K', action: 'Open global search' },
              { keys: 'Ctrl/Cmd + /', action: 'Show keyboard shortcuts' },
              { keys: 'Ctrl/Cmd + R', action: 'Refresh data' },
              { keys: 'Esc', action: 'Close dialogs/modals' },
            ].map((shortcut, idx) => (
              <Box key={idx} sx={{ display: 'flex', justifyContent: 'space-between', py: 1.5, borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {shortcut.action}
                </Typography>
                <Chip
                  label={shortcut.keys}
                  size="small"
                  sx={{
                    backgroundColor: 'rgba(0, 212, 255, 0.2)',
                    color: '#00d4ff',
                    fontFamily: 'monospace',
                    fontSize: '0.75rem'
                  }}
                />
              </Box>
            ))}
            <Typography variant="subtitle2" sx={{ color: '#00d4ff', mb: 2, mt: 3, fontWeight: 600 }}>
              Navigation (G + key)
            </Typography>
            {[
              { keys: 'G + D', action: 'Go to Dashboard' },
              { keys: 'G + U', action: 'Go to User Management' },
              { keys: 'G + A', action: 'Go to Analytics' },
              { keys: 'G + T', action: 'Go to Live Trading' },
              { keys: 'G + P', action: 'Go to Paper Trading' },
              { keys: 'G + N', action: 'Go to Notifications' },
              { keys: 'G + S', action: 'Go to System Health' },
              { keys: 'G + F', action: 'Go to Fund Allocation' },
              { keys: 'G + L', action: 'Go to Audit Logs' },
            ].map((shortcut, idx) => (
              <Box key={idx} sx={{ display: 'flex', justifyContent: 'space-between', py: 1.5, borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {shortcut.action}
                </Typography>
                <Chip
                  label={shortcut.keys}
                  size="small"
                  sx={{
                    backgroundColor: 'rgba(0, 212, 255, 0.2)',
                    color: '#00d4ff',
                    fontFamily: 'monospace',
                    fontSize: '0.75rem'
                  }}
                />
              </Box>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowKeyboardShortcuts(false)} sx={{ color: '#aaa' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
    </ErrorBoundary>
  );

  // System Health render method
  function renderSystemHealth() {
    return (
      <Box>
        <Typography variant="h5" sx={{ color: '#00d4ff', mb: 3, fontWeight: 600 }}>
          🏥 System Health & Monitoring
        </Typography>

        {/* System Status Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: systemHealth?.overall_status === 'healthy'
                ? 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)'
                : 'linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%)',
              border: `1px solid ${systemHealth?.overall_status === 'healthy' ? 'rgba(76, 175, 80, 0.3)' : 'rgba(244, 67, 54, 0.3)'}`
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: systemHealth?.overall_status === 'healthy' ? '#4caf50' : '#f44336', mb: 1 }}>
                  System Status
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {systemHealth?.overall_status?.toUpperCase() || 'UNKNOWN'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%)',
              border: '1px solid rgba(0, 212, 255, 0.3)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1 }}>
                  Uptime
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                  {systemHealth?.uptime ? `${(systemHealth.uptime / 3600).toFixed(1)}h` : '0h'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Resource Usage */}
        <Card sx={{
          background: 'rgba(26, 26, 26, 0.95)',
          border: '1px solid rgba(0, 212, 255, 0.3)'
        }}>
          <CardContent>
            <Typography variant="h6" sx={{ color: '#00d4ff', mb: 3 }}>
              Resource Usage
            </Typography>
            <Grid container spacing={3}>
              {[
                { label: 'CPU Usage', value: systemHealth?.cpu_usage || 0, color: '#4caf50' },
                { label: 'Memory Usage', value: systemHealth?.memory_usage || 0, color: '#ff9800' },
                { label: 'Disk Usage', value: systemHealth?.disk_usage || 0, color: '#f44336' }
              ].map((metric, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" sx={{ color: 'white' }}>
                        {metric.label}
                      </Typography>
                      <Typography variant="body2" sx={{ color: metric.color, fontWeight: 600 }}>
                        {metric.value.toFixed(1)}%
                      </Typography>
                    </Box>
                    <Tooltip title={`${metric.label}: ${metric.value.toFixed(1)}%`} arrow>
                    <LinearProgress
                      variant="determinate"
                      value={metric.value}
                        aria-label={`${metric.label}: ${metric.value.toFixed(1)}%`}
                        aria-valuenow={metric.value}
                        aria-valuemin={0}
                        aria-valuemax={100}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: metric.color,
                            borderRadius: 4,
                            transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
                            boxShadow: `0 0 10px ${metric.color}60`
                        }
                      }}
                    />
                    </Tooltip>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Box>
    );
  };

  // Load consolidated data on component mount
  useEffect(() => {
    loadAdminData();
    loadAuditData();
    loadInvitations();
    loadSystemHealthData();
    loadPermissions();
  }, []);
};

// Helper function for page descriptions
const getPageDescription = (section: string): string => {
  const descriptions: Record<string, string> = {
    'dashboard': 'System overview and key performance metrics',
    'analytics': 'Advanced analytics and performance insights',
    'notifications': 'System alerts and user notifications',
    'paper-trading': 'Paper trading management and monitoring',
    'live-trading': 'Live trading controls and real-time monitoring',
    'portfolio': 'Portfolio management and performance tracking',
    'ai-systems': 'AI system management and optimization',
    'taf-analysis': 'FINRA TAF fee impact analysis and optimization recommendations',
    'strategy-management': 'Trading strategy configuration and analysis',
    'user-management': 'User accounts, approvals, and tier management',
    'fund-allocation': 'Fund allocation and live trading activation',
    'permissions': 'Role-based permissions and access control',
    'system-config': 'System configuration and settings',
    'security': 'Security settings and access controls',
    'audit-logs': 'System audit trails and compliance reporting',
    'monitoring': 'Real-time system health and performance monitoring',
    'user-invitations': 'User invitation management and tracking',
    'system-health': 'System health monitoring and resource usage'
  };
  return descriptions[section] || 'Advanced admin functionality';
};

// Memoize the component to prevent unnecessary re-renders
export default memo(UnifiedCockpitAdminDashboard);
