import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SnackbarProvider } from 'notistack';
import OrderManagement from './OrderManagement';
import { orderService } from '../services/OrderService';

// Mock the order service
jest.mock('../services/OrderService', () => ({
  orderService: {
    getOrders: jest.fn(),
    cancelOrder: jest.fn(),
    modifyOrder: jest.fn(),
  },
}));

// Mock the API call
jest.mock('../config/api', () => ({
  apiCall: jest.fn(),
  API_ENDPOINTS: {
    ALPACA_PAPER_ORDERS: '/api/trading/alpaca/paper/orders',
    ALPACA_LIVE_ORDERS: '/api/trading/alpaca/live/orders',
  },
}));

const mockOrders = [
  {
    id: 'test-order-1',
    client_order_id: 'client-1',
    created_at: '2024-01-01T10:00:00Z',
    updated_at: '2024-01-01T10:00:00Z',
    submitted_at: '2024-01-01T10:00:00Z',
    filled_at: null,
    expired_at: null,
    canceled_at: null,
    failed_at: null,
    replaced_at: null,
    replaced_by: null,
    replaces: null,
    asset_id: 'test-asset',
    symbol: 'AAPL',
    asset_class: 'us_equity',
    notional: null,
    qty: '10',
    filled_qty: '0',
    filled_avg_price: null,
    order_class: 'simple',
    order_type: 'limit',
    type: 'limit',
    side: 'buy',
    time_in_force: 'day',
    limit_price: '150.00',
    stop_price: null,
    status: 'pending',
    extended_hours: false,
    legs: null,
    trail_percent: null,
    trail_price: null,
    hwm: null,
  },
  {
    id: 'test-order-2',
    client_order_id: 'client-2',
    created_at: '2024-01-01T11:00:00Z',
    updated_at: '2024-01-01T11:00:00Z',
    submitted_at: '2024-01-01T11:00:00Z',
    filled_at: '2024-01-01T11:30:00Z',
    expired_at: null,
    canceled_at: null,
    failed_at: null,
    replaced_at: null,
    replaced_by: null,
    replaces: null,
    asset_id: 'test-asset-2',
    symbol: 'GOOGL',
    asset_class: 'us_equity',
    notional: null,
    qty: '5',
    filled_qty: '5',
    filled_avg_price: '2800.00',
    order_class: 'simple',
    order_type: 'market',
    type: 'market',
    side: 'sell',
    time_in_force: 'day',
    limit_price: null,
    stop_price: null,
    status: 'filled',
    extended_hours: false,
    legs: null,
    trail_percent: null,
    trail_price: null,
    hwm: null,
  },
];

const renderWithSnackbar = (component: React.ReactElement) => {
  return render(
    <SnackbarProvider>
      {component}
    </SnackbarProvider>
  );
};

describe('OrderManagement Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders order management interface', async () => {
    (orderService.getOrders as jest.Mock).mockResolvedValue(mockOrders);
    
    renderWithSnackbar(<OrderManagement mode="paper" />);
    
    await waitFor(() => {
      expect(screen.getByText('📋 订单管理 (模拟)')).toBeInTheDocument();
    });
    
    expect(screen.getByText('AAPL')).toBeInTheDocument();
    expect(screen.getByText('GOOGL')).toBeInTheDocument();
  });

  it('displays orders in table format', async () => {
    (orderService.getOrders as jest.Mock).mockResolvedValue(mockOrders);
    
    renderWithSnackbar(<OrderManagement mode="paper" />);
    
    await waitFor(() => {
      expect(screen.getByText('订单ID')).toBeInTheDocument();
      expect(screen.getByText('股票代码')).toBeInTheDocument();
      expect(screen.getByText('方向')).toBeInTheDocument();
      expect(screen.getByText('数量')).toBeInTheDocument();
      expect(screen.getByText('价格')).toBeInTheDocument();
      expect(screen.getByText('状态')).toBeInTheDocument();
      expect(screen.getByText('创建时间')).toBeInTheDocument();
      expect(screen.getByText('操作')).toBeInTheDocument();
    });
  });

  it('shows cancel and modify buttons for pending orders', async () => {
    (orderService.getOrders as jest.Mock).mockResolvedValue(mockOrders);
    
    renderWithSnackbar(<OrderManagement mode="paper" />);
    
    await waitFor(() => {
      // Check for pending order actions
      const cancelButtons = screen.getAllByLabelText('取消订单');
      const modifyButtons = screen.getAllByLabelText('修改订单');
      
      expect(cancelButtons.length).toBeGreaterThan(0);
      expect(modifyButtons.length).toBeGreaterThan(0);
    });
  });

  it('handles order cancellation', async () => {
    (orderService.getOrders as jest.Mock).mockResolvedValue(mockOrders);
    (orderService.cancelOrder as jest.Mock).mockResolvedValue(undefined);
    
    renderWithSnackbar(<OrderManagement mode="paper" />);
    
    await waitFor(() => {
      const cancelButton = screen.getAllByLabelText('取消订单')[0];
      fireEvent.click(cancelButton);
    });
    
    await waitFor(() => {
      expect(orderService.cancelOrder).toHaveBeenCalledWith('test-order-1', 'paper');
    });
  });

  it('opens modify dialog when modify button is clicked', async () => {
    (orderService.getOrders as jest.Mock).mockResolvedValue(mockOrders);
    
    renderWithSnackbar(<OrderManagement mode="paper" />);
    
    await waitFor(() => {
      const modifyButton = screen.getAllByLabelText('修改订单')[0];
      fireEvent.click(modifyButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('修改订单 - AAPL')).toBeInTheDocument();
      expect(screen.getByLabelText('数量')).toBeInTheDocument();
      expect(screen.getByLabelText('限价')).toBeInTheDocument();
      expect(screen.getByLabelText('止损价')).toBeInTheDocument();
      expect(screen.getByLabelText('有效期')).toBeInTheDocument();
    });
  });

  it('handles order modification', async () => {
    (orderService.getOrders as jest.Mock).mockResolvedValue(mockOrders);
    (orderService.modifyOrder as jest.Mock).mockResolvedValue(undefined);
    
    renderWithSnackbar(<OrderManagement mode="paper" />);
    
    await waitFor(() => {
      const modifyButton = screen.getAllByLabelText('修改订单')[0];
      fireEvent.click(modifyButton);
    });
    
    await waitFor(() => {
      const quantityInput = screen.getByLabelText('数量');
      fireEvent.change(quantityInput, { target: { value: '20' } });
      
      const confirmButton = screen.getByText('确认修改');
      fireEvent.click(confirmButton);
    });
    
    await waitFor(() => {
      expect(orderService.modifyOrder).toHaveBeenCalledWith(
        'test-order-1',
        expect.objectContaining({ quantity: 20 }),
        'paper'
      );
    });
  });

  it('refreshes orders when refresh button is clicked', async () => {
    (orderService.getOrders as jest.Mock).mockResolvedValue(mockOrders);
    
    renderWithSnackbar(<OrderManagement mode="paper" />);
    
    await waitFor(() => {
      const refreshButton = screen.getByText('刷新');
      fireEvent.click(refreshButton);
    });
    
    await waitFor(() => {
      expect(orderService.getOrders).toHaveBeenCalledTimes(2); // Initial load + refresh
    });
  });

  it('handles different trading modes', async () => {
    (orderService.getOrders as jest.Mock).mockResolvedValue(mockOrders);
    
    const { rerender } = renderWithSnackbar(<OrderManagement mode="paper" />);
    
    await waitFor(() => {
      expect(screen.getByText('📋 订单管理 (模拟)')).toBeInTheDocument();
    });
    
    rerender(
      <SnackbarProvider>
        <OrderManagement mode="live" />
      </SnackbarProvider>
    );
    
    await waitFor(() => {
      expect(screen.getByText('📋 订单管理 (实盘)')).toBeInTheDocument();
    });
  });
});


