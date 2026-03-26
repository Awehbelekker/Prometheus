import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Tooltip,
  alpha,
  Stack,
  Divider
} from '@mui/material';
import {
  Cancel,
  Edit,
  Refresh,
  Visibility,
  CheckCircle,
  Error,
  Pending,
  AttachMoney,
  TrendingUp,
  TrendingDown
} from '@mui/icons-material';
import { AlpacaOrder } from '../services/RealAlpacaService';
import { orderService } from '../services/OrderService';
import { useSnackbar } from 'notistack';

interface OrderManagementProps {
  mode?: 'paper' | 'live';
  onOrderUpdate?: () => void;
}

interface ModifyOrderData {
  quantity?: number;
  limit_price?: number;
  stop_price?: number;
  time_in_force?: 'day' | 'gtc' | 'ioc' | 'fok';
}

const OrderManagement: React.FC<OrderManagementProps> = ({ 
  mode = 'paper', 
  onOrderUpdate 
}) => {
  const [orders, setOrders] = useState<AlpacaOrder[]>([]);
  const [loading, setLoading] = useState(false);
  const [modifyDialogOpen, setModifyDialogOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<AlpacaOrder | null>(null);
  const [modifyData, setModifyData] = useState<ModifyOrderData>({});
  const { enqueueSnackbar } = useSnackbar();

  // Fetch orders
  const fetchOrders = async () => {
    try {
      setLoading(true);
      const ordersData = await orderService.getOrders(mode);
      setOrders(ordersData);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
      enqueueSnackbar('Failed to fetch orders', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Cancel order
  const handleCancelOrder = async (orderId: string) => {
    try {
      setLoading(true);
      await orderService.cancelOrder(orderId, mode);
      enqueueSnackbar('Order cancelled', { variant: 'success' });
      await fetchOrders();
      onOrderUpdate?.();
    } catch (error) {
      console.error('Failed to cancel order:', error);
      enqueueSnackbar('Failed to cancel order', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Modify order
  const handleModifyOrder = async (orderId: string, modifiedOrder: ModifyOrderData) => {
    try {
      setLoading(true);
      await orderService.modifyOrder(orderId, modifiedOrder, mode);
      enqueueSnackbar('Order modified successfully', { variant: 'success' });
      setModifyDialogOpen(false);
      await fetchOrders();
      onOrderUpdate?.();
    } catch (error) {
      console.error('Failed to modify order:', error);
      enqueueSnackbar('Failed to modify order', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Open modify dialog
  const openModifyDialog = (order: AlpacaOrder) => {
    setSelectedOrder(order);
    setModifyData({
      quantity: order.qty,
      limit_price: order.limit_price,
      stop_price: order.stop_price,
      time_in_force: order.time_in_force as 'day' | 'gtc' | 'ioc' | 'fok'
    });
    setModifyDialogOpen(true);
  };

  // Get order status icon
  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'filled':
        return <CheckCircle color="success" />;
      case 'canceled':
        return <Cancel color="error" />;
      case 'pending':
      case 'pending_new':
        return <Pending color="warning" />;
      default:
        return <Error color="error" />;
    }
  };

  // Get order status color
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'filled':
        return 'success';
      case 'canceled':
        return 'error';
      case 'pending':
      case 'pending_new':
        return 'warning';
      default:
        return 'default';
    }
  };

  // Format price
  const formatPrice = (price: number | null) => {
    return price ? `$${price.toFixed(2)}` : 'N/A';
  };

  // Format time
  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleString();
  };

  useEffect(() => {
    fetchOrders();
  }, [mode]);

  return (
    <Box>
      <Card sx={{
        background: 'linear-gradient(135deg, rgba(26, 26, 46, 0.95) 0%, rgba(0, 212, 255, 0.05) 100%)',
        border: '2px solid rgba(0, 212, 255, 0.4)',
        borderRadius: 4,
        backdropFilter: 'blur(15px)',
        boxShadow: '0 8px 32px rgba(0, 212, 255, 0.2)'
      }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5" sx={{ color: '#00d4ff', fontWeight: 600 }}>
              📋 Order Management ({mode === 'paper' ? 'Paper' : 'Live'})
            </Typography>
            <Stack direction="row" spacing={2}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={fetchOrders}
                disabled={loading}
                sx={{
                  borderColor: '#00d4ff',
                  color: '#00d4ff',
                  '&:hover': {
                    borderColor: '#0099cc',
                    backgroundColor: alpha('#00d4ff', 0.15)
                  }
                }}
              >
                Refresh
              </Button>
            </Stack>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress sx={{ color: '#00d4ff' }} />
            </Box>
          ) : (
            <TableContainer component={Paper} sx={{
              backgroundColor: 'rgba(26, 26, 46, 0.8)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              borderRadius: 2
            }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Order ID</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Symbol</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Side</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Quantity</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Price</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Status</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Created At</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 600 }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {orders.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} sx={{ textAlign: 'center', color: '#666' }}>
                        No orders
                      </TableCell>
                    </TableRow>
                  ) : (
                    orders.map((order) => (
                      <TableRow key={order.id} hover>
                        <TableCell sx={{ color: '#fff' }}>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                            {order.id.slice(0, 8)}...
                          </Typography>
                        </TableCell>
                        <TableCell sx={{ color: '#fff', fontWeight: 600 }}>
                          {order.symbol}
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={order.side === 'buy' ? <TrendingUp /> : <TrendingDown />}
                            label={order.side === 'buy' ? 'Buy' : 'Sell'}
                            color={order.side === 'buy' ? 'success' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell sx={{ color: '#fff' }}>
                          {order.qty}
                        </TableCell>
                        <TableCell sx={{ color: '#fff' }}>
                          {formatPrice(order.limit_price)}
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={getStatusIcon(order.status)}
                            label={order.status}
                            color={getStatusColor(order.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell sx={{ color: '#fff' }}>
                          <Typography variant="body2">
                            {formatTime(order.created_at)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Stack direction="row" spacing={1}>
                            {order.status === 'pending' || order.status === 'pending_new' ? (
                              <>
                                <Tooltip title="Modify Order">
                                  <IconButton
                                    size="small"
                                    onClick={() => openModifyDialog(order)}
                                    sx={{ color: '#00d4ff' }}
                                  >
                                    <Edit />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Cancel Order">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleCancelOrder(order.id)}
                                    sx={{ color: '#f44336' }}
                                  >
                                    <Cancel />
                                  </IconButton>
                                </Tooltip>
                              </>
                            ) : (
                              <Tooltip title="View Details">
                                <IconButton size="small" sx={{ color: '#666' }}>
                                  <Visibility />
                                </IconButton>
                              </Tooltip>
                            )}
                          </Stack>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Modify Order Dialog */}
      <Dialog
        open={modifyDialogOpen}
        onClose={() => setModifyDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(26, 26, 46, 0.95)',
            border: '2px solid rgba(0, 212, 255, 0.4)',
            borderRadius: 4
          }
        }}
      >
        <DialogTitle sx={{ color: '#00d4ff', fontWeight: 600 }}>
          Modify Order - {selectedOrder?.symbol}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <TextField
              label="Quantity"
              type="number"
              value={modifyData.quantity || ''}
              onChange={(e) => setModifyData({ ...modifyData, quantity: Number(e.target.value) })}
              fullWidth
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: '#fff',
                  '& fieldset': { borderColor: '#00d4ff' },
                  '&:hover fieldset': { borderColor: '#0099cc' }
                },
                '& .MuiInputLabel-root': { color: '#00d4ff' }
              }}
            />
            
            <TextField
              label="Limit Price"
              type="number"
              value={modifyData.limit_price || ''}
              onChange={(e) => setModifyData({ ...modifyData, limit_price: Number(e.target.value) })}
              fullWidth
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: '#fff',
                  '& fieldset': { borderColor: '#00d4ff' },
                  '&:hover fieldset': { borderColor: '#0099cc' }
                },
                '& .MuiInputLabel-root': { color: '#00d4ff' }
              }}
            />
            
            <TextField
              label="Stop Price"
              type="number"
              value={modifyData.stop_price || ''}
              onChange={(e) => setModifyData({ ...modifyData, stop_price: Number(e.target.value) })}
              fullWidth
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: '#fff',
                  '& fieldset': { borderColor: '#00d4ff' },
                  '&:hover fieldset': { borderColor: '#0099cc' }
                },
                '& .MuiInputLabel-root': { color: '#00d4ff' }
              }}
            />
            
            <FormControl fullWidth>
              <InputLabel sx={{ color: '#00d4ff' }}>Time in Force</InputLabel>
              <Select
                value={modifyData.time_in_force || 'day'}
                onChange={(e) => setModifyData({ ...modifyData, time_in_force: e.target.value as any })}
                sx={{
                  color: '#fff',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#0099cc' }
                }}
              >
                <MenuItem value="day">Day</MenuItem>
                <MenuItem value="gtc">Good Till Canceled</MenuItem>
                <MenuItem value="ioc">Immediate or Cancel</MenuItem>
                <MenuItem value="fok">Fill or Kill</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setModifyDialogOpen(false)}
            sx={{ color: '#666' }}
            >
            Cancel
          </Button>
          <Button
            onClick={() => selectedOrder && handleModifyOrder(selectedOrder.id, modifyData)}
            disabled={loading}
            sx={{
              backgroundColor: '#00d4ff',
              color: '#000',
              fontWeight: 600,
              '&:hover': { backgroundColor: '#0099cc' }
            }}
          >
            {loading ? <CircularProgress size={20} /> : 'Confirm'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OrderManagement;
