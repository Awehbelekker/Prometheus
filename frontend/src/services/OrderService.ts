import { apiCall, API_ENDPOINTS } from '../config/api';
import { AlpacaOrder } from './RealAlpacaService';

export interface OrderService {
  getOrders(mode: 'paper' | 'live'): Promise<AlpacaOrder[]>;
  cancelOrder(orderId: string, mode: 'paper' | 'live'): Promise<void>;
  modifyOrder(orderId: string, modifiedOrder: Partial<AlpacaOrder>, mode: 'paper' | 'live'): Promise<void>;
}

class OrderServiceImpl implements OrderService {
  async getOrders(mode: 'paper' | 'live'): Promise<AlpacaOrder[]> {
    try {
      const endpoint = mode === 'paper' 
        ? API_ENDPOINTS.ALPACA_PAPER_ORDERS 
        : API_ENDPOINTS.ALPACA_LIVE_ORDERS;
      
      const response = await apiCall(endpoint);
      return Array.isArray(response) ? response : response.orders || [];
    } catch (error) {
      console.error('获取订单失败:', error);
      throw error;
    }
  }

  async cancelOrder(orderId: string, mode: 'paper' | 'live'): Promise<void> {
    try {
      const endpoint = mode === 'paper' 
        ? `/api/trading/alpaca/paper/orders/${orderId}/cancel`
        : `/api/trading/alpaca/live/orders/${orderId}/cancel`;
      
      await apiCall(endpoint, { method: 'DELETE' });
    } catch (error) {
      console.error('取消订单失败:', error);
      throw error;
    }
  }

  async modifyOrder(orderId: string, modifiedOrder: Partial<AlpacaOrder>, mode: 'paper' | 'live'): Promise<void> {
    try {
      const endpoint = mode === 'paper' 
        ? `/api/trading/alpaca/paper/orders/${orderId}`
        : `/api/trading/alpaca/live/orders/${orderId}`;
      
      await apiCall(endpoint, { 
        method: 'PATCH',
        body: JSON.stringify(modifiedOrder)
      });
    } catch (error) {
      console.error('修改订单失败:', error);
      throw error;
    }
  }
}

export const orderService = new OrderServiceImpl();


