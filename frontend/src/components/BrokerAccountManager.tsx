import React, { useState, useEffect } from 'react';
import { Box, Card, CardContent, Typography, Button, TextField, Select, MenuItem, InputLabel, FormControl, Alert } from '@mui/material';
import { getApiUrl, API_ENDPOINTS, apiCall } from '../config/api';
import './BrokerAccountManager.css';

interface BrokerCredential {
  id?: string;
  broker: string;
  apiKey: string;
  apiSecret: string;
  accountName?: string;
  status?: string;
}

const BROKER_OPTIONS = [
  { value: 'alpaca', label: 'Alpaca' },
  { value: 'ibkr', label: 'Interactive Brokers' },
  { value: 'binance', label: 'Binance' },
  { value: 'other', label: 'Other' },
];

const BrokerAccountManager: React.FC = () => {
  const [credentials, setCredentials] = useState<BrokerCredential[]>([]);
  const [form, setForm] = useState<BrokerCredential>({ broker: '', apiKey: '', apiSecret: '', accountName: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    // Fetch existing broker credentials from backend
    const fetchCredentials = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('auth_token');
        const data = await apiCall(API_ENDPOINTS.BROKER_CREDENTIALS, {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined
        });
        setCredentials(data.credentials || []);
      } catch (e: any) {
        setError(e.message || 'Error fetching broker credentials');
      } finally {
        setLoading(false);
      }
    };
    fetchCredentials();
  }, []);

  const handleInputChange = (field: keyof BrokerCredential, value: string) => {
    setForm({ ...form, [field]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const token = localStorage.getItem('auth_token');
      const data = await apiCall(API_ENDPOINTS.BROKER_CREDENTIALS, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        body: JSON.stringify(form)
      });
      setSuccess('Broker credentials saved successfully!');
      setForm({ broker: '', apiKey: '', apiSecret: '', accountName: '' });
      // Refresh credentials list
      setCredentials(data.credentials || []);
    } catch (e: any) {
      setError(e.message || 'Error saving broker credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 4, maxWidth: 600, margin: '0 auto' }}>
      <Card sx={{ background: '#23272e', color: '#fff', mb: 3 }}>
        <CardContent>
          <Typography variant="h5" sx={{ mb: 2 }}>
            Broker Account Management
          </Typography>
          <form onSubmit={handleSubmit}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="broker-label" sx={{ color: '#b0b5bd' }}>Broker</InputLabel>
              <Select
                labelId="broker-label"
                value={form.broker}
                label="Broker"
                onChange={e => handleInputChange('broker', e.target.value)}
                required
                sx={{ color: '#fff', background: '#282c34' }}
              >
                {BROKER_OPTIONS.map(opt => (
                  <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Account Name (optional)"
              value={form.accountName}
              onChange={e => handleInputChange('accountName', e.target.value)}
              fullWidth
              sx={{ mb: 2, input: { color: '#fff', background: '#282c34' } }}
            />
            <TextField
              label="API Key"
              value={form.apiKey}
              onChange={e => handleInputChange('apiKey', e.target.value)}
              fullWidth
              required
              sx={{ mb: 2, input: { color: '#fff', background: '#282c34' } }}
            />
            <TextField
              label="API Secret"
              value={form.apiSecret}
              onChange={e => handleInputChange('apiSecret', e.target.value)}
              fullWidth
              required
              type="password"
              sx={{ mb: 2, input: { color: '#fff', background: '#282c34' } }}
            />
            <Button type="submit" variant="contained" color="primary" disabled={loading} fullWidth>
              {loading ? 'Saving...' : 'Save Broker Credentials'}
            </Button>
            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
            {success && <Alert severity="success" sx={{ mt: 2 }}>{success}</Alert>}
          </form>
        </CardContent>
      </Card>
      <Card sx={{ background: '#23272e', color: '#fff' }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 1 }}>
            Connected Broker Accounts
          </Typography>
          {credentials.length === 0 ? (
            <Typography>No broker accounts connected yet.</Typography>
          ) : (
            <ul>
              {credentials.map((cred, idx) => (
                <li key={cred.id || idx}>
                  <strong>{cred.accountName || cred.broker}</strong> ({cred.broker}) - <span className={cred.status === 'connected' ? 'status-connected' : 'status-disconnected'}>{cred.status || 'pending'}</span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default BrokerAccountManager;
