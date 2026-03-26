import React, { useState } from 'react';
import Login from './Login';
import UserRegistration from './UserRegistration';
import './AuthContainer.css';

interface AuthContainerProps {
  onLogin: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
}

type AuthMode = 'login' | 'register';

const AuthContainer: React.FC<AuthContainerProps> = ({ onLogin }) => {
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [isTransitioning, setIsTransitioning] = useState(false);

  const handleModeSwitch = (newMode: AuthMode) => {
    if (newMode === authMode || isTransitioning) return;
    
    setIsTransitioning(true);
    setTimeout(() => {
      setAuthMode(newMode);
      setIsTransitioning(false);
    }, 300);
  };

  const handleRegistrationSuccess = (userData: any) => {
    // Handle successful registration - for now just switch to login
    handleModeSwitch('login');
  };

  const handleSwitchToLogin = () => {
    handleModeSwitch('login');
  };

  const handleSwitchToRegister = () => {
    handleModeSwitch('register');
  };

  return (
    <div className="auth-container">
      <div className={`auth-wrapper ${isTransitioning ? 'transitioning' : ''}`}>
        {authMode === 'login' ? (
          <div className="auth-component">
            <Login 
              onLogin={onLogin}
            />
            <div className="auth-switch">
              <p>Don't have an account? 
                <button 
                  type="button" 
                  className="switch-link"
                  onClick={handleSwitchToRegister}
                  disabled={isTransitioning}
                >
                  Create account
                </button>
              </p>
            </div>
          </div>        ) : (
          <div className="auth-component">
            <UserRegistration
              onRegister={handleRegistrationSuccess}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default AuthContainer;
