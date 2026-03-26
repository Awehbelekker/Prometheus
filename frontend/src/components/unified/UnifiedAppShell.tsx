import React, { useState, Suspense } from 'react';
import EnterpriseAdminPanel from '../EnterpriseAdminPanel';
import { Box, CircularProgress, Alert, Typography } from '@mui/material';
import CleanNavigation from './CleanNavigation';
import UnifiedDashboard from './UnifiedDashboard';
import IntuitiveHolographicUI from './IntuitiveholographicUI';
import DashboardStyleSelector from './DashboardStyleSelector';
import ThemeSystem from './ThemeSystem';
import ErrorBoundary from '../ErrorBoundary';

/**
 * 🎯 UNIFIED APP SHELL - SINGLE SOURCE OF TRUTH
 * 
 * FEATURES:
 * - Single app shell for all users
 * - Tier-based content rendering
 * - Clean, seamless experience
 * - No duplicated components
 * - Responsive design
 * - Error boundaries
 */

interface UnifiedAppShellProps {
  user: {
    id: string;
    username?: string;
    email?: string;
    role: string;
    tier?: 'demo' | 'premium' | 'admin';
  } | null;
  onLogout: () => void;
}

// Lazy load components for better performance
const TradingDashboard = React.lazy(() => import('../TradingDashboard'));
const AnalyticsDashboard = React.lazy(() => import('../EnhancedAnalyticsDashboard'));
const AIAgentsDashboard = React.lazy(() => import('../HierarchicalAgentCoordinator'));
const UserManagement = React.lazy(() => import('../UserManagement'));
const AccessRequestManagement = React.lazy(() => import('../AccessRequestManagement'));
const ComprehensivePerformanceReview = React.lazy(() => import('../ComprehensivePerformanceReview'));
const SystemHealth = React.lazy(() => import('../SystemHealthDashboard'));
const Settings = React.lazy(() => import('../EnhancedForms'));

const UnifiedAppShell: React.FC<UnifiedAppShellProps> = ({ user, onLogout }) => {
  const [selectedItem, setSelectedItem] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedHeader, setSelectedHeader] = useState('command-center');
  const [selectedTheme, setSelectedTheme] = useState('dark');

  // Provide safe defaults for user
  const safeUser = {
    id: user?.id || 'unknown',
    username: user?.username || user?.email?.split('@')[0] || 'User',
    email: user?.email || 'user@example.com',
    role: user?.role || 'user',
    tier: (user?.tier || (user?.role === 'admin' ? 'admin' : 'demo')) as 'demo' | 'premium' | 'admin'
  };

  const handleItemSelect = (itemId: string) => {
    setSelectedItem(itemId);
  };

  const handleToggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const renderMainContent = () => {
    const commonProps = {
      user: safeUser,
      onLogout,
      selectedHeader,
      onHeaderChange: setSelectedHeader,
      selectedTheme,
      onThemeChange: setSelectedTheme
    };

    switch (selectedItem) {
      case 'dashboard':
        return <UnifiedDashboard {...commonProps} />;
      
      case 'paper-trading':
      case 'live-trading':
        return (
          <Suspense fallback={<LoadingSpinner />}>
            <TradingDashboard mode={selectedItem === 'live-trading' ? 'live' : 'paper'} />
          </Suspense>
        );
      
      case 'analytics':
        return (
          <Suspense fallback={<LoadingSpinner />}>
            <AnalyticsDashboard />
          </Suspense>
        );
      
      case 'holographic-ui':
        return <IntuitiveHolographicUI />;
      
      case 'ai-agents':
        return (
          <Suspense fallback={<LoadingSpinner />}>
            <AIAgentsDashboard />
          </Suspense>
        );
      
      case 'user-management':
        return (
          <Suspense fallback={<LoadingSpinner />}>
            <UserManagement />
          </Suspense>
        );

      case 'access-requests':
        return (
          <Suspense fallback={<LoadingSpinner />}>
            <AccessRequestManagement user={safeUser} />
          </Suspense>
        );

      case 'performance-review':
        return (
          <Suspense fallback={<LoadingSpinner />}>
            <ComprehensivePerformanceReview user={safeUser} />
          </Suspense>
        );

      case 'system-health':
        return (
          <Suspense fallback={<LoadingSpinner />}>
            <SystemHealth />
          </Suspense>
        );
      
      case 'profile':
      case 'preferences':
        return (
          <Box sx={{ p: 3, minHeight: '100vh', backgroundColor: '#0a0a0a', color: 'white' }}>
            <Typography variant="h4" sx={{ mb: 4, fontWeight: 700, color: '#00d4ff' }}>
              ⚙️ {selectedItem === 'profile' ? 'Profile Settings' : 'User Preferences'}
            </Typography>
            <Typography variant="body1" sx={{ color: '#aaa' }}>
              {selectedItem === 'profile' && 'Manage your profile information and account details.'}
              {selectedItem === 'preferences' && 'Customize your trading preferences and notifications.'}
            </Typography>
          </Box>
        );
      case 'admin-settings':
        return (
          <EnterpriseAdminPanel />
        );
      
      case 'portfolio':
        return (
          <Box sx={{ p: 3, color: 'white' }}>
            <h2>Portfolio Management</h2>
            <p>Your portfolio overview and management tools.</p>
          </Box>
        );
      
      case 'quantum-trading':
        return (
          <Box sx={{ p: 3, color: 'white' }}>
            <h2>🔮 Quantum Trading Engine</h2>
            <p>Advanced quantum-enhanced trading algorithms.</p>
          </Box>
        );
      
      case 'notifications':
        return (
          <Box sx={{ p: 3, color: 'white' }}>
            <h2>📢 Notifications</h2>
            <p>Your trading alerts and system notifications.</p>
          </Box>
        );

      case 'dashboard-style':
        return (
          <Box sx={{ p: 3, minHeight: '100vh', backgroundColor: '#0a0a0a', color: 'white' }}>
            <Typography variant="h4" sx={{ mb: 4, fontWeight: 700, color: '#00d4ff' }}>
              🎯 Dashboard Style Settings
            </Typography>
            <DashboardStyleSelector
              selectedHeader={selectedHeader}
              onHeaderChange={setSelectedHeader}
            />
          </Box>
        );

      case 'theme-settings':
        return (
          <Box sx={{ p: 3, minHeight: '100vh', backgroundColor: '#0a0a0a', color: 'white' }}>
            <Typography variant="h4" sx={{ mb: 4, fontWeight: 700, color: '#00d4ff' }}>
              🎨 Theme Settings
            </Typography>
            <ThemeSystem
              selectedTheme={selectedTheme}
              onThemeChange={setSelectedTheme}
            />
          </Box>
        );

      default:
        return (
          <Box sx={{ 
            p: 3, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            minHeight: '400px'
          }}>
            <Alert severity="info">
              Feature "{selectedItem}" is coming soon!
            </Alert>
          </Box>
        );
    }
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      minHeight: '100vh',
      backgroundColor: '#0a0a0a'
    }}>
      {/* Navigation Sidebar */}
      <CleanNavigation
        selectedItem={selectedItem}
        onItemSelect={handleItemSelect}
        userTier={safeUser.tier}
        collapsed={sidebarCollapsed}
        onToggleCollapse={handleToggleSidebar}
        selectedHeader={selectedHeader}
        onHeaderChange={setSelectedHeader}
        selectedTheme={selectedTheme}
        onThemeChange={setSelectedTheme}
      />

      {/* Main Content Area */}
      <Box sx={{
        flex: 1,
        overflow: 'auto',
        minHeight: '100vh',
        backgroundColor: '#0a0a0a'
      }}>
        <ErrorBoundary>
          {renderMainContent()}
        </ErrorBoundary>
      </Box>
    </Box>
  );
};

// Loading component
const LoadingSpinner: React.FC = () => (
  <Box sx={{
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '400px',
    flexDirection: 'column',
    gap: 2
  }}>
    <CircularProgress sx={{ color: '#00d4ff' }} aria-label="Loading" role="progressbar" />
    <Box sx={{ color: '#aaa', textAlign: 'center' }} aria-live="polite">
      Loading...
    </Box>
  </Box>
);

export default UnifiedAppShell;
