import React from 'react';
import { Box, Tooltip, Typography, Chip } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';
import { useRealWorldIntelligence } from './RealWorldIntelligenceProvider';

const MarketIntelligenceIndicators: React.FC = () => {
  const { intelligence, lastUpdate } = useRealWorldIntelligence();

  if (!intelligence) return null;

  const getSentimentIcon = (sentiment: number) => {
    if (sentiment > 0.2) return <TrendingUpIcon sx={{ fontSize: 16, color: '#4caf50' }} />;
    if (sentiment < -0.2) return <TrendingDownIcon sx={{ fontSize: 16, color: '#f44336' }} />;
    return <TrendingFlatIcon sx={{ fontSize: 16, color: '#ff9800' }} />;
  };

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.2) return '#e8f5e9';
    if (sentiment < -0.2) return '#ffebee';
    return '#fff8e1';
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', mr: 2, gap: 1 }}>
      {/* Overall Market Sentiment */}
      <Tooltip title={`Overall Market Sentiment: ${intelligence.sentiment.overall.toFixed(2)} (Updated: ${new Date(lastUpdate).toLocaleTimeString()})`}>
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          backgroundColor: getSentimentColor(intelligence.sentiment.overall),
          borderRadius: '4px',
          padding: '2px 8px',
          gap: 0.5
        }}>
          {getSentimentIcon(intelligence.sentiment.overall)}
          <Typography variant="caption" sx={{ fontWeight: 'medium' }}>
            Sentiment: {(intelligence.sentiment.overall * 100).toFixed(0)}
          </Typography>
        </Box>
      </Tooltip>

      {/* Fear & Greed Index */}
      <Tooltip title={`Fear & Greed Index: ${intelligence.crypto.fearGreedIndex}`}>
        <Chip
          label={`F&G: ${intelligence.crypto.fearGreedIndex}`}
          size="small"
          color={
            intelligence.crypto.fearGreedIndex > 70 ? 'error' :
            intelligence.crypto.fearGreedIndex < 30 ? 'success' : 'warning'
          }
          variant="outlined"
        />
      </Tooltip>

      {/* Whale Activity */}
      {intelligence.crypto.whaleMovements.length > 0 && (
        <Tooltip title={`${intelligence.crypto.whaleMovements.length} whale movements detected`}>
          <Chip
            label={`Whales: ${intelligence.crypto.whaleMovements.length}`}
            size="small"
            color="secondary"
            variant="outlined"
          />
        </Tooltip>
      )}

      {/* Economic Alert */}
      {intelligence.economic.inflation > 0.05 && (
        <Tooltip title={`High inflation detected: ${(intelligence.economic.inflation * 100).toFixed(1)}%`}>
          <Chip
            label="⚠️ Inflation"
            size="small"
            color="warning"
            variant="filled"
          />
        </Tooltip>
      )}
    </Box>
  );
};

export default MarketIntelligenceIndicators;
