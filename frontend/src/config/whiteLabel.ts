/**
 * White-Label Configuration
 * Customizable branding and theme settings
 */

export interface WhiteLabelConfig {
  branding: {
    companyName: string;
    logo: string;
    logoLight?: string;
    favicon: string;
    tagline?: string;
  };
  theme: {
    primaryColor: string;
    secondaryColor: string;
    accentColor?: string;
    backgroundColor?: string;
    textColor?: string;
  };
  features: {
    socialFeatures: boolean;
    aiAssistant: boolean;
    gamification: boolean;
    leaderboard: boolean;
    notifications: boolean;
    darkMode: boolean;
  };
  contact: {
    email?: string;
    phone?: string;
    website?: string;
    supportUrl?: string;
  };
  legal: {
    termsUrl?: string;
    privacyUrl?: string;
    disclaimerUrl?: string;
  };
  customization: {
    customCSS?: string;
    customJS?: string;
    headerHTML?: string;
    footerHTML?: string;
  };
}

// Default PROMETHEUS configuration
export const defaultConfig: WhiteLabelConfig = {
  branding: {
    companyName: 'PROMETHEUS',
    logo: '/assets/prometheus-logo.png',
    logoLight: '/assets/prometheus-logo-light.png',
    favicon: '/assets/favicon.ico',
    tagline: 'Advanced AI Trading Platform'
  },
  theme: {
    primaryColor: '#00d4ff',
    secondaryColor: '#ff6b35',
    accentColor: '#ffd700',
    backgroundColor: '#0a0a0a',
    textColor: '#ffffff'
  },
  features: {
    socialFeatures: true,
    aiAssistant: true,
    gamification: true,
    leaderboard: true,
    notifications: true,
    darkMode: true
  },
  contact: {
    email: 'support@prometheus-trade.com',
    website: 'https://prometheus-trade.com',
    supportUrl: 'https://prometheus-trade.com/support'
  },
  legal: {
    termsUrl: '/legal/terms',
    privacyUrl: '/legal/privacy',
    disclaimerUrl: '/legal/disclaimer'
  },
  customization: {}
};

// Load white-label configuration from environment or API
export const loadWhiteLabelConfig = async (): Promise<WhiteLabelConfig> => {
  try {
    // Try to load from API first
    const response = await fetch('/api/white-label/config');
    if (response.ok) {
      const config = await response.json();
      return { ...defaultConfig, ...config };
    }
  } catch (error) {
    console.warn('Failed to load white-label config from API, using default');
  }

  // Try to load from environment variables
  const envConfig: Partial<WhiteLabelConfig> = {};

  if (process.env.REACT_APP_COMPANY_NAME) {
    envConfig.branding = {
      ...defaultConfig.branding,
      companyName: process.env.REACT_APP_COMPANY_NAME,
      logo: process.env.REACT_APP_LOGO || defaultConfig.branding.logo,
      favicon: process.env.REACT_APP_FAVICON || defaultConfig.branding.favicon,
      tagline: process.env.REACT_APP_TAGLINE
    };
  }

  if (process.env.REACT_APP_PRIMARY_COLOR) {
    envConfig.theme = {
      ...defaultConfig.theme,
      primaryColor: process.env.REACT_APP_PRIMARY_COLOR,
      secondaryColor: process.env.REACT_APP_SECONDARY_COLOR || defaultConfig.theme.secondaryColor
    };
  }

  return { ...defaultConfig, ...envConfig };
};

// Apply white-label configuration to document
export const applyWhiteLabelConfig = (config: WhiteLabelConfig) => {
  // Update document title
  document.title = config.branding.companyName;

  // Update favicon
  const favicon = document.querySelector('link[rel="icon"]') as HTMLLinkElement;
  if (favicon) {
    favicon.href = config.branding.favicon;
  }

  // Apply custom CSS
  if (config.customization.customCSS) {
    const style = document.createElement('style');
    style.textContent = config.customization.customCSS;
    document.head.appendChild(style);
  }

  // Apply custom JS
  if (config.customization.customJS) {
    const script = document.createElement('script');
    script.textContent = config.customization.customJS;
    document.body.appendChild(script);
  }

  // Apply CSS variables for theme
  document.documentElement.style.setProperty('--primary-color', config.theme.primaryColor);
  document.documentElement.style.setProperty('--secondary-color', config.theme.secondaryColor);
  if (config.theme.accentColor) {
    document.documentElement.style.setProperty('--accent-color', config.theme.accentColor);
  }
  if (config.theme.backgroundColor) {
    document.documentElement.style.setProperty('--background-color', config.theme.backgroundColor);
  }
  if (config.theme.textColor) {
    document.documentElement.style.setProperty('--text-color', config.theme.textColor);
  }
};

// Hook to use white-label configuration
import { useState, useEffect } from 'react';

export const useWhiteLabelConfig = () => {
  const [config, setConfig] = useState<WhiteLabelConfig>(defaultConfig);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadWhiteLabelConfig().then((loadedConfig) => {
      setConfig(loadedConfig);
      applyWhiteLabelConfig(loadedConfig);
      setIsLoading(false);
    });
  }, []);

  return { config, isLoading };
};

export default {
  defaultConfig,
  loadWhiteLabelConfig,
  applyWhiteLabelConfig,
  useWhiteLabelConfig
};

