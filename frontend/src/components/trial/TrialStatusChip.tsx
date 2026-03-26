import React from 'react';
import { Chip } from '@mui/material';

interface TrialStatusChipProps {
  hoursRemaining?: number;
  active?: boolean;
}

const TrialStatusChip: React.FC<TrialStatusChipProps> = ({ hoursRemaining, active }) => {
  if (active === false) return null;
  const hrs = typeof hoursRemaining === 'number' ? hoursRemaining : undefined;
  const color = hrs !== undefined && hrs < 12 ? 'error' : 'info';
  const label = hrs !== undefined ? `${hrs.toFixed(1)}h left` : 'Trial Active';
  return (
    <Chip
      size="small"
      label={label}
      color={color as any}
      sx={{ fontWeight: 700, ml: 1 }}
    />
  );
};

export default TrialStatusChip;
