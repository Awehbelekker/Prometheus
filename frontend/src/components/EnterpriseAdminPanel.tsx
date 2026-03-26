
import React from 'react';
import { Box, Typography, Paper, Tabs, Tab } from '@mui/material';
import UserManagement from './UserManagement';

const tabLabels = [
  'User Management',
  'Roles & Permissions',
  'System Config',
  'Audit Logs',
  'User Audit Trail',
  'API Key Management',
  'Security Controls',
  'Data Export/Import',
  'Notification Center',
  'Custom Branding',
  'License Management',
  'Advanced Audit Log Search',
];

const EnterpriseAdminPanel: React.FC = () => {
  const [tab, setTab] = React.useState(0);

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" sx={{ mb: 2, color: '#00d4ff', fontWeight: 700 }}>
        ⚙️ Enterprise Admin Panel
      </Typography>
      <Paper sx={{ mb: 2 }}>
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {tabLabels.map(label => (
            <Tab key={label} label={label} />
          ))}
        </Tabs>
      </Paper>
      {tab === 0 && <UserManagement />}
      {tab === 1 && (
        <Box>
          <Typography variant="h6">Role & Permission Editor</Typography>
          <Typography>Assign roles and permissions to users. (Mock table below)</Typography>
          <table style={{width:'100%',marginTop:8}}><thead><tr><th>User</th><th>Role</th><th>Permissions</th></tr></thead><tbody><tr><td>Alice</td><td>Admin</td><td>All</td></tr><tr><td>Bob</td><td>Analyst</td><td>Read, Export</td></tr></tbody></table>
        </Box>
      )}
      {tab === 2 && (
        <Box>
          <Typography variant="h6">System Settings Editor</Typography>
          <Typography>Update system-wide settings. (Mock form below)</Typography>
          <form style={{marginTop:8}}><label>Maintenance Mode: <input type="checkbox" /></label><br/><label>API Endpoint: <input type="text" value="https://api.example.com" readOnly /></label></form>
        </Box>
      )}
      {tab === 3 && (
        <Box>
          <Typography variant="h6">Audit Log Viewer</Typography>
          <Typography>Recent admin actions. (Mock log below)</Typography>
          <ul><li>2025-08-29: Alice updated system settings</li><li>2025-08-28: Bob created new user</li></ul>
        </Box>
      )}
      {tab === 4 && (
        <Box>
          <Typography variant="h6">User Audit Trail</Typography>
          <Typography>Track all user actions. (Mock table below)</Typography>
          <table style={{width:'100%',marginTop:8}}><thead><tr><th>User</th><th>Action</th><th>Date</th></tr></thead><tbody><tr><td>Alice</td><td>Login</td><td>2025-08-29</td></tr><tr><td>Bob</td><td>Export Data</td><td>2025-08-28</td></tr></tbody></table>
        </Box>
      )}
      {tab === 5 && (
        <Box>
          <Typography variant="h6">API Key Management</Typography>
          <Typography>Manage API keys for integrations. (Mock list below)</Typography>
          <ul><li>Key: abcd-1234-efgh-5678 <button>Revoke</button></li><li>Key: wxyz-9876-ijkl-5432 <button>Revoke</button></li></ul>
        </Box>
      )}
      {tab === 6 && (
        <Box>
          <Typography variant="h6">Security Controls</Typography>
          <Typography>Enforce security policies. (Mock controls below)</Typography>
          <button>Force Logout All Users</button> <button>Enforce 2FA</button>
        </Box>
      )}
      {tab === 7 && (
        <Box>
          <Typography variant="h6">Data Export/Import</Typography>
          <Typography>Export or import user/activity data. (Mock controls below)</Typography>
          <button>Export Users (CSV)</button> <button>Import Users</button>
        </Box>
      )}
      {tab === 8 && (
        <Box>
          <Typography variant="h6">Notification Center</Typography>
          <Typography>Configure system-wide alerts. (Mock form below)</Typography>
          <form style={{marginTop:8}}><label>Email Alerts: <input type="checkbox" defaultChecked /></label><br/><label>Admin Notifications: <input type="checkbox" /></label></form>
        </Box>
      )}
      {tab === 9 && (
        <Box>
          <Typography variant="h6">Custom Branding</Typography>
          <Typography>Manage platform branding. (Mock controls below)</Typography>
          <button>Upload Logo</button> <button>Set Theme Color</button>
        </Box>
      )}
      {tab === 10 && (
        <Box>
          <Typography variant="h6">License Management</Typography>
          <Typography>View and update license info. (Mock info below)</Typography>
          <p>License Key: XXXX-YYYY-ZZZZ</p><p>Seats Used: 12/50</p>
        </Box>
      )}
      {tab === 11 && (
        <Box>
          <Typography variant="h6">Advanced Audit Log Search</Typography>
          <Typography>Filter logs by user, action, or date. (Mock search below)</Typography>
          <form style={{marginTop:8}}><input type="text" placeholder="Search logs..." /> <button>Search</button></form>
        </Box>
      )}
    </Box>
  );
};

export default EnterpriseAdminPanel;
