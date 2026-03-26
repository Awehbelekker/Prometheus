/**
 * InfoTooltip Component
 * Contextual tooltip with helpful information
 */

import React from 'react';
import {
  Tooltip,
  IconButton,
  TooltipProps,
  styled
} from '@mui/material';
import { HelpOutline, Info } from '@mui/icons-material';

export interface InfoTooltipProps {
  title: string;
  description?: string;
  placement?: TooltipProps['placement'];
  icon?: 'help' | 'info';
  size?: 'small' | 'medium';
}

const StyledTooltip = styled(({ className, ...props }: TooltipProps) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(({ theme }) => ({
  '& .MuiTooltip-tooltip': {
    backgroundColor: 'rgba(26, 26, 26, 0.98)',
    border: '1px solid rgba(0, 212, 255, 0.3)',
    borderRadius: 8,
    padding: '12px 16px',
    maxWidth: 300,
    fontSize: 14,
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)'
  },
  '& .MuiTooltip-arrow': {
    color: 'rgba(26, 26, 26, 0.98)',
    '&::before': {
      border: '1px solid rgba(0, 212, 255, 0.3)'
    }
  }
}));

const InfoTooltip: React.FC<InfoTooltipProps> = ({
  title,
  description,
  placement = 'top',
  icon = 'help',
  size = 'small'
}) => {
  const tooltipContent = (
    <div>
      <div style={{ fontWeight: 600, marginBottom: description ? 8 : 0, color: '#00d4ff' }}>
        {title}
      </div>
      {description && (
        <div style={{ color: '#ccc', fontSize: 13 }}>
          {description}
        </div>
      )}
    </div>
  );

  return (
    <StyledTooltip
      title={tooltipContent}
      placement={placement}
      arrow
      enterDelay={200}
      leaveDelay={0}
    >
      <IconButton
        size={size}
        sx={{
          color: '#888',
          '&:hover': {
            color: '#00d4ff',
            backgroundColor: 'rgba(0, 212, 255, 0.1)'
          }
        }}
      >
        {icon === 'help' ? (
          <HelpOutline fontSize={size} />
        ) : (
          <Info fontSize={size} />
        )}
      </IconButton>
    </StyledTooltip>
  );
};

export default InfoTooltip;

