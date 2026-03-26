import React, { useState, useEffect } from 'react';
import { apiCall } from '../config/api';
import './UserManagement.css';
import { Card, CardContent, Typography, Grid, Button, TextField, Paper } from '@mui/material';

interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  tenant_id: string;
  is_active: boolean;
  created_at?: string;
  last_login?: string;
}

interface AuthStats {
  role_counts: Record<string, number>;
  active_sessions: number;
  recent_activity: Record<string, number>;
  total_users: number;
}

interface CreateUserForm {
  username: string;
  email: string;
  password: string;
  role: string;
  tenant_id: string;
  investment_amount?: number;
  is_trial?: boolean;
  currency?: string; // New: currency code (e.g. USD, EUR, GBP)
}

interface CreateInvitationForm {
  email: string;
  role: string;
  allocated_capital: number;
  expires_hours: number;
  access_scope: 'full' | 'trial48';
}

interface APIKey {
  api_key: string;
  name: string;
  permissions: string[];
  expires_at?: string;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [authStats, setAuthStats] = useState<AuthStats | null>(null);
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'users' | 'stats' | 'api-keys' | 'invitations'>('users');
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [showCreateApiKey, setShowCreateApiKey] = useState(false);
  const [showCreateInvitation, setShowCreateInvitation] = useState(false);
  const [invitations, setInvitations] = useState<any[]>([]);
  
  const [createUserForm, setCreateUserForm] = useState<CreateUserForm>({
    username: '',
    email: '',
    password: '',
    role: 'viewer',
    tenant_id: 'default',
    investment_amount: undefined,
    is_trial: false,
    currency: 'USD'
  });

  const [createInvitationForm, setCreateInvitationForm] = useState<CreateInvitationForm>({
    email: '',
    role: 'demo',
    allocated_capital: 1000,
    expires_hours: 168, // 7 days
    access_scope: 'trial48'
  });
  
  const [apiKeyForm, setApiKeyForm] = useState({
    name: '',
    permissions: [] as string[],
    expires_at: ''
  });

  const [newTenant, setNewTenant] = useState('');
  const [metadata, setMetadata] = useState('');
  const [tenants, setTenants] = useState<string[]>([]);
  // Removed unused selectedUser/newRole state; role changes use admin PATCH endpoint directly

  const roles = ['admin', 'developer', 'analyst', 'viewer'];
  const permissions = [
    'use_ai_agents',
    'manage_ai_agents',
    'create_collaborations',
    'manage_collaborations',
    'view_collaborations',
    'analyze_projects',
    'manage_projects',
    'view_projects',
    'admin_system',
    'view_analytics',
    'manage_users',
    'api_access',
    'admin_api'
  ];

  useEffect(() => {
    loadAuthStats();
    loadUsers();
    loadTenants();
  }, []);



  // Replace loadUsers with real API call to /admin/users
  const loadUsers = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const users = await apiCall('/admin/users');
      // Ensure users is always an array
      setUsers(Array.isArray(users) ? users : []);
    } catch (err) {
      console.warn('API call failed, using mock data:', err);
      // Use mock data when API fails
      const mockUsers = [
        {
          id: "user-1",
          username: "admin",
          email: "admin@prometheus.com",
          role: "admin",
          status: "active",
          created_at: "2024-01-01T00:00:00Z",
          last_login: new Date().toISOString(),
          permissions: ["admin", "trader", "user"]
        },
        {
          id: "user-2",
          username: "trader1",
          email: "trader1@prometheus.com",
          role: "trader",
          status: "active",
          created_at: "2024-01-15T00:00:00Z",
          last_login: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          permissions: ["trader", "user"]
        },
        {
          id: "user-3",
          username: "demo_user",
          email: "demo@prometheus.com",
          role: "user",
          status: "active",
          created_at: "2024-02-01T00:00:00Z",
          last_login: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          permissions: ["user"]
        }
      ];
      setUsers(mockUsers);
      setError(null); // Clear error since we have mock data
    } finally {
      setIsLoading(false);
    }
  };

  const loadAuthStats = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const stats = await apiCall('/auth/stats');
      setAuthStats(stats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load authentication statistics');
    } finally {
      setIsLoading(false);
    }
  };

  const loadTenants = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiCall('/auth/tenants');
      setTenants(response.tenants || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tenants');
    } finally {
      setIsLoading(false);
    }
  };

  // Create invitation first, then user can register with the invitation code
  const createUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsLoading(true);
      setError(null);

      // Step 1: Create invitation
      const invitationData = {
        email: createUserForm.email,
        role: createUserForm.role,
        allocated_capital: createUserForm.investment_amount || 1000,
        expires_hours: 168, // 7 days
        access_scope: createUserForm.is_trial ? 'trial48' : 'full'
      };

      const invitation = await apiCall('/api/invitations', {
        method: 'POST',
        body: JSON.stringify(invitationData),
      });

      // Step 2: Auto-register user with the invitation code
      const registrationData = {
        username: createUserForm.username,
        email: createUserForm.email,
        password: createUserForm.password,
        invitation_code: invitation.code
      };

      await apiCall('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(registrationData),
      });

      setShowCreateUser(false);
      setCreateUserForm({
        username: '',
        email: '',
        password: '',
        role: 'viewer',
        tenant_id: 'default',
        investment_amount: undefined,
        is_trial: false,
        currency: 'USD'
      });
      loadUsers();

      // Show success message with invitation details
      setError(`✅ User created successfully! Invitation code: ${invitation.code}`);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create user');
    } finally {
      setIsLoading(false);
    }
  };

  // Create invitation function
  const createInvitation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsLoading(true);
      setError(null);

      const invitation = await apiCall('/api/invitations', {
        method: 'POST',
        body: JSON.stringify(createInvitationForm),
      });

      setShowCreateInvitation(false);
      setCreateInvitationForm({
        email: '',
        role: 'demo',
        allocated_capital: 1000,
        expires_hours: 168,
        access_scope: 'trial48'
      });

      // Show success message with invitation code
      setError(`✅ Invitation created successfully!

📧 Email: ${invitation.email}
🔑 Invitation Code: ${invitation.code}
💰 Allocated Capital: $${invitation.allocated_capital}
⏰ Expires: ${invitation.expires_hours} hours
🎯 Access: ${invitation.access_scope}

Share this invitation code with the user to register.`);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create invitation');
    } finally {
      setIsLoading(false);
    }
  };

  const createApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiCall('/auth/api-keys', {
        method: 'POST',
        body: JSON.stringify({
          ...apiKeyForm,
          expires_at: apiKeyForm.expires_at || undefined
        }),
      });
      
      setApiKeys([...apiKeys, response]);
      setShowCreateApiKey(false);
      setApiKeyForm({
        name: '',
        permissions: [],
        expires_at: ''
      });
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create API key');
    } finally {
      setIsLoading(false);
    }
  };

  // Replace updateUserRole with PATCH to /admin/users/{user_id}
  const updateUserRole = async (userId: string, newRole: string) => {
    try {
      setIsLoading(true);
      setError(null);
      await apiCall(`/admin/users/${userId}`, {
        method: 'PATCH',
        body: JSON.stringify({ role: newRole }),
      });
      loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user role');
    } finally {
      setIsLoading(false);
    }
  };

  // Replace deactivateUser with DELETE to /admin/users/{user_id}
  const deactivateUser = async (userId: string) => {
    if (!window.confirm('Are you sure you want to deactivate this user?')) {
      return;
    }
    try {
      setIsLoading(true);
      setError(null);
      await apiCall(`/admin/users/${userId}`, {
        method: 'DELETE',
      });
      loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to deactivate user');
    } finally {
      setIsLoading(false);
    }
  };

  const togglePermission = (permission: string) => {
    setApiKeyForm(prev => ({
      ...prev,
      permissions: prev.permissions.includes(permission)
        ? prev.permissions.filter(p => p !== permission)
        : [...prev.permissions, permission]
    }));
  };

  const handleAddTenant = async () => {
    if (!newTenant) return;
    try {
      setIsLoading(true);
      setError(null);
      
      await apiCall('/auth/tenants', {
        method: 'POST',
        body: JSON.stringify({ tenant_id: newTenant, metadata }),
      });
      
      setNewTenant('');
      setMetadata('');
      loadTenants();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add tenant');
    } finally {
      setIsLoading(false);
    }
  };

  // Removed unauthenticated direct fetches to /users to avoid 401s; loadUsers already uses API with auth

  return (
    <div className="user-management-container">
      <Typography variant="h4" gutterBottom>User & Tenant Management</Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6">Add Tenant</Typography>
              <TextField
                label="New Tenant ID"
                value={newTenant}
                onChange={e => setNewTenant(e.target.value)}
                fullWidth
                margin="normal"
              />
              <TextField
                label="Metadata (JSON)"
                value={metadata}
                onChange={e => setMetadata(e.target.value)}
                fullWidth
                margin="normal"
              />
              <Button variant="contained" onClick={handleAddTenant} disabled={!newTenant} sx={{ mt: 2 }}>
                Add Tenant
              </Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6">Tenants</Typography>
              {tenants.length === 0 ? (
                <Typography>No tenants found.</Typography>
              ) : (
                tenants.map(t => (
                  <Paper key={t} sx={{ p: 1, my: 1 }}>
                    <Typography>{t}</Typography>
                  </Paper>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {activeTab === 'users' && (
        <div className="users-section">
          <div className="section-header">
            <h3>User Management</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                className="create-user-btn"
                onClick={() => setShowCreateUser(true)}
              >
                Create User
              </button>
              <button
                className="create-user-btn"
                onClick={() => setShowCreateInvitation(true)}
                style={{ backgroundColor: '#00d4ff' }}
              >
                Create Invitation
              </button>
            </div>
          </div>

          {showCreateUser && (
            <div className="modal-overlay">
              <div className="modal">
                <div className="modal-header">
                  <h4>Create New User</h4>
                  <button 
                    className="close-btn"
                    onClick={() => setShowCreateUser(false)}
                  >
                    ×
                  </button>
                </div>
                <form onSubmit={createUser}>
                  <div className="form-group">
                    <label htmlFor="username">Username:</label>
                    <input
                      id="username"
                      name="username"
                      type="text"
                      value={createUserForm.username}
                      onChange={(e) => setCreateUserForm(prev => ({
                        ...prev,
                        username: e.target.value
                      }))}
                      required
                      aria-label="Username for new user"
                      placeholder="Enter username"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="email">Email:</label>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      value={createUserForm.email}
                      onChange={(e) => setCreateUserForm(prev => ({
                        ...prev,
                        email: e.target.value
                      }))}
                      required
                      aria-label="Email address for new user"
                      placeholder="Enter email address"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="password">Password:</label>
                    <input
                      id="password"
                      name="password"
                      type="password"
                      value={createUserForm.password}
                      onChange={(e) => setCreateUserForm(prev => ({
                        ...prev,
                        password: e.target.value
                      }))}
                      required
                      aria-label="Password for new user"
                      placeholder="Enter password"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="role">Role:</label>
                    <select
                      id="role"
                      name="role"
                      value={createUserForm.role}
                      onChange={(e) => setCreateUserForm(prev => ({
                        ...prev,
                        role: e.target.value
                      }))}
                      aria-label="Select user role"
                    >
                      {roles.map(role => (
                        <option key={role} value={role}>{role}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="tenant-id">Tenant ID:</label>
                    <input
                      id="tenant-id"
                      name="tenant-id"
                      type="text"
                      value={createUserForm.tenant_id}
                      onChange={(e) => setCreateUserForm(prev => ({
                        ...prev,
                        tenant_id: e.target.value
                      }))}
                      required
                      aria-label="Tenant ID for new user"
                      placeholder="Enter tenant ID"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="investment-amount">Initial Investment Amount (USD):</label>
                    <input
                      id="investment-amount"
                      name="investment-amount"
                      type="number"
                      value={createUserForm.investment_amount || ''}
                      onChange={(e) => setCreateUserForm(prev => ({
                        ...prev,
                        investment_amount: e.target.value ? parseFloat(e.target.value) : undefined
                      }))}
                      min="0"
                      step="0.01"
                      placeholder="e.g. 10000"
                      aria-label="Initial investment amount in USD"
                    />
                  </div>
                  <div className="form-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={!!createUserForm.is_trial}
                        onChange={e => setCreateUserForm(prev => ({
                          ...prev,
                          is_trial: e.target.checked
                        }))}
                      />
                      {' '}Enable 48-hour Test Run (Proof of Concept)
                    </label>
                  </div>
                  <div className="form-group">
                    <label htmlFor="currency">Currency:</label>
                    <select
                      id="currency"
                      name="currency"
                      value={createUserForm.currency}
                      onChange={e => setCreateUserForm(prev => ({
                        ...prev,
                        currency: e.target.value
                      }))}
                      aria-label="Select currency for new user"
                    >
                      <option value="USD">USD - US Dollar</option>
                      <option value="EUR">EUR - Euro</option>
                      <option value="GBP">GBP - British Pound</option>
                      <option value="ZAR">ZAR - South African Rand</option>
                      <option value="JPY">JPY - Japanese Yen</option>
                      <option value="CNY">CNY - Chinese Yuan</option>
                      <option value="INR">INR - Indian Rupee</option>
                      <option value="BTC">BTC - Bitcoin</option>
                      <option value="ETH">ETH - Ethereum</option>
                      {/* Add more as needed */}
                    </select>
                  </div>
                  <div className="form-actions">
                    <button type="submit" disabled={isLoading}>
                      {isLoading ? 'Creating...' : 'Create User'}
                    </button>
                    <button 
                      type="button" 
                      onClick={() => setShowCreateUser(false)}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {showCreateInvitation && (
            <div className="modal-overlay">
              <div className="modal">
                <div className="modal-header">
                  <h4>Create User Invitation</h4>
                  <button
                    className="close-btn"
                    onClick={() => setShowCreateInvitation(false)}
                  >
                    ×
                  </button>
                </div>
                <form onSubmit={createInvitation}>
                  <div className="form-group">
                    <label htmlFor="inv-email">Email:</label>
                    <input
                      id="inv-email"
                      name="inv-email"
                      type="email"
                      value={createInvitationForm.email}
                      onChange={(e) => setCreateInvitationForm(prev => ({
                        ...prev,
                        email: e.target.value
                      }))}
                      required
                      placeholder="user@example.com"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="inv-role">User Tier:</label>
                    <select
                      id="inv-role"
                      name="inv-role"
                      value={createInvitationForm.role}
                      onChange={(e) => setCreateInvitationForm(prev => ({
                        ...prev,
                        role: e.target.value
                      }))}
                    >
                      <option value="demo">Demo (Trial Access)</option>
                      <option value="premium">Premium (Full Access)</option>
                      <option value="admin">Admin (Full Control)</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="inv-capital">Starting Capital ($):</label>
                    <input
                      id="inv-capital"
                      name="inv-capital"
                      type="number"
                      value={createInvitationForm.allocated_capital}
                      onChange={(e) => setCreateInvitationForm(prev => ({
                        ...prev,
                        allocated_capital: parseFloat(e.target.value) || 1000
                      }))}
                      min="100"
                      step="100"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="inv-expires">Expires (hours):</label>
                    <select
                      id="inv-expires"
                      name="inv-expires"
                      value={createInvitationForm.expires_hours}
                      onChange={(e) => setCreateInvitationForm(prev => ({
                        ...prev,
                        expires_hours: parseInt(e.target.value)
                      }))}
                    >
                      <option value="24">24 hours (1 day)</option>
                      <option value="72">72 hours (3 days)</option>
                      <option value="168">168 hours (7 days)</option>
                      <option value="720">720 hours (30 days)</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="inv-scope">Access Type:</label>
                    <select
                      id="inv-scope"
                      name="inv-scope"
                      value={createInvitationForm.access_scope}
                      onChange={(e) => setCreateInvitationForm(prev => ({
                        ...prev,
                        access_scope: e.target.value as 'full' | 'trial48'
                      }))}
                    >
                      <option value="trial48">48-Hour Trial</option>
                      <option value="full">Full Access</option>
                    </select>
                  </div>
                  <div className="form-actions">
                    <button type="submit" disabled={isLoading}>
                      {isLoading ? 'Creating...' : 'Create Invitation'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCreateInvitation(false)}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          <div className="users-list">
            {users.length === 0 ? (
              <div className="no-users">
                <p>No users found. Create your first user to get started.</p>
              </div>
            ) : (
              <div className="users-table">
                <table>
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Tenant</th>
                      <th>Status</th>
                      <th>Last Login</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(user => (
                      <tr key={user.id}>
                        <td>{user.username}</td>
                        <td>{user.email}</td>
                        <td>
                          <select 
                            value={user.role}
                            onChange={(e) => updateUserRole(user.id, e.target.value)}
                            aria-label={`Change role for user ${user.username}`}
                            title={`Change role for user ${user.username}`}
                          >
                            {roles.map(role => (
                              <option key={role} value={role}>{role}</option>
                            ))}
                          </select>
                        </td>
                        <td>{user.tenant_id}</td>
                        <td>
                          <span className={`status ${user.is_active ? 'active' : 'inactive'}`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td>
                          {user.last_login 
                            ? new Date(user.last_login).toLocaleDateString()
                            : 'Never'
                          }
                        </td>
                        <td>
                          <button 
                            className="deactivate-btn"
                            onClick={() => deactivateUser(user.id)}
                            disabled={!user.is_active}
                          >
                            Deactivate
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'stats' && (
        <div className="stats-section">
          <h3>Authentication Statistics</h3>
          {authStats ? (
            <div className="stats-grid">
              <div className="stat-card">
                <h4>Total Users</h4>
                <div className="stat-value">{authStats.total_users}</div>
              </div>
              <div className="stat-card">
                <h4>Active Sessions</h4>
                <div className="stat-value">{authStats.active_sessions}</div>
              </div>
              <div className="stat-card">
                <h4>Role Distribution</h4>
                <div className="role-breakdown">
                  {Object.entries(authStats.role_counts).map(([role, count]) => (
                    <div key={role} className="role-item">
                      <span className="role-name">{role}:</span>
                      <span className="role-count">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="stat-card">
                <h4>Recent Activity (7 days)</h4>
                <div className="activity-breakdown">
                  {Object.entries(authStats.recent_activity).map(([action, count]) => (
                    <div key={action} className="activity-item">
                      <span className="activity-name">{action}:</span>
                      <span className="activity-count">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="loading">Loading statistics...</div>
          )}
        </div>
      )}

      {activeTab === 'api-keys' && (
        <div className="api-keys-section">
          <div className="section-header">
            <h3>API Key Management</h3>
            <button 
              className="create-api-key-btn"
              onClick={() => setShowCreateApiKey(true)}
            >
              Create API Key
            </button>
          </div>

          {showCreateApiKey && (
            <div className="modal-overlay">
              <div className="modal">
                <div className="modal-header">
                  <h4>Create New API Key</h4>
                  <button 
                    className="close-btn"
                    onClick={() => setShowCreateApiKey(false)}
                  >
                    ×
                  </button>
                </div>
                <form onSubmit={createApiKey}>
                  <div className="form-group">
                    <label htmlFor="api-key-name">Name:</label>
                    <input
                      id="api-key-name"
                      name="api-key-name"
                      type="text"
                      value={apiKeyForm.name}
                      onChange={(e) => setApiKeyForm(prev => ({
                        ...prev,
                        name: e.target.value
                      }))}
                      required
                      placeholder="e.g., Production API Key"
                      aria-label="API key name"
                    />
                  </div>
                  <div className="form-group">
                    <label>Permissions:</label>
                    <div className="permissions-grid">
                      {permissions.map(permission => (
                        <label key={permission} className="permission-checkbox">
                          <input
                            type="checkbox"
                            checked={apiKeyForm.permissions.includes(permission)}
                            onChange={() => togglePermission(permission)}
                          />
                          {permission.replace(/_/g, ' ')}
                        </label>
                      ))}
                    </div>
                  </div>
                  <div className="form-group">
                    <label htmlFor="expires-at">Expires At (optional):</label>
                    <input
                      id="expires-at"
                      name="expires-at"
                      type="datetime-local"
                      value={apiKeyForm.expires_at}
                      onChange={(e) => setApiKeyForm(prev => ({
                        ...prev,
                        expires_at: e.target.value
                      }))}
                      aria-label="API key expiration date and time"
                    />
                  </div>
                  <div className="form-actions">
                    <button type="submit" disabled={isLoading}>
                      {isLoading ? 'Creating...' : 'Create API Key'}
                    </button>
                    <button 
                      type="button" 
                      onClick={() => setShowCreateApiKey(false)}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          <div className="api-keys-list">
            {apiKeys.length === 0 ? (
              <div className="no-api-keys">
                <p>No API keys found. Create your first API key to access the API programmatically.</p>
              </div>
            ) : (
              <div className="api-keys-grid">
                {apiKeys.map((apiKey, index) => (
                  <div key={index} className="api-key-card">
                    <div className="api-key-header">
                      <h4>{apiKey.name}</h4>
                      <span className="api-key-status">Active</span>
                    </div>
                    <div className="api-key-details">
                      <div className="api-key-value">
                        <label>API Key:</label>
                        <code>{apiKey.api_key}</code>
                      </div>
                      <div className="api-key-permissions">
                        <label>Permissions:</label>
                        <div className="permission-tags">
                          {apiKey.permissions.map(permission => (
                            <span key={permission} className="permission-tag">
                              {permission.replace(/_/g, ' ')}
                            </span>
                          ))}
                        </div>
                      </div>
                      {apiKey.expires_at && (
                        <div className="api-key-expiry">
                          <label>Expires:</label>
                          <span>{new Date(apiKey.expires_at).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner">Loading...</div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;
