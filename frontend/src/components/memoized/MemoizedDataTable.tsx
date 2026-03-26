import React, { memo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';

interface MemoizedDataTableProps {
  headers: string[];
  rows: any[];
  renderRow: (row: any, index: number) => React.ReactNode;
  loading?: boolean;
}

/**
 * Memoized data table component for better performance
 * Only re-renders when props actually change
 */
const MemoizedDataTable: React.FC<MemoizedDataTableProps> = memo(({
  headers,
  rows,
  renderRow,
  loading = false
}) => {
  return (
    <TableContainer component={Paper} sx={{ background: 'rgba(42, 42, 42, 0.5)' }}>
      <Table>
        <TableHead>
          <TableRow>
            {headers.map((header, index) => (
              <TableCell key={index} sx={{ color: '#00d4ff', fontWeight: 600 }}>
                {header}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {loading ? (
            <TableRow>
              <TableCell colSpan={headers.length} sx={{ textAlign: 'center', py: 4 }}>
                Loading...
              </TableCell>
            </TableRow>
          ) : (
            rows.map((row, index) => renderRow(row, index))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function for better memoization
  return (
    prevProps.headers.length === nextProps.headers.length &&
    prevProps.rows.length === nextProps.rows.length &&
    prevProps.loading === nextProps.loading &&
    JSON.stringify(prevProps.rows) === JSON.stringify(nextProps.rows)
  );
});

MemoizedDataTable.displayName = 'MemoizedDataTable';

export default MemoizedDataTable;