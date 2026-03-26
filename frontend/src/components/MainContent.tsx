import React, { useState, Suspense, useEffect } from 'react';
import TopNavigation from './TopNavigation';
import './MainContent.css';
import { ROUTES_BY_ID } from '../routes/routeMap';
import { useUserContext } from '../context/UserContext';
import ErrorBoundary from './ErrorBoundary';
import DashboardSkeleton from './skeletons/DashboardSkeleton';
import AnalyticsSkeleton from './skeletons/AnalyticsSkeleton';
import LiveTradingSkeleton from './skeletons/LiveTradingSkeleton';
import HRMSkeleton from './skeletons/HRMSkeleton';
import AdminFeatureBadges from './AdminFeatureBadges';

// Fallback simple loader
const Loader = () => <div style={{ padding: '2rem' }}>Loading...</div>;

interface MainContentProps {
  selectedItem: string;
  currentUser?: { role: string; metadata?: any } | null;
  platformStatuses?: Array<{
    id: string;
    name: string;
    status: 'connected' | 'disconnected' | 'syncing';
    lastSync: string;
    tradingVolume: number;
  }>;
  notifications?: Array<{
    id: string;
    message: string;
    type: string;
    read: boolean;
  }>;
}

const MainContent: React.FC<MainContentProps> = ({ 
  selectedItem, 
  currentUser,
  platformStatuses,
  notifications
}) => {
  // Props to pass to all dashboard components
  const commonProps = {
    platformStatuses,
    notifications
  };
  
  const { userMeta, loading, error, setInvestment } = useUserContext();

  // Trial activation handled via context (activateTrial) if needed in future UI.

  // Prompt for initial investment if not set
  const [showInvestmentPrompt, setShowInvestmentPrompt] = useState(false);
  const [investmentInput, setInvestmentInput] = useState('');
  const [currencyInput, setCurrencyInput] = useState('USD');
  useEffect(() => {
    if (currentUser?.role === 'user' && (!userMeta.investment_amount || userMeta.investment_amount <= 0)) {
      setShowInvestmentPrompt(true);
    } else {
      setShowInvestmentPrompt(false);
    }
  }, [userMeta, currentUser]);

  const handleSetInvestment = async (e: React.FormEvent) => {
    e.preventDefault();
    await setInvestment(parseFloat(investmentInput), currencyInput);
    setShowInvestmentPrompt(false);
  };

  // Admin live trading state
  // Admin live trading moved to future context/service (stub removed here)
  const adminLiveStatus = '';
  const adminLiveLoading = false;
  const adminLiveError: string | null = null;
  const handleAdminStartLive = () => {/* TODO integrate service */};

  const getPageTitle = () => ROUTES_BY_ID[selectedItem]?.title || 'Dashboard';

  const renderContent = () => {
    const route = ROUTES_BY_ID[selectedItem] || ROUTES_BY_ID['dashboard'];
    // Role gating
    if (route?.roles && !route.roles.includes(currentUser?.role || '')) {
      return (
        <div className="page-container">
          <h2>Access Denied</h2>
          <p>You don't have permission to view this area.</p>
        </div>
      );
    }

    // Special dashboard investment/trial logic remains for 'dashboard'
    if (route.id === 'dashboard') {
      if (currentUser?.role === 'user') {
        if (showInvestmentPrompt) {
          return (
            <div className="investment-form-container">
              <h2>Set Your Initial Investment</h2>
              <form onSubmit={handleSetInvestment}>
                <div className="form-group">
                  <label htmlFor="investment-amount">Amount:</label>
                  <input
                    id="investment-amount"
                    name="investment-amount"
                    type="number"
                    min="1"
                    step="0.01"
                    value={investmentInput}
                    onChange={e => setInvestmentInput(e.target.value)}
                    required
                    placeholder="Enter investment amount"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <select
                    id="currency-select"
                    name="currency-select"
                    value={currencyInput}
                    onChange={e => setCurrencyInput(e.target.value)}
                    aria-label="Select currency"
                    className="form-input"
                  >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="ZAR">ZAR</option>
                    <option value="JPY">JPY</option>
                    <option value="CNY">CNY</option>
                    <option value="INR">INR</option>
                    <option value="BTC">BTC</option>
                    <option value="ETH">ETH</option>
                  </select>
                </div>
                <button type="submit" disabled={loading} className="submit-button">
                  {loading ? 'Saving...' : 'Save Investment'}
                </button>
                {error && <div className="error-message">{error}</div>}
              </form>
            </div>
          );
        }
        return React.createElement(ROUTES_BY_ID['user-dashboard'].lazy as any, {});
      }
      if (currentUser?.role === 'admin') {
        return (
          <div className="admin-live-container" style={{display:'flex', flexDirection:'column', gap:24}}>
            <AdminFeatureBadges />
            <div style={{border:'1px solid #333', padding:16, borderRadius:8}}>
              <h2 style={{marginTop:0}}>Admin Live Trading Control</h2>
              <button onClick={handleAdminStartLive} disabled={adminLiveLoading} className="admin-live-button">
                {adminLiveLoading ? 'Starting...' : 'Start Live Trading'}
              </button>
              {adminLiveStatus && <div className="admin-live-status">{adminLiveStatus}</div>}
              {adminLiveError && <div className="admin-live-error">{adminLiveError}</div>}
              <div className="admin-live-section">
                <h3>Live Trading Results (Real Money)</h3>
                <p>Results and logs will appear here after live trading is started.</p>
              </div>
            </div>
          </div>
        );
      }
    }

    if (loading) {
      if (route.id === 'dashboard') return <DashboardSkeleton />;
      if (route.id === 'analytics') return <AnalyticsSkeleton />;
      if (route.id === 'live-trading') return <LiveTradingSkeleton />;
      if (route.id === 'hrm-dashboard') return <HRMSkeleton />;
    }
    const Component: any = route.lazy as any;
    return <Component currentUser={currentUser} {...commonProps} />;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <a href="#main-content" className="skip-to-content">Skip to content</a>
      <TopNavigation
        currentUser={currentUser}
        title={getPageTitle()}
        showStats={selectedItem === 'dashboard' || selectedItem === 'admin'}
      />
      <div id="main-content" style={{ flex: 1, overflow: 'auto' }} tabIndex={-1}>
        <ErrorBoundary>
          <Suspense fallback={<Loader />}>{renderContent()}</Suspense>
        </ErrorBoundary>
      </div>
    </div>
  );
};

export default MainContent;
