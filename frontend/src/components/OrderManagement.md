# OrderManagement 组件

## 概述

OrderManagement 组件是一个功能完整的订单管理界面，允许用户查看、取消和修改交易订单。该组件支持模拟交易和实盘交易两种模式。

## 功能特性

### 📋 订单列表显示
- 显示所有订单的详细信息
- 支持订单状态可视化（待处理、已成交、已取消等）
- 实时更新订单状态
- 响应式表格设计

### ❌ 订单取消
- 一键取消待处理的订单
- 实时反馈操作结果
- 自动刷新订单列表

### ✏️ 订单修改
- 修改订单数量
- 调整限价
- 设置止损价
- 更改订单有效期
- 实时验证输入

### 🔄 实时刷新
- 手动刷新订单列表
- 自动更新订单状态
- 支持回调函数通知父组件

## 组件接口

### Props

```typescript

interface OrderManagementProps {
  mode?: 'paper' | 'live';  // 交易模式，默认为 'paper'
  onOrderUpdate?: () => void; // 订单更新回调函数
}

```

### 使用示例

```tsx

import OrderManagement from './components/OrderManagement';

function TradingDashboard() {
  const handleOrderUpdate = () => {
    // 处理订单更新后的逻辑
    console.log('订单已更新');
  };

  return (
    <div>
      <OrderManagement 
        mode="paper" 
        onOrderUpdate={handleOrderUpdate}
      />
    </div>
  );
}

```

## 订单服务

### OrderService 接口

```typescript

interface OrderService {
  getOrders(mode: 'paper' | 'live'): Promise<AlpacaOrder[]>;
  cancelOrder(orderId: string, mode: 'paper' | 'live'): Promise<void>;
  modifyOrder(orderId: string, modifiedOrder: Partial<AlpacaOrder>, mode: 'paper' | 'live'): Promise<void>;
}

```

### 服务方法

#### getOrders(mode)

获取指定模式下的所有订单

#### cancelOrder(orderId, mode)

取消指定ID的订单

#### modifyOrder(orderId, modifiedOrder, mode)

修改指定ID的订单

## 订单状态

组件支持以下订单状态：

- **pending**: 待处理 - 显示取消和修改按钮
- **pending_new**: 新订单待处理 - 显示取消和修改按钮
- **filled**: 已成交 - 只显示查看按钮
- **canceled**: 已取消 - 只显示查看按钮
- **其他状态**: 显示查看按钮

## 样式特性

- 使用 Material-UI 组件库
- 响应式设计，支持移动端
- 深色主题，符合交易平台风格
- 渐变背景和发光效果
- 动画过渡效果

## 错误处理

- 网络请求失败时显示错误提示
- 操作失败时提供用户友好的错误信息
- 自动重试机制
- 加载状态指示器

## 测试

组件包含完整的单元测试，覆盖以下场景：

- 组件渲染
- 订单列表显示
- 订单取消功能
- 订单修改功能
- 刷新功能
- 不同交易模式切换

运行测试：

```bash

npm test OrderManagement.test.tsx

```

## 集成

OrderManagement 组件已集成到 TradingDashboard 中，位于投资指导部分之前。组件会根据当前交易模式自动切换显示模拟交易或实盘交易的订单。

## 依赖

- React 18+
- Material-UI 5+
- notistack (用于通知)
- TypeScript

## 注意事项

1. 确保后端API支持订单的取消和修改操作
2. 订单修改功能仅对特定状态的订单可用
3. 组件会自动处理API错误和网络异常
4. 建议在生产环境中添加更多的错误边界处理

