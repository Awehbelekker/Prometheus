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
  Grid,
  Alert,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TablePagination,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  Assignment,
  GetApp,
  CloudDownload,
  Visibility,
  Search,
  FilterList,
  DateRange,
  ExpandMore,
  History,
  Security,
  AdminPanelSettings,
  Person,
  AttachMoney,
  TrendingUp,
  Assessment,
  PictureAsPdf,
  TableChart,
  InsertChart,
  Schedule,
  CheckCircle,
  Error,
  Warning,
  Info
} from '@mui/icons-material';

interface AuditLog {
  log_id: string;
  admin_id: string;
  admin_username: string;
  action_type: string;
  target_user_id?: string;
  target_username?: string;
  action_details: string;
  timestamp: string;
  ip_address: string;
  user_agent: string;
  result: 'success' | 'failure' | 'partial';
  error_message?: string;
}

interface AuditReportingTabProps {
  auditLogs: AuditLog[];
  onGenerateReport: (reportType: string, params: any) => void;
  loading: boolean;
  formatDate: (date: string) => string;
  showAlert: (type: 'success' | 'error' | 'info' | 'warning', message: string) => void;
}

const AuditReportingTab: React.FC<AuditReportingTabProps> = ({
  auditLogs,
  onGenerateReport,
  loading,
  formatDate,
  showAlert
}) => {
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [logDetailDialog, setLogDetailDialog] = useState(false);
  const [reportDialog, setReportDialog] = useState(false);
  const [reportType, setReportType] = useState('');
  const [auditFilter, setAuditFilter] = useState('all');
  const [auditSearch, setAuditSearch] = useState('');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [auditPage, setAuditPage] = useState(0);
  const [auditRowsPerPage, setAuditRowsPerPage] = useState(25);
  const [activeTab, setActiveTab] = useState(0);
  const [expandedAccordion, setExpandedAccordion] = useState<string | false>('recent');

  const getFilteredLogs = () => {
    let filtered = auditLogs;
    
    // Filter by type
    if (auditFilter !== 'all') {
      filtered = filtered.filter(log => {
        switch (auditFilter) {
          case 'user_management': return log.action_type.includes('user') || log.action_type.includes('create') || log.action_type.includes('update');
          case 'permissions': return log.action_type.includes('approve') || log.action_type.includes('revoke') || log.action_type.includes('permission');
          case 'allocations': return log.action_type.includes('allocate') || log.action_type.includes('fund');
          case 'system': return log.action_type.includes('system') || log.action_type.includes('backup') || log.action_type.includes('restart');
          case 'security': return log.action_type.includes('login') || log.action_type.includes('security') || log.action_type.includes('auth');
          case 'errors': return log.result === 'failure' || log.result === 'partial';
          default: return true;
        }
      });
    }
    
    // Filter by search
    if (auditSearch) {
      const search = auditSearch.toLowerCase();
      filtered = filtered.filter(log => 
        log.admin_username.toLowerCase().includes(search) ||
        log.action_type.toLowerCase().includes(search) ||
        log.action_details.toLowerCase().includes(search) ||
        (log.target_username && log.target_username.toLowerCase().includes(search))
      );
    }
    
    // Filter by date range
    if (dateRange.start && dateRange.end) {
      const startDate = new Date(dateRange.start);
      const endDate = new Date(dateRange.end);
      filtered = filtered.filter(log => {
        const logDate = new Date(log.timestamp);
        return logDate >= startDate && logDate <= endDate;
      });
    }
    
    return filtered.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  };

  const getPaginatedLogs = () => {
    const filtered = getFilteredLogs();
    const start = auditPage * auditRowsPerPage;
    const end = start + auditRowsPerPage;
    return filtered.slice(start, end);
  };

  const getActionTypeColor = (actionType: string) => {
    if (actionType.includes('create') || actionType.includes('approve')) return '#4caf50';
    if (actionType.includes('delete') || actionType.includes('revoke')) return '#f44336';
    if (actionType.includes('update') || actionType.includes('modify')) return '#ff9800';
    if (actionType.includes('system') || actionType.includes('backup')) return '#2196f3';
    return '#757575';
  };

  const getResultIcon = (result: string) => {
    switch (result) {
      case 'success': return <CheckCircle sx={{ color: '#4caf50', fontSize: 16 }} />;
      case 'failure': return <Error sx={{ color: '#f44336', fontSize: 16 }} />;
      case 'partial': return <Warning sx={{ color: '#ff9800', fontSize: 16 }} />;
      default: return <Info sx={{ color: '#757575', fontSize: 16 }} />;
    }
  };

  const getAuditSummary = () => {
    const logs = getFilteredLogs();
    const today = new Date();
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

    return {
      total: logs.length,
      today: logs.filter(log => new Date(log.timestamp) >= yesterday).length,
      week: logs.filter(log => new Date(log.timestamp) >= lastWeek).length,
      success: logs.filter(log => log.result === 'success').length,
      failures: logs.filter(log => log.result === 'failure').length,
      admins: new Set(logs.map(log => log.admin_username)).size
    };
  };

  const handleGenerateReport = () => {
    if (!reportType) {
      showAlert('warning', 'Please select a report type');
      return;
    }

    const params = {
      type: reportType,
      dateRange: dateRange,
      filters: {
        auditFilter,
        auditSearch
      }
    };

    onGenerateReport(reportType, params);
    setReportDialog(false);
    showAlert('info', 'Report generation started. Download will begin shortly.');
  };

  const summary = getAuditSummary();

  return (
    <Box>
      {/* Header with Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%)', 
            border: '1px solid rgba(33, 150, 243, 0.3)'
          }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#2196f3' }}>
                {summary.total}
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Total Logs
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)', 
            border: '1px solid rgba(76, 175, 80, 0.3)'
          }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#4caf50' }}>
                {summary.today}
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Today
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%)', 
            border: '1px solid rgba(255, 152, 0, 0.3)'
          }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#ff9800' }}>
                {summary.week}
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                This Week
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)', 
            border: '1px solid rgba(76, 175, 80, 0.3)'
          }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#4caf50' }}>
                {summary.success}
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Successful
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%)', 
            border: '1px solid rgba(244, 67, 54, 0.3)'
          }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#f44336' }}>
                {summary.failures}
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Failed
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(156, 39, 176, 0.05) 100%)', 
            border: '1px solid rgba(156, 39, 176, 0.3)'
          }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#9c27b0' }}>
                {summary.admins}
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Active Admins
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
          Audit Trail & Reporting
        </Typography>
        
        <Button
          variant="contained"
          startIcon={<Assessment />}
          onClick={() => setReportDialog(true)}
          sx={{ bgcolor: '#00d4ff', '&:hover': { bgcolor: '#0099cc' } }}
        >
          Generate Report
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ 
        backgroundColor: 'rgba(26, 26, 46, 0.8)', 
        border: '1px solid rgba(0, 212, 255, 0.3)',
        mb: 3
      }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search logs..."
                value={auditSearch}
                onChange={(e) => setAuditSearch(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ color: '#aaa', mr: 1 }} />,
                  style: { color: 'white' }
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '&:hover fieldset': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                    '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                  }
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <Select
                  value={auditFilter}
                  onChange={(e) => setAuditFilter(e.target.value)}
                  sx={{
                    color: 'white',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' }
                  }}
                >
                  <MenuItem value="all">All Actions</MenuItem>
                  <MenuItem value="user_management">User Management</MenuItem>
                  <MenuItem value="permissions">Permissions</MenuItem>
                  <MenuItem value="allocations">Fund Allocations</MenuItem>
                  <MenuItem value="system">System Actions</MenuItem>
                  <MenuItem value="security">Security Events</MenuItem>
                  <MenuItem value="errors">Errors Only</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                type="date"
                label="Start Date"
                value={dateRange.start}
                onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                InputLabelProps={{ shrink: true, style: { color: '#aaa' } }}
                InputProps={{ style: { color: 'white' } }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '&:hover fieldset': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                    '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                  }
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                type="date"
                label="End Date"
                value={dateRange.end}
                onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                InputLabelProps={{ shrink: true, style: { color: '#aaa' } }}
                InputProps={{ style: { color: 'white' } }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '&:hover fieldset': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                    '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                  }
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    setAuditSearch('');
                    setAuditFilter('all');
                    setDateRange({ start: '', end: '' });
                  }}
                  sx={{ borderColor: '#666', color: '#666' }}
                >
                  Clear Filters
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Audit Logs Table */}
      <Card sx={{ 
        backgroundColor: 'rgba(26, 26, 46, 0.8)', 
        border: '1px solid rgba(0, 212, 255, 0.3)'
      }}>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>Timestamp</TableCell>
                  <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>Admin</TableCell>
                  <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>Action</TableCell>
                  <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>Target</TableCell>
                  <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>Result</TableCell>
                  <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>IP Address</TableCell>
                  <TableCell sx={{ color: '#aaa', fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {getPaginatedLogs().map((log) => (
                  <TableRow 
                    key={log.log_id}
                    sx={{ '&:hover': { backgroundColor: 'rgba(0, 212, 255, 0.05)' } }}
                  >
                    <TableCell>
                      <Typography variant="body2" sx={{ color: 'white' }}>
                        {formatDate(log.timestamp)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
                        {log.admin_username}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={log.action_type.replace('_', ' ')}
                        size="small"
                        sx={{
                          backgroundColor: `${getActionTypeColor(log.action_type)}20`,
                          color: getActionTypeColor(log.action_type),
                          border: `1px solid ${getActionTypeColor(log.action_type)}40`
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ color: '#aaa' }}>
                        {log.target_username || 'System'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getResultIcon(log.result)}
                        <Typography variant="body2" sx={{ color: 'white' }}>
                          {log.result}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ color: '#aaa' }}>
                        {log.ip_address}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setSelectedLog(log);
                            setLogDetailDialog(true);
                          }}
                          sx={{ color: '#00d4ff' }}
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <TablePagination
            component="div"
            count={getFilteredLogs().length}
            page={auditPage}
            onPageChange={(_, newPage) => setAuditPage(newPage)}
            rowsPerPage={auditRowsPerPage}
            onRowsPerPageChange={(e) => {
              setAuditRowsPerPage(parseInt(e.target.value, 10));
              setAuditPage(0);
            }}
            sx={{
              color: 'white',
              '& .MuiTablePagination-selectIcon': { color: 'white' },
              '& .MuiTablePagination-select': { color: 'white' },
              '& .MuiTablePagination-displayedRows': { color: 'white' }
            }}
          />
        </CardContent>
      </Card>

      {/* Log Detail Dialog */}
      <Dialog open={logDetailDialog} onClose={() => setLogDetailDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          Audit Log Details
        </DialogTitle>
        <DialogContent sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          {selectedLog && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ color: '#aaa' }}>Log ID</Typography>
                  <Typography variant="body1" sx={{ color: 'white', mb: 2 }}>{selectedLog.log_id}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ color: '#aaa' }}>Timestamp</Typography>
                  <Typography variant="body1" sx={{ color: 'white', mb: 2 }}>{formatDate(selectedLog.timestamp)}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ color: '#aaa' }}>Admin</Typography>
                  <Typography variant="body1" sx={{ color: 'white', mb: 2 }}>{selectedLog.admin_username}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ color: '#aaa' }}>Action Type</Typography>
                  <Typography variant="body1" sx={{ color: 'white', mb: 2 }}>{selectedLog.action_type}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ color: '#aaa' }}>Target User</Typography>
                  <Typography variant="body1" sx={{ color: 'white', mb: 2 }}>{selectedLog.target_username || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ color: '#aaa' }}>Result</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    {getResultIcon(selectedLog.result)}
                    <Typography variant="body1" sx={{ color: 'white' }}>{selectedLog.result}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ color: '#aaa' }}>IP Address</Typography>
                  <Typography variant="body1" sx={{ color: 'white', mb: 2 }}>{selectedLog.ip_address}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" sx={{ color: '#aaa' }}>User Agent</Typography>
                  <Typography variant="body2" sx={{ color: '#aaa', mb: 2, wordBreak: 'break-all' }}>
                    {selectedLog.user_agent}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" sx={{ color: '#aaa' }}>Action Details</Typography>
                  <Paper sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)', mb: 2 }}>
                    <Typography variant="body2" sx={{ color: 'white' }}>
                      {selectedLog.action_details}
                    </Typography>
                  </Paper>
                </Grid>
                {selectedLog.error_message && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ color: '#f44336' }}>Error Message</Typography>
                    <Paper sx={{ p: 2, backgroundColor: 'rgba(244, 67, 54, 0.1)', border: '1px solid rgba(244, 67, 54, 0.3)' }}>
                      <Typography variant="body2" sx={{ color: '#f44336' }}>
                        {selectedLog.error_message}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ bgcolor: '#1a1a2e' }}>
          <Button onClick={() => setLogDetailDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Report Generation Dialog */}
      <Dialog open={reportDialog} onClose={() => setReportDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          Generate Report
        </DialogTitle>
        <DialogContent sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel sx={{ color: '#aaa' }}>Report Type</InputLabel>
                <Select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  sx={{
                    color: 'white',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' }
                  }}
                >
                  <MenuItem value="audit_summary">Audit Summary Report</MenuItem>
                  <MenuItem value="user_activity">User Activity Report</MenuItem>
                  <MenuItem value="permission_changes">Permission Changes Report</MenuItem>
                  <MenuItem value="allocation_history">Allocation History Report</MenuItem>
                  <MenuItem value="system_events">System Events Report</MenuItem>
                  <MenuItem value="security_audit">Security Audit Report</MenuItem>
                  <MenuItem value="compliance_report">Compliance Report</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Alert severity="info">
                The report will include all data matching your current filters and date range.
              </Alert>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ bgcolor: '#1a1a2e' }}>
          <Button onClick={() => setReportDialog(false)}>Cancel</Button>
          <Button onClick={handleGenerateReport} variant="contained">
            Generate Report
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AuditReportingTab;
