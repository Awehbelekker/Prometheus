// PROMETHEUS Trading Platform - Version 2025.10.08
import React, { useState, useEffect, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import {
  Box, ThemeProvider, CssBaseline
} from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import './App.css';
import './styles/animations.css';
import './styles/modern-ui.css';
import './styles/modern-design-system.css';
import './styles/accessibility.css';
import './styles/logo-fix.css';
import './styles/responsive.css';

// PWA Manager
import { pwaManager } from './utils/pwa';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 3,
      staleTime: 30000, // 30 seconds
    },
  },
});



// Import API service
import { apiService } from './services/api';

// Import components
import PrometheusShowcase from './components/PrometheusShowcase';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import UserDashboard from './components/UserDashboard';
import TradingDashboard from './components/TradingDashboard';
import RiskEnginePanel from './components/RiskEnginePanel';
import AILearningDashboard from './components/AILearningDashboard';
import UserRegistration from './components/UserRegistration';
import Login from './components/Login';
import MainContent from './components/MainContent';
import Sidebar from './components/Sidebar';
import EnhancedInvestorDashboard from './components/EnhancedInvestorDashboard';
import InternalPaperTrading from './components/InternalPaperTrading';
import LiveMarketDashboard from './components/LiveMarketDashboard';
import UnifiedCockpitAdminDashboard from './components/UnifiedCockpitAdminDashboard';
import ErrorBoundary from './components/common/ErrorBoundary';
import { AppWithShortcuts } from './components/AppWithShortcuts';

import { TradingModeProvider } from './contexts/TradingModeContext';

// Centralized theme
import { theme } from './theme';

const isDev = process.env.NODE_ENV === 'development';


interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  tier?: string;
  token: string;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Initialize PWA manager
    console.log('🚀 Initializing Prometheus Trading PWA...');

    // Check for existing authentication and restore session
    const restoreSession = async () => {
      const token = localStorage.getItem('authToken');
      const userData = localStorage.getItem('userData');

      if (token && userData) {
        try {
          // Set token for API calls
          apiService.setToken(token);

          // Validate token with backend
          await apiService.getCurrentUser();

          // Parse stored user data
          const parsedUserData = JSON.parse(userData);

          // Update role detection for session restoration
          const isAdmin = parsedUserData.email.includes('admin') ||
                         parsedUserData.email.includes('prometheus-trader') ||
                         parsedUserData.email === 'admin@prometheus-trader.com@example.com';

          // Update user data with correct role
          const updatedUserData = {
            ...parsedUserData,
            role: isAdmin ? 'admin' : 'user'
          };

          // Restore authentication state
          setIsAuthenticated(true);
          setUser(updatedUserData);

          // Update localStorage with correct role
          localStorage.setItem('userData', JSON.stringify(updatedUserData));

          console.log('✅ Session restored successfully for user:', updatedUserData.email, 'with role:', updatedUserData.role);
        } catch (error) {
          console.log('❌ Session validation failed, clearing stored data');
          // Token invalid, clear storage
          localStorage.removeItem('authToken');
          localStorage.removeItem('userData');
          setIsAuthenticated(false);
          setUser(null);
        }
      } else {
        console.log('ℹ️ No existing session found');
      }
    };

    restoreSession();
  }, []);

  const handleLogin = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      // Use real backend API
      const response = await apiService.login({
        username: email, // Backend accepts username field
        password: password
      });

      // Get user info after successful login
      const userInfo = await apiService.getCurrentUser();

      // Determine role based on email or tier - Force admin for admin emails
      const isAdmin = userInfo.user.email.includes('admin') ||
                     userInfo.user.email.includes('prometheus-trader') ||


                     userInfo.user.tier === 'live_approved' ||
                     userInfo.user.email === 'admin@prometheus-trader.com@example.com';

      const userData = {
        id: userInfo.user.user_id,
        email: userInfo.user.email,
        name: userInfo.user.email.split('@')[0],
        role: isAdmin ? 'admin' : 'user',
        tier: userInfo.user.tier,
        token: response.access_token
      };

      console.log('🔍 Login - Determined role:', isAdmin ? 'admin' : 'user', 'for email:', userInfo.user.email);

      setIsAuthenticated(true);
      setUser(userData);
      localStorage.setItem('userData', JSON.stringify(userData));
      localStorage.setItem('authToken', response.access_token); // Store token for session persistence

      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Login failed. Please try again.'
      };
    }
  };

  const handleRegister = (userData: any) => {
    // For demo purposes, treat registration like login
    setIsAuthenticated(true);
    setUser(userData);
    localStorage.setItem('authToken', userData.token);
    localStorage.setItem('userData', JSON.stringify(userData));
  };

  const handleLogout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear state regardless of API call success
      setIsAuthenticated(false);
      setUser(null);
      // Force page reload to ensure clean state
      window.location.href = '/';
    }
  };

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SnackbarProvider maxSnack={4}>
          <TradingModeProvider user={user}>
            <BrowserRouter>
            <AppWithShortcuts>
            <Box component="main" id="main" sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)' }}>
              <Suspense fallback={<Box sx={{ p: 2 }}>Loading…</Box>}>
                <Routes>
            <Route
              path="/"
              element={
                isAuthenticated ? (
                  user?.role === 'admin' ? (
                    <Navigate to="/cockpit" replace />
                  ) : (
                    <Navigate to="/dashboard" replace />
                  )
                ) : (
                  <LandingPage />
                )
              }
            />
            <Route
              path="/register"
              element={
                isAuthenticated ? (
                  <Navigate to="/admin-dashboard" replace />
                ) : (
                  <UserRegistration onRegister={handleRegister} />
                )
              }
            />
            <Route
              path="/login"
              element={
                isAuthenticated ? (
                  <Navigate to="/admin-dashboard" replace />
                ) : (
                  <Login onLogin={handleLogin} />
                )
              }
            />
            {/* 📊 MAIN DASHBOARD - TIER-BASED ROUTING */}
            <Route
              path="/dashboard"
              element={
                isAuthenticated && user ? (
                  (() => {
                    console.log('🔍 Dashboard routing - User role:', user.role, 'User object:', user);
                    return user.role === 'admin' ? (
                      <Navigate to="/cockpit" replace />
                    ) : (
                      <UserDashboard
                        user={user}
                      />
                    );
                  })()
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="/admin-dashboard"
              element={
                isAuthenticated && user && user.role === 'admin' ? (
                  <UnifiedCockpitAdminDashboard user={{
                    id: user.id,
                    username: user.name,
                    email: user.email,
                    role: user.role || 'admin',
                    tier: 'admin'
                  }} onLogout={handleLogout} />
                ) : isAuthenticated && user ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="/ai-admin"
              element={
                isAuthenticated && user && user.role === 'admin' ? (
                  <UnifiedCockpitAdminDashboard user={{
                    id: user.id,
                    username: user.name,
                    email: user.email,
                    role: user.role || 'admin',
                    tier: 'admin'
                  }} onLogout={handleLogout} />
                ) : isAuthenticated && user ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            {/* 👑 ADMIN COCKPIT - PRIMARY ADMIN INTERFACE WITH ALL PHASE 1-4 FEATURES */}
            <Route
              path="/cockpit"
              element={
                isAuthenticated && user && user.role === 'admin' ? (
                  <UnifiedCockpitAdminDashboard user={{
                    id: user.id,
                    username: user.name,
                    email: user.email,
                    role: user.role || 'admin',
                    tier: 'admin'
                  }} onLogout={handleLogout} />
                ) : isAuthenticated && user ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            {/* 🔧 FORCE COCKPIT - Direct access for debugging (dev only) */}
            {isDev && (
              <Route
                path="/force-cockpit"
                element={
                  isAuthenticated && user ? (
                    <UnifiedCockpitAdminDashboard user={{
                      id: user.id,
                      username: user.name,
                      email: user.email,
                      role: 'admin', // Force admin role
                      tier: 'admin'
                    }} onLogout={handleLogout} />
                  ) : (
                    <Navigate to="/" replace />
                  )
                }
              />
            )}
            {isDev && (
              <Route
                path="/master-admin"
                element={
                  isAuthenticated ? (
                    <UnifiedCockpitAdminDashboard user={{
                      id: user?.id || '',
                      username: user?.name || '',
                      email: user?.email || '',
                      role: user?.role || 'user',
                      tier: (user?.tier === 'admin' || user?.tier === 'premium') ? user.tier : 'demo'
                    }} onLogout={handleLogout} />
                  ) : (
                    <Navigate to="/" replace />
                  )
                }
              />
            )}
            {/* 🎮 USER TRADING - PAPER TRADING WITH GAMIFICATION */}
            <Route
              path="/trading"
              element={
                isAuthenticated ? (
                  <TradingDashboard
                    mode="paper"
                    user={user}
                    showGamification={true}
                    enableSocialFeatures={true}
                  />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />

            {/* 💰 LIVE TRADING - ADMIN ONLY WITH FUND ALLOCATION */}
            <Route
              path="/live-trading"
              element={
                isAuthenticated && user && user.role === 'admin' ? (
                  <TradingDashboard
                    mode="live"
                    user={user}
                    requiresFundAllocation={true}
                    showRiskControls={true}
                  />
                ) : isAuthenticated ? (
                  <Navigate to="/trading" replace />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="/risk"
              element={
                isAuthenticated ? (
                  <RiskEnginePanel />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="/ai-learning"
              element={
                isAuthenticated ? (
                  <AILearningDashboard user={user} onLogout={handleLogout} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            {isDev && (
              <Route
                path="/admin"
                element={
                  isAuthenticated && user?.role === 'admin' ? (
                    <UnifiedCockpitAdminDashboard user={{
                      id: user.id,
                      username: user.name,
                      email: user.email,
                      role: user.role,
                      tier: (user.tier === 'admin' || user.tier === 'premium') ? user.tier : 'admin'
                    }} onLogout={handleLogout} />
                  ) : (
                    <Navigate to="/" replace />
                  )
                }
              />
            )}
            <Route
              path="/investor"
              element={
                isAuthenticated ? (
                  <EnhancedInvestorDashboard userId={user?.id || 'demo-user'} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="/paper-trading"
              element={
                isAuthenticated ? (
                  <InternalPaperTrading />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="/live-market"
              element={
                isAuthenticated ? (
                  <LiveMarketDashboard />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            </Routes>
              </Suspense>
            </Box>
            </AppWithShortcuts>
            </BrowserRouter>
          </TradingModeProvider>
        </SnackbarProvider>
      </ThemeProvider>
      <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
