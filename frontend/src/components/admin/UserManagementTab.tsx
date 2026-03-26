import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Avatar,
  Box,
  Typography,
  IconButton,
  Tooltip,
  LinearProgress
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  AttachMoney,
  Visibility,
  Edit,
  PersonAdd
} from '@mui/icons-material';

interface User {
  id: string;
  name: string;
  email: string;
  status: 'pending' | 'approved' | 'rejected' | 'active';
  investmentAmount: number;
  allocatedFunds: number;
  currentValue: number;
  pnl: number;
  pnlPercentage: number;
  joinDate: string;
  tier: 'silver' | 'gold' | 'platinum';
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
}

interface UserManagementTabProps {
  users: User[];
  onApprove: (userId: string) => void;
  onReject: (userId: string) => void;
  onAllocate: (user: User) => void;
  loading: boolean;
  formatCurrency: (amount: number) => string;
  formatPercentage: (value: number) => string;
  getStatusColor: (status: string) => any;
  getTierColor: (tier: string) => string;
}

const UserManagementTab: React.FC<UserManagementTabProps> = ({
  users,
  onApprove,
  onReject,
  onAllocate,
  loading,
  formatCurrency,
  formatPercentage,
  getStatusColor,
  getTierColor
}) => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          👥 User Management & Approvals
        </Typography>
        <Button
          variant="contained"
          startIcon={<PersonAdd />}
          sx={{ background: 'linear-gradient(45deg, #00d4ff, #0099cc)' }}
        >
          Invite New User
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <TableContainer component={Paper} sx={{ background: 'rgba(42, 42, 42, 0.5)' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>User</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Tier</TableCell>
              <TableCell>Investment</TableCell>
              <TableCell>Allocated</TableCell>
              <TableCell>Current Value</TableCell>
              <TableCell>P&L</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id} hover>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar sx={{ bgcolor: getTierColor(user.tier) }}>
                      {user.name.charAt(0)}
                    </Avatar>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {user.name}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        {user.email}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                
                <TableCell>
                  <Chip
                    label={user.status.toUpperCase()}
                    color={getStatusColor(user.status)}
                    size="small"
                    sx={{ fontWeight: 600 }}
                  />
                </TableCell>
                
                <TableCell>
                  <Chip
                    label={user.tier.toUpperCase()}
                    sx={{
                      bgcolor: getTierColor(user.tier),
                      color: 'white',
                      fontWeight: 600
                    }}
                    size="small"
                  />
                </TableCell>
                
                <TableCell>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {formatCurrency(user.investmentAmount)}
                  </Typography>
                </TableCell>
                
                <TableCell>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {formatCurrency(user.allocatedFunds)}
                  </Typography>
                </TableCell>
                
                <TableCell>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {formatCurrency(user.currentValue)}
                  </Typography>
                </TableCell>
                
                <TableCell>
                  <Box>
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: 600,
                        color: user.pnl >= 0 ? '#4caf50' : '#f44336'
                      }}
                    >
                      {formatCurrency(user.pnl)}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        color: user.pnl >= 0 ? '#4caf50' : '#f44336'
                      }}
                    >
                      {formatPercentage(user.pnlPercentage)}
                    </Typography>
                  </Box>
                </TableCell>
                
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {user.status === 'pending' && (
                      <>
                        <Tooltip title="Approve User">
                          <IconButton
                            size="small"
                            onClick={() => onApprove(user.id)}
                            sx={{ color: '#4caf50' }}
                          >
                            <CheckCircle />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Reject User">
                          <IconButton
                            size="small"
                            onClick={() => onReject(user.id)}
                            sx={{ color: '#f44336' }}
                          >
                            <Cancel />
                          </IconButton>
                        </Tooltip>
                      </>
                    )}
                    
                    {(user.status === 'approved' || user.status === 'active') && (
                      <Tooltip title="Allocate Funds">
                        <IconButton
                          size="small"
                          onClick={() => onAllocate(user)}
                          sx={{ color: '#00d4ff' }}
                        >
                          <AttachMoney />
                        </IconButton>
                      </Tooltip>
                    )}
                    
                    <Tooltip title="View Details">
                      <IconButton size="small" sx={{ color: '#ff9800' }}>
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    
                    <Tooltip title="Edit User">
                      <IconButton size="small" sx={{ color: '#9c27b0' }}>
                        <Edit />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {users.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" sx={{ color: 'text.secondary', mb: 2 }}>
            No users found
          </Typography>
          <Button
            variant="contained"
            startIcon={<PersonAdd />}
            sx={{ background: 'linear-gradient(45deg, #00d4ff, #0099cc)' }}
          >
            Invite First User
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default UserManagementTab;
