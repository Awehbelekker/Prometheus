import React, { useState } from 'react';
import AuthContainer from './components/AuthContainer';
import './RegistrationDemo.css';

interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  firstName: string;
  lastName: string;
}

const RegistrationDemo: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  const handleLogin = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      // Demo authentication logic
      const demoUsers = {
        'admin@prometheus.com': { role: 'admin', firstName: 'Admin', lastName: 'User', password: 'admin123!' },
        'trader@prometheus.com': { role: 'trader', firstName: 'Trader', lastName: 'User', password: 'trader123!' },
        'viewer@prometheus.com': { role: 'viewer', firstName: 'Viewer', lastName: 'User', password: 'viewer123!' }
      };

      const user = demoUsers[email as keyof typeof demoUsers];

      if (!user || user.password !== password) {
        return { success: false, error: 'Invalid email or password' };
      }

      const userData: User = {
        id: email,
        username: email.split('@')[0],
        email: email,
        role: user.role,
        firstName: user.firstName,
        lastName: user.lastName
      };

      const token = 'demo-token-' + Date.now();

      setAuthToken(token);
      setCurrentUser(userData);
      setIsAuthenticated(true);
      console.log('User logged in:', userData);

      return { success: true };
    } catch (error) {
      return { success: false, error: 'Login failed. Please try again.' };
    }
  };

  const handleLogout = () => {
    setAuthToken(null);
    setCurrentUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  };

  if (isAuthenticated && currentUser) {
    return (
      <div className="demo-dashboard">
        <div className="dashboard-container">
          <div className="dashboard-header">
            <h1>Welcome to MASS Framework</h1>
            <button 
              className="logout-button"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
          
          <div className="user-info-card">
            <h2>User Information</h2>
            <div className="user-details">
              <div className="detail-item">
                <label>Name:</label>
                <span>{currentUser.firstName} {currentUser.lastName}</span>
              </div>
              <div className="detail-item">
                <label>Username:</label>
                <span>{currentUser.username}</span>
              </div>
              <div className="detail-item">
                <label>Email:</label>
                <span>{currentUser.email}</span>
              </div>
              <div className="detail-item">
                <label>Role:</label>
                <span className={`role-badge ${currentUser.role}`}>
                  {currentUser.role}
                </span>
              </div>
              <div className="detail-item">
                <label>User ID:</label>
                <span>{currentUser.id}</span>
              </div>
            </div>
          </div>

          <div className="features-demo">
            <h2>Available Features</h2>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">🤖</div>
                <h3>AI Agents</h3>
                <p>Access to intelligent development agents for automated coding and project management.</p>
                <button className="feature-button">Explore Agents</button>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">🚀</div>
                <h3>Project Builder</h3>
                <p>Visual project builder with drag-and-drop components and real-time collaboration.</p>
                <button className="feature-button">Start Building</button>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">☁️</div>
                <h3>Cloud Deployment</h3>
                <p>One-click deployment to major cloud providers with automatic scaling and monitoring.</p>
                <button className="feature-button">Deploy Projects</button>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">📊</div>
                <h3>Analytics Dashboard</h3>
                <p>Comprehensive analytics and insights for your projects and team performance.</p>
                <button className="feature-button">View Analytics</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return <AuthContainer onLogin={handleLogin} />;
};

export default RegistrationDemo;
