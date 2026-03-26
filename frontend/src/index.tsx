import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { FeatureFlagsProvider, UserProvider } from './context/UserContext';

// Initialize PWA and service worker
import './utils/pwa';

// PROMETHEUS Trading Platform v2.3.0 - Build 20251018-1130
console.log('🚀 PROMETHEUS Trading Platform v2.3.0 - Phase 4 Complete');
console.log('📊 Build: 20251018-1130');
console.log('🧠 AI Agents: 20 Active (3 Supervisors + 17 Execution)');
console.log('📈 Learning System: Enabled');
console.log('✨ Phase 4 Enhancements: All 7 Features Active');

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <FeatureFlagsProvider>
      <UserProvider>
        <App />
      </UserProvider>
    </FeatureFlagsProvider>
  </React.StrictMode>
);

// Register service worker for PWA functionality
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('✅ SW registered successfully:', registration);
      })
      .catch((registrationError) => {
        console.log('❌ SW registration failed:', registrationError);
      });
  });
}
