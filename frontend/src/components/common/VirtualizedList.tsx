import React, { useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';
import { Box, ListItem, ListItemButton, ListItemText, alpha } from '@mui/material';

interface VirtualizedListProps<T> {
  items: T[];
  height?: number;
  itemHeight?: number;
  renderItem: (item: T, index: number) => React.ReactNode;
  onItemClick?: (item: T, index: number) => void;
  emptyMessage?: string;
}

/**
 * Virtualized List Component
 * Efficiently renders large lists by only rendering visible items
 * Use this for lists with 100+ items
 */
function VirtualizedList<T>({
  items,
  height = 400,
  itemHeight = 60,
  renderItem,
  onItemClick,
  emptyMessage = 'No items found'
}: VirtualizedListProps<T>) {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const item = items[index];
    if (!item) return null;

    return (
      <div style={style}>
        {onItemClick ? (
          <ListItemButton
            onClick={() => onItemClick(item, index)}
            sx={{
              transition: 'all 0.2s ease',
              '&:hover': {
                backgroundColor: alpha('#00d4ff', 0.1)
              }
            }}
          >
            {renderItem(item, index)}
          </ListItemButton>
        ) : (
          <ListItem>
            {renderItem(item, index)}
          </ListItem>
        )}
      </div>
    );
  };

  if (items.length === 0) {
    return (
      <Box
        sx={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'rgba(255, 255, 255, 0.5)'
        }}
      >
        {emptyMessage}
      </Box>
    );
  }

  return (
    <Box sx={{ height, overflow: 'hidden' }}>
      <List
        height={height}
        itemCount={items.length}
        itemSize={itemHeight}
        width="100%"
      >
        {Row}
      </List>
    </Box>
  );
}

export default VirtualizedList;

