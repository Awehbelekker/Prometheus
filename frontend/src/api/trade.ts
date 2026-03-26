import { apiCall } from '../config/api';

export async function executeTrade(tradeData: any) {
  const result = await apiCall('/api/trade', {
    method: 'POST',
    body: JSON.stringify(tradeData),
  });
  return result;
}