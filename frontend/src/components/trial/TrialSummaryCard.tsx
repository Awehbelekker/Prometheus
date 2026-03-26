import React from 'react';
import { Card, CardContent, Typography, Box, LinearProgress, alpha } from '@mui/material';

interface TrialSummary {
  active: boolean;
  hours_remaining?: number;
  starting_capital?: number;
  ending_equity?: number;
  pnl?: number;
  return_pct?: number;
}

interface TrialSummaryCardProps {
  data?: TrialSummary | null;
}

const TrialSummaryCard: React.FC<TrialSummaryCardProps> = ({ data }) => {
  if (!data) return null;
  const { active, hours_remaining, starting_capital, ending_equity, pnl, return_pct } = data;
  const progress = typeof hours_remaining === 'number' ? Math.min(100, Math.max(0, (hours_remaining / 48) * 100)) : undefined;
  const pnlColor = (pnl ?? 0) >= 0 ? '#4caf50' : '#f44336';
  const pctColor = (return_pct ?? 0) >= 0 ? '#4caf50' : '#f44336';

  return (
    <Card sx={{
      mb: 3,
      backgroundColor: 'rgba(26,26,46,0.8)',
      border: '1px solid rgba(0, 212, 255, 0.3)'
    }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 1, color: '#00d4ff', fontWeight: 700 }}>
          48-Hour Trial Status
        </Typography>
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap', alignItems: 'center' }}>
          <Box>
            <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>STATUS</Typography>
            <Typography variant="subtitle1" sx={{ color: active ? '#4caf50' : '#aaa', fontWeight: 700 }}>
              {active ? 'Active' : 'Completed'}
            </Typography>
          </Box>
          {typeof hours_remaining === 'number' && (
            <Box sx={{ minWidth: 180 }}>
              <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>HOURS LEFT</Typography>
              <Typography variant="subtitle1" sx={{ color: hours_remaining < 12 ? '#f44336' : '#00d4ff', fontWeight: 700 }}>
                {hours_remaining.toFixed(1)}h
              </Typography>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: alpha('#333', 0.3),
                  '& .MuiLinearProgress-bar': { backgroundColor: hours_remaining < 12 ? '#f44336' : '#00d4ff' }
                }}
              />
            </Box>
          )}
          {typeof starting_capital === 'number' && (
            <Box>
              <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>START</Typography>
              <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>
                ${starting_capital.toLocaleString()}
              </Typography>
            </Box>
          )}
          {typeof ending_equity === 'number' && (
            <Box>
              <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>END</Typography>
              <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>
                ${ending_equity.toLocaleString()}
              </Typography>
            </Box>
          )}
          {typeof pnl === 'number' && (
            <Box>
              <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>PnL</Typography>
              <Typography variant="subtitle1" sx={{ color: pnlColor, fontWeight: 700 }}>
                {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
              </Typography>
            </Box>
          )}
          {typeof return_pct === 'number' && (
            <Box>
              <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>RETURN</Typography>
              <Typography variant="subtitle1" sx={{ color: pctColor, fontWeight: 700 }}>
                {return_pct >= 0 ? '+' : ''}{return_pct.toFixed(2)}%
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default TrialSummaryCard;
