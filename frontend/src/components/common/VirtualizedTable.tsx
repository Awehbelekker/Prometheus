import React, { useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableContainer,
  Paper,
  Box
} from '@mui/material';

interface VirtualizedTableProps<T> {
  items: T[];
  columns: {
    key: string;
    label: string;
    width?: number;
    render?: (item: T, index: number) => React.ReactNode;
  }[];
  height?: number;
  rowHeight?: number;
  onRowClick?: (item: T, index: number) => void;
}

/**
 * Virtualized Table Component
 * Efficiently renders large lists by only rendering visible items
 * Use this for tables with 100+ rows
 */
function VirtualizedTable<T extends Record<string, any>>({
  items,
  columns,
  height = 600,
  rowHeight = 60,
  onRowClick
}: VirtualizedTableProps<T>) {
  const totalWidth = useMemo(() => {
    return columns.reduce((sum, col) => sum + (col.width || 150), 0);
  }, [columns]);

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const item = items[index];
    if (!item) return null;

    return (
      <TableRow
        style={style}
        hover
        onClick={() => onRowClick?.(item, index)}
        sx={{
          cursor: onRowClick ? 'pointer' : 'default',
          transition: 'all 0.2s ease',
          '&:hover': {
            backgroundColor: 'rgba(0, 212, 255, 0.05)'
          }
        }}
      >
        {columns.map((column) => (
          <TableCell
            key={column.key}
            sx={{
              width: column.width || 150,
              color: 'white',
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
            }}
          >
            {column.render ? column.render(item, index) : item[column.key]}
          </TableCell>
        ))}
      </TableRow>
    );
  };

  return (
    <TableContainer
      component={Paper}
      sx={{
        background: 'rgba(42, 42, 42, 0.5)',
        borderRadius: 2,
        overflow: 'hidden',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        height
      }}
    >
      <Table>
        <TableHead>
          <TableRow sx={{ backgroundColor: 'rgba(0, 212, 255, 0.05)' }}>
            {columns.map((column) => (
              <TableCell
                key={column.key}
                sx={{
                  width: column.width || 150,
                  color: '#aaa',
                  fontWeight: 600,
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
                }}
              >
                {column.label}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
      </Table>
      <Box sx={{ height: height - 60, overflow: 'hidden' }}>
        <List
          height={height - 60}
          itemCount={items.length}
          itemSize={rowHeight}
          width={totalWidth}
        >
          {Row}
        </List>
      </Box>
    </TableContainer>
  );
}

export default VirtualizedTable;

