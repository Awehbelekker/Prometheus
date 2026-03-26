import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  Button,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress
} from '@mui/material';
import {
  Search as SearchIcon,
  Download as DownloadIcon,
  Security as SecurityIcon,
  Shield as ShieldIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { format } from 'date-fns';

interface AuditLog {
  id: string;
  timestamp: string;
  user_id: string;
  username: string;
  action: string;
  resource: string;
  details: string;
  ip_address: string;
  user_agent: string;
  status: 'success' | 'failed' | 'warning';
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

interface ComplianceCheck {
  id: string;
  rule_name: string;
  description: string;
  status: 'passed' | 'failed' | 'warning';
  last_checked: string;
  details: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

const EnhancedAuditLogViewer: React.FC = () => {
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [complianceChecks, setComplianceChecks] = useState<ComplianceCheck[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterRisk, setFilterRisk] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);

  const fetchAuditData = async () => {
    try {
      setLoading(true);
      
      // Generate mock audit logs
      const mockLogs: AuditLog[] = [];
      const actions = [
        'Login', 'Logout', 'Trade Executed', 'Settings Changed', 'User Created',
        'Agent Started', 'Agent Stopped', 'Data Export', 'Permission Changed',
        'Password Reset', 'API Key Generated', 'Trade Failed', 'System Alert'
      ];
      const resources = [
        'User Account', 'Trading System', 'Agent Controller', 'Configuration',
        'Database', 'API Endpoint', 'Security Settings', 'Audit System'
      ];
      
      for (let i = 0; i < 100; i++) {
        const timestamp = new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000);
        const action = actions[Math.floor(Math.random() * actions.length)];
        const resource = resources[Math.floor(Math.random() * resources.length)];
        const status = Math.random() > 0.1 ? 'success' : Math.random() > 0.5 ? 'failed' : 'warning';
        const risk = Math.random() > 0.8 ? 'high' : Math.random() > 0.6 ? 'medium' : 'low';
        
        mockLogs.push({
          id: `audit-${i}`,
          timestamp: timestamp.toISOString(),
          user_id: `user-${Math.floor(Math.random() * 10)}`,
          username: `user${Math.floor(Math.random() * 10)}`,
          action,
          resource,
          details: `${action} performed on ${resource}`,
          ip_address: `192.168.1.${Math.floor(Math.random() * 255)}`,
          user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          status: status as any,
          risk_level: risk as any
        });
      }
      
      // Generate mock compliance checks
      const mockCompliance: ComplianceCheck[] = [
        {
          id: 'comp-1',
          rule_name: 'Password Policy Compliance',
          description: 'All users must have strong passwords',
          status: 'passed',
          last_checked: new Date().toISOString(),
          details: 'All 15 user accounts meet password requirements',
          severity: 'medium'
        },
        {
          id: 'comp-2',
          rule_name: 'Two-Factor Authentication',
          description: 'Admin accounts must have 2FA enabled',
          status: 'warning',
          last_checked: new Date().toISOString(),
          details: '2 of 3 admin accounts have 2FA enabled',
          severity: 'high'
        },
        {
          id: 'comp-3',
          rule_name: 'Trading Limits Compliance',
          description: 'Daily trading limits must not exceed $100,000',
          status: 'passed',
          last_checked: new Date().toISOString(),
          details: 'All agents operating within limits',
          severity: 'critical'
        },
        {
          id: 'comp-4',
          rule_name: 'Data Encryption',
          description: 'All sensitive data must be encrypted at rest',
          status: 'passed',
          last_checked: new Date().toISOString(),
          details: 'Database encryption verified',
          severity: 'high'
        },
        {
          id: 'comp-5',
          rule_name: 'Audit Log Retention',
          description: 'Audit logs must be retained for 365 days',
          status: 'passed',
          last_checked: new Date().toISOString(),
          details: 'Log retention policy active',
          severity: 'medium'
        },
        {
          id: 'comp-6',
          rule_name: 'API Rate Limiting',
          description: 'API endpoints must have rate limiting enabled',
          status: 'failed',
          last_checked: new Date().toISOString(),
          details: '3 endpoints missing rate limiting',
          severity: 'medium'
        }
      ];
      
      setAuditLogs(mockLogs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()));
      setComplianceChecks(mockCompliance);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch audit data:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditData();
  }, []);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleViewDetails = (log: AuditLog) => {
    setSelectedLog(log);
    setDetailsDialogOpen(true);
  };

  const handleExportLogs = () => {
    const csvContent = [
      ['Timestamp', 'User', 'Action', 'Resource', 'Status', 'Risk Level', 'IP Address'],
      ...filteredLogs.map(log => [
        format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm:ss'),
        log.username,
        log.action,
        log.resource,
        log.status,
        log.risk_level,
        log.ip_address
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-logs-${format(new Date(), 'yyyy-MM-dd')}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'failed':
        return <WarningIcon color="error" />;
      default:
        return <CheckCircleIcon color="disabled" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  // Filter logs based on search and filters
  const filteredLogs = auditLogs.filter(log => {
    const matchesSearch = searchTerm === '' || 
      log.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.resource.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || log.status === filterStatus;
    const matchesRisk = filterRisk === 'all' || log.risk_level === filterRisk;
    
    let matchesDate = true;
    if (dateFrom && dateTo) {
      const logDate = new Date(log.timestamp);
      const fromDate = new Date(dateFrom);
      const toDate = new Date(dateTo);
      matchesDate = logDate >= fromDate && logDate <= toDate;
    }
    
    return matchesSearch && matchesStatus && matchesRisk && matchesDate;
  });

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Security & Compliance Dashboard
      </Typography>

      {/* Compliance Status Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Compliance Score
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {Math.round((complianceChecks.filter(c => c.status === 'passed').length / complianceChecks.length) * 100)}%
                  </Typography>
                </Box>
                <ShieldIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Security Alerts
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {auditLogs.filter(log => log.risk_level === 'high' || log.risk_level === 'critical').length}
                  </Typography>
                </Box>
                <SecurityIcon color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Failed Actions
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {auditLogs.filter(log => log.status === 'failed').length}
                  </Typography>
                </Box>
                <WarningIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Events
                  </Typography>
                  <Typography variant="h4">
                    {auditLogs.length.toLocaleString()}
                  </Typography>
                </Box>
                <CheckCircleIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Compliance Checks */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Compliance Checks
          </Typography>
          <Grid container spacing={2}>
            {complianceChecks.map((check) => (
              <Grid item xs={12} md={6} key={check.id}>
                <Alert
                  severity={getStatusColor(check.status) as any}
                  icon={getStatusIcon(check.status)}
                  sx={{ mb: 1 }}
                >
                  <Box>
                    <Typography variant="body2" fontWeight="medium">
                      {check.rule_name}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {check.description}
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip
                        label={check.severity}
                        size="small"
                        color={getRiskColor(check.severity) as any}
                        sx={{ mr: 1 }}
                      />
                      <Typography variant="caption">
                        Last checked: {format(new Date(check.last_checked), 'MMM dd, HH:mm')}
                      </Typography>
                    </Box>
                  </Box>
                </Alert>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Audit Logs */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Audit Logs
            </Typography>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleExportLogs}
            >
              Export Logs
            </Button>
          </Box>

          {/* Filters */}
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1 }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="success">Success</MenuItem>
                  <MenuItem value="failed">Failed</MenuItem>
                  <MenuItem value="warning">Warning</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Risk Level</InputLabel>
                <Select
                  value={filterRisk}
                  onChange={(e) => setFilterRisk(e.target.value)}
                  label="Risk Level"
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2.5}>
              <TextField
                fullWidth
                label="From Date"
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={2.5}>
              <TextField
                fullWidth
                label="To Date"
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>

          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Risk Level</TableCell>
                <TableCell>IP Address</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredLogs
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>
                      {format(new Date(log.timestamp), 'MMM dd, HH:mm:ss')}
                    </TableCell>
                    <TableCell>{log.username}</TableCell>
                    <TableCell>{log.action}</TableCell>
                    <TableCell>{log.resource}</TableCell>
                    <TableCell>
                      <Chip
                        label={log.status}
                        color={getStatusColor(log.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={log.risk_level}
                        color={getRiskColor(log.risk_level) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{log.ip_address}</TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        onClick={() => handleViewDetails(log)}
                      >
                        Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>

          <TablePagination
            rowsPerPageOptions={[10, 25, 50, 100]}
            component="div"
            count={filteredLogs.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </CardContent>
      </Card>

      {/* Details Dialog */}
      <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Audit Log Details</DialogTitle>
        <DialogContent>
          {selectedLog && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Timestamp</Typography>
                <Typography variant="body1">{format(new Date(selectedLog.timestamp), 'PPpp')}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">User</Typography>
                <Typography variant="body1">{selectedLog.username} ({selectedLog.user_id})</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Action</Typography>
                <Typography variant="body1">{selectedLog.action}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Resource</Typography>
                <Typography variant="body1">{selectedLog.resource}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Status</Typography>
                <Chip label={selectedLog.status} color={getStatusColor(selectedLog.status) as any} />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Risk Level</Typography>
                <Chip label={selectedLog.risk_level} color={getRiskColor(selectedLog.risk_level) as any} />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">IP Address</Typography>
                <Typography variant="body1">{selectedLog.ip_address}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="textSecondary">User Agent</Typography>
                <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>{selectedLog.user_agent}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="textSecondary">Details</Typography>
                <Typography variant="body1">{selectedLog.details}</Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EnhancedAuditLogViewer;
