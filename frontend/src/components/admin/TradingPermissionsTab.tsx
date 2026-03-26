import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  LinearProgress,
  Avatar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Switch,
  Checkbox,
  FormControlLabel,
  Divider
} from '@mui/material';
import {
  VpnKey,
  Security,
  Check,
  Close,
  Edit,
  Delete,
  Warning,
  Info,
  Schedule,
  ExpandMore,
  Shield,
  VerifiedUser,
  Block,
  Approval,
  AccessTime,
  Assignment,
  PersonAdd,
  GroupAdd,
  Visibility,
  SupervisorAccount
} from '@mui/icons-material';

interface Permission {
  permission_id: string;
  user_id: string;
  username: string;
  permission_type: string;
  granted_by: string;
  granted_at: string;
  expires_at?: string;
  is_active: boolean;
  conditions: string[];
}

interface User {
  user_id: string;
  username: string;
  email: string;
  role: string;
  live_trading_approved: boolean;
  max_allocation: number;
  current_allocation: number;
  is_active: boolean;
}

interface TradingPermissionsTabProps {
  permissions: Permission[];
  users: User[];
  onApproveTrading: (user: User) => void;
  onRevokeTrading: (user: User) => void;
  onUpdatePermission: (permission: Permission, updates: any) => void;
  onRevokePermission: (permission: Permission) => void;
  loading: boolean;
  formatDate: (date: string) => string;
  getStatusIcon: (status: string) => React.ReactNode;
  showAlert: (type: 'success' | 'error' | 'info' | 'warning', message: string) => void;
}

const TradingPermissionsTab: React.FC<TradingPermissionsTabProps> = ({
  permissions,
  users,
  onApproveTrading,
  onRevokeTrading,
  onUpdatePermission,
  onRevokePermission,
  loading,
  formatDate,
  getStatusIcon,
  showAlert
}) => {
  const [selectedPermission, setSelectedPermission] = useState<Permission | null>(null);
  const [permissionDialog, setPermissionDialog] = useState(false);
  const [bulkApprovalDialog, setBulkApprovalDialog] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [permissionFilter, setPermissionFilter] = useState('all');
  const [expandedAccordion, setExpandedAccordion] = useState<string | false>('pending');

  const getPermissionsByType = () => {
    const grouped = permissions.reduce((acc, permission) => {
      const type = permission.permission_type;
      if (!acc[type]) acc[type] = [];
      acc[type].push(permission);
      return acc;
    }, {} as Record<string, Permission[]>);
    return grouped;
  };

  const getPendingApprovals = () => {
    return users.filter(user => user.is_active && !user.live_trading_approved);
  };

  const getApprovedTraders = () => {
    return users.filter(user => user.live_trading_approved);
  };

  const handleBulkApproval = () => {
    if (selectedUsers.length === 0) {
      showAlert('warning', 'Please select users to approve');
      return;
    }
    setBulkApprovalDialog(true);
  };

  const confirmBulkApproval = () => {
    selectedUsers.forEach(userId => {
      const user = users.find(u => u.user_id === userId);
      if (user) {
        onApproveTrading(user);
      }
    });
    setSelectedUsers([]);
    setBulkApprovalDialog(false);
    showAlert('success', `Approved ${selectedUsers.length} users for live trading`);
  };

  const handleUserSelection = (userId: string, checked: boolean) => {
    if (checked) {
      setSelectedUsers([...selectedUsers, userId]);
    } else {
      setSelectedUsers(selectedUsers.filter(id => id !== userId));
    }
  };

  const getPermissionColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'live_trading': return '#4caf50';
      case 'paper_trading': return '#2196f3';
      case 'view_portfolios': return '#ff9800';
      case 'manage_users': return '#f44336';
      case 'system_admin': return '#9c27b0';
      default: return '#757575';
    }
  };

  const getPermissionIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'live_trading': return <VerifiedUser />;
      case 'paper_trading': return <Assignment />;
      case 'view_portfolios': return <Visibility />;
      case 'manage_users': return <SupervisorAccount />;
      case 'system_admin': return <Shield />;
      default: return <Security />;
    }
  };

  return (
    <Box>
      {/* Header with Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
          Trading Permissions Management
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<GroupAdd />}
            onClick={handleBulkApproval}
            disabled={selectedUsers.length === 0}
            sx={{ borderColor: '#00d4ff', color: '#00d4ff' }}
          >
            Bulk Approve ({selectedUsers.length})
          </Button>
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <Select
              value={permissionFilter}
              onChange={(e) => setPermissionFilter(e.target.value)}
              sx={{
                color: 'white',
                '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' }
              }}
            >
              <MenuItem value="all">All Permissions</MenuItem>
              <MenuItem value="active">Active Only</MenuItem>
              <MenuItem value="expired">Expired</MenuItem>
              <MenuItem value="live_trading">Live Trading</MenuItem>
              <MenuItem value="paper_trading">Paper Trading</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Permission Management Sections */}
      <Grid container spacing={3}>
        {/* Pending Approvals */}
        <Grid item xs={12}>
          <Accordion 
            expanded={expandedAccordion === 'pending'} 
            onChange={(_, isExpanded) => setExpandedAccordion(isExpanded ? 'pending' : false)}
            sx={{ 
              backgroundColor: 'rgba(26, 26, 46, 0.8)', 
              border: '1px solid rgba(255, 152, 0, 0.3)',
              '&:before': { display: 'none' }
            }}
          >
            <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#ff9800' }} />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Schedule sx={{ color: '#ff9800' }} />
                <Typography variant="h6" sx={{ color: '#ff9800' }}>
                  Pending Live Trading Approvals ({getPendingApprovals().length})
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell padding="checkbox">
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={selectedUsers.length === getPendingApprovals().length && getPendingApprovals().length > 0}
                              indeterminate={selectedUsers.length > 0 && selectedUsers.length < getPendingApprovals().length}
                              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                                if (e.target.checked) {
                                  setSelectedUsers(getPendingApprovals().map(u => u.user_id));
                                } else {
                                  setSelectedUsers([]);
                                }
                              }}
                              sx={{ color: '#00d4ff' }}
                            />
                          }
                          label=""
                        />
                      </TableCell>
                      <TableCell sx={{ color: '#aaa' }}>User</TableCell>
                      <TableCell sx={{ color: '#aaa' }}>Role</TableCell>
                      <TableCell sx={{ color: '#aaa' }}>Current Access</TableCell>
                      <TableCell sx={{ color: '#aaa' }}>Risk Assessment</TableCell>
                      <TableCell sx={{ color: '#aaa' }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {getPendingApprovals().map((user) => (
                      <TableRow key={user.user_id}>
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={selectedUsers.includes(user.user_id)}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleUserSelection(user.user_id, e.target.checked)}
                            sx={{ color: '#00d4ff' }}
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar sx={{ width: 32, height: 32, bgcolor: '#00d4ff' }}>
                              {user.username.charAt(0).toUpperCase()}
                            </Avatar>
                            <Box>
                              <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
                                {user.username}
                              </Typography>
                              <Typography variant="caption" sx={{ color: '#aaa' }}>
                                {user.email}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip label={user.role} size="small" color="primary" />
                        </TableCell>
                        <TableCell>
                          <Chip label="Paper Trading Only" size="small" color="default" />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Info sx={{ color: '#2196f3', fontSize: 16 }} />
                            <Typography variant="caption" sx={{ color: '#aaa' }}>
                              Pending Review
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Tooltip title="Approve Live Trading">
                              <IconButton
                                size="small"
                                onClick={() => onApproveTrading(user)}
                                sx={{ color: '#4caf50' }}
                              >
                                <Check />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Reject Application">
                              <IconButton
                                size="small"
                                sx={{ color: '#f44336' }}
                              >
                                <Close />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Active Permissions */}
        <Grid item xs={12}>
          <Accordion 
            expanded={expandedAccordion === 'active'} 
            onChange={(_, isExpanded) => setExpandedAccordion(isExpanded ? 'active' : false)}
            sx={{ 
              backgroundColor: 'rgba(26, 26, 46, 0.8)', 
              border: '1px solid rgba(76, 175, 80, 0.3)',
              '&:before': { display: 'none' }
            }}
          >
            <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#4caf50' }} />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <VerifiedUser sx={{ color: '#4caf50' }} />
                <Typography variant="h6" sx={{ color: '#4caf50' }}>
                  Active Live Traders ({getApprovedTraders().length})
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: '#aaa' }}>User</TableCell>
                      <TableCell sx={{ color: '#aaa' }}>Permissions</TableCell>
                      <TableCell sx={{ color: '#aaa' }}>Granted By</TableCell>
                      <TableCell sx={{ color: '#aaa' }}>Granted Date</TableCell>
                      <TableCell sx={{ color: '#aaa' }}>Expires</TableCell>
                      <TableCell sx={{ color: '#aaa' }}>Status</TableCell>
                      <TableCell sx={{ color: '#aaa' }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {getApprovedTraders().map((user) => {
                      const userPermissions = permissions.filter(p => p.user_id === user.user_id);
                      return (
                        <TableRow key={user.user_id}>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Avatar sx={{ width: 32, height: 32, bgcolor: '#4caf50' }}>
                                {user.username.charAt(0).toUpperCase()}
                              </Avatar>
                              <Box>
                                <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
                                  {user.username}
                                </Typography>
                                <Typography variant="caption" sx={{ color: '#aaa' }}>
                                  {user.email}
                                </Typography>
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                              {userPermissions.map((permission) => (
                                <Chip
                                  key={permission.permission_id}
                                  label={permission.permission_type.replace('_', ' ')}
                                  size="small"
                                  sx={{
                                    backgroundColor: `${getPermissionColor(permission.permission_type)}20`,
                                    color: getPermissionColor(permission.permission_type),
                                    border: `1px solid ${getPermissionColor(permission.permission_type)}40`
                                  }}
                                />
                              ))}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" sx={{ color: 'white' }}>
                              {userPermissions[0]?.granted_by || 'System'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" sx={{ color: '#aaa' }}>
                              {userPermissions[0] ? formatDate(userPermissions[0].granted_at) : '-'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" sx={{ color: '#aaa' }}>
                              {userPermissions[0]?.expires_at ? formatDate(userPermissions[0].expires_at) : 'Never'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {getStatusIcon('active')}
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Tooltip title="Edit Permissions">
                                <IconButton
                                  size="small"
                                  onClick={() => {
                                    setSelectedPermission(userPermissions[0]);
                                    setPermissionDialog(true);
                                  }}
                                  sx={{ color: '#00d4ff' }}
                                >
                                  <Edit />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Revoke Live Trading">
                                <IconButton
                                  size="small"
                                  onClick={() => onRevokeTrading(user)}
                                  sx={{ color: '#f44336' }}
                                >
                                  <Block />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>

      {/* Bulk Approval Dialog */}
      <Dialog open={bulkApprovalDialog} onClose={() => setBulkApprovalDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          Bulk Approve Live Trading
        </DialogTitle>
        <DialogContent sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Are you sure you want to approve live trading for {selectedUsers.length} selected users?
          </Typography>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will grant live trading permissions with default allocation limits. You can adjust individual limits later.
          </Alert>
        </DialogContent>
        <DialogActions sx={{ bgcolor: '#1a1a2e' }}>
          <Button onClick={() => setBulkApprovalDialog(false)}>Cancel</Button>
          <Button onClick={confirmBulkApproval} variant="contained" color="primary">
            Approve All
          </Button>
        </DialogActions>
      </Dialog>

      {/* Permission Edit Dialog */}
      <Dialog open={permissionDialog} onClose={() => setPermissionDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          Edit Permission - {selectedPermission?.username}
        </DialogTitle>
        <DialogContent sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          {selectedPermission && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Permission Type"
                    value={selectedPermission.permission_type}
                    disabled
                    InputProps={{ style: { color: 'white' } }}
                    InputLabelProps={{ style: { color: '#aaa' } }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Expires At"
                    type="datetime-local"
                    defaultValue={selectedPermission.expires_at}
                    InputProps={{ style: { color: 'white' } }}
                    InputLabelProps={{ style: { color: '#aaa' } }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={selectedPermission.is_active}
                        sx={{
                          '& .MuiSwitch-switchBase.Mui-checked': { color: '#00d4ff' },
                          '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { backgroundColor: '#00d4ff' }
                        }}
                      />
                    }
                    label="Active"
                    sx={{ color: 'white' }}
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ bgcolor: '#1a1a2e' }}>
          <Button onClick={() => setPermissionDialog(false)}>Cancel</Button>
          <Button variant="contained" color="primary">
            Update Permission
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TradingPermissionsTab;
