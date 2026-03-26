/**
 * Export utilities for admin portal
 * Supports CSV, Excel, and JSON export formats
 */

import { logger } from './logger';

/**
 * Convert array of objects to CSV string
 */
export function arrayToCSV<T extends Record<string, any>>(
  data: T[],
  headers?: string[]
): string {
  if (data.length === 0) {
    return '';
  }

  // Use provided headers or extract from first object
  const csvHeaders = headers || Object.keys(data[0]);
  
  // Create header row
  const headerRow = csvHeaders.map(header => `"${String(header).replace(/"/g, '""')}"`).join(',');
  
  // Create data rows
  const dataRows = data.map(row => {
    return csvHeaders.map(header => {
      const value = row[header];
      if (value === null || value === undefined) {
        return '""';
      }
      // Escape quotes and wrap in quotes
      return `"${String(value).replace(/"/g, '""')}"`;
    }).join(',');
  });

  return [headerRow, ...dataRows].join('\n');
}

/**
 * Download data as CSV file
 */
export function downloadCSV<T extends Record<string, any>>(
  data: T[],
  filename: string,
  headers?: string[]
): void {
  try {
    const csv = arrayToCSV(data, headers);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    logger.info(`CSV exported: ${filename}`, { rowCount: data.length }, 'Export');
  } catch (error) {
    logger.error('Failed to export CSV', error, 'Export');
    throw error;
  }
}

/**
 * Convert array of objects to JSON string
 */
export function arrayToJSON<T>(data: T[], pretty: boolean = true): string {
  if (pretty) {
    return JSON.stringify(data, null, 2);
  }
  return JSON.stringify(data);
}

/**
 * Download data as JSON file
 */
export function downloadJSON<T>(
  data: T[],
  filename: string,
  pretty: boolean = true
): void {
  try {
    const json = arrayToJSON(data, pretty);
    const blob = new Blob([json], { type: 'application/json;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}.json`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    logger.info(`JSON exported: ${filename}`, { rowCount: data.length }, 'Export');
  } catch (error) {
    logger.error('Failed to export JSON', error, 'Export');
    throw error;
  }
}

/**
 * Export user data with formatted columns
 */
export function exportUsers(users: any[], format: 'csv' | 'json' = 'csv'): void {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `prometheus-users-${timestamp}`;

  // Format user data for export
  const formattedUsers = users.map(user => ({
    'User ID': user.id,
    'Username': user.username || user.name,
    'Email': user.email,
    'Status': user.status,
    'Tier': user.tier,
    'Allocated Funds': user.allocatedFunds || user.allocated_funds || 0,
    'Current Value': user.currentValue || user.current_value || 0,
    'P&L': user.pnl || 0,
    'P&L %': user.pnlPercentage || user.pnl_percentage || 0,
    'Live Trading': user.liveTrading || user.live_trading ? 'Yes' : 'No',
    'Join Date': user.joinDate || user.join_date || '',
    'Last Activity': user.lastActivity || user.last_activity || ''
  }));

  if (format === 'csv') {
    downloadCSV(formattedUsers, filename);
  } else {
    downloadJSON(formattedUsers, filename);
  }
}

/**
 * Export audit logs
 */
export function exportAuditLogs(logs: any[], format: 'csv' | 'json' = 'csv'): void {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `prometheus-audit-logs-${timestamp}`;

  const formattedLogs = logs.map(log => ({
    'Timestamp': log.timestamp || log.created_at || '',
    'User ID': log.user_id || '',
    'Action': log.action || log.action_type || '',
    'Resource': log.resource || '',
    'Details': typeof log.details === 'string' ? log.details : JSON.stringify(log.details || {}),
    'IP Address': log.ip_address || '',
    'Status': log.status || 'success'
  }));

  if (format === 'csv') {
    downloadCSV(formattedLogs, filename);
  } else {
    downloadJSON(formattedLogs, filename);
  }
}

/**
 * Export admin metrics
 */
export function exportAdminMetrics(metrics: any, format: 'csv' | 'json' = 'json'): void {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `prometheus-admin-metrics-${timestamp}`;

  const formattedMetrics = {
    'Export Date': new Date().toISOString(),
    'Total Users': metrics.totalUsers || 0,
    'Active Traders': metrics.activeTraders || 0,
    'Total Allocated Funds': metrics.totalAllocated || 0,
    'Total Portfolio Value': metrics.totalPortfolioValue || 0,
    'Daily P&L': metrics.dailyPnL || 0,
    'System Uptime %': metrics.systemUptime || 0,
    'Pending Approvals': metrics.pendingApprovals || 0,
    'Active Sessions': metrics.activeSessions || 0
  };

  if (format === 'csv') {
    downloadCSV([formattedMetrics], filename);
  } else {
    downloadJSON([formattedMetrics], filename);
  }
}

/**
 * Export revolutionary AI data (from RevolutionaryAIPanel)
 */
export function exportRevolutionaryAI(data: any): void {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `prometheus-revolutionary-ai-${timestamp}`;
  downloadJSON(data, filename);
}

/**
 * Export all agents data (from HierarchicalAgentMonitor)
 */
export function exportAllAgents(data: any): void {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `prometheus-agents-${timestamp}`;
  downloadJSON(data, filename);
}

/**
 * Export to PDF (requires jspdf and jspdf-autotable libraries)
 * This is a placeholder - install libraries to enable:
 * npm install jspdf jspdf-autotable
 */
export async function exportToPDF<T extends Record<string, any>>(
  data: T[],
  filename: string,
  title: string = 'Export'
): Promise<void> {
  try {
    // Dynamic import to avoid errors if library not installed
    const { default: jsPDF } = await import('jspdf');
    const autoTable = (await import('jspdf-autotable')).default;
    
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(16);
    doc.text(title, 14, 15);
    doc.setFontSize(10);
    doc.text(`Exported: ${new Date().toLocaleString()}`, 14, 22);
    
    // Convert data to table format
    const headers = data.length > 0 ? Object.keys(data[0]) : [];
    const rows = data.map(row => headers.map(header => String(row[header] || '')));
    
    // Add table
    autoTable(doc, {
      head: [headers],
      body: rows,
      startY: 30,
      styles: { fontSize: 8 },
      headStyles: { fillColor: [0, 212, 255] }
    });
    
    // Save
    doc.save(`${filename}.pdf`);
    logger.info(`PDF exported: ${filename}`, { rowCount: data.length }, 'Export');
  } catch (error) {
    logger.warn('PDF export library not installed. Install with: npm install jspdf jspdf-autotable', error, 'Export');
    // Fallback to CSV
    downloadCSV(data, filename);
  }
}

/**
 * Export to Excel (requires xlsx library)
 * This is a placeholder - install library to enable:
 * npm install xlsx
 */
export async function exportToExcel<T extends Record<string, any>>(
  data: T[],
  filename: string,
  sheetName: string = 'Sheet1'
): Promise<void> {
  try {
    // Dynamic import to avoid errors if library not installed
    const XLSX = await import('xlsx');
    
    // Convert data to worksheet
    const ws = XLSX.utils.json_to_sheet(data);
    
    // Create workbook
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, sheetName);
    
    // Write file
    XLSX.writeFile(wb, `${filename}.xlsx`);
    logger.info(`Excel exported: ${filename}`, { rowCount: data.length }, 'Export');
  } catch (error) {
    logger.warn('Excel export library not installed. Install with: npm install xlsx', error, 'Export');
    // Fallback to CSV
    downloadCSV(data, filename);
  }
}
