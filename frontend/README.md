# Prometheus Trading Platform Frontend

A sophisticated, production-ready React/TypeScript trading platform frontend with comprehensive features for AI-powered trading, portfolio management, and real-time market data.

## 🚀 Features

### Core Features
- **Authentication & Authorization** - JWT-based auth with role-based access control
- **User Dashboard** - Portfolio tracking, gamification, and social features
- **Trading Dashboard** - Dual-mode (paper/live) trading interface
- **Admin Cockpit** - Comprehensive admin interface with system monitoring
- **Real-Time Updates** - WebSocket connections for live data
- **Gamification** - XP, levels, achievements, and leaderboards
- **Responsive Design** - Mobile-friendly interface

### Advanced Features
- **Revolutionary AI Panels** - Monitor 5 AI trading engines
- **Hierarchical Agent Monitoring** - Track 17 trading agents
- **Analytics Dashboards** - Performance metrics and reporting
- **Order Management** - Complete order lifecycle management
- **Risk Engine** - Risk controls and monitoring
- **Social Trading** - Leaderboards and social features

## 📋 Prerequisites

- Node.js 16+ and npm/yarn
- Backend API running on `http://localhost:8000` (or configured via `REACT_APP_API_URL`)

## 🛠️ Installation

```bash

# Install dependencies

npm install

# Start development server

npm start

```

The app will open at `http://localhost:3000`

## 📜 Available Scripts

### Development
- `npm start` - Start development server
- `npm test` - Run tests
- `npm run test:a11y` - Run accessibility tests
- `npm run storybook` - Start Storybook component library

### Production
- `npm run build` - Build for production
- `npm run analyze` - Analyze bundle size

### Testing
- `npm test` - Run unit tests
- `npm run test:full` - Run all tests including accessibility

### AI/ML
- `npm run ai:status` - Check AI system status
- `npm run ai:validate` - Validate AI models
- `npm run ai:benchmark` - Run AI benchmarks

## 🏗️ Project Structure

```
```text
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── admin/          # Admin-specific components
│   │   ├── unified/        # Unified UI components
│   │   ├── ai/             # AI-related components
│   │   ├── analytics/      # Analytics components
│   │   ├── common/         # Shared components
│   │   ├── portfolio/      # Portfolio components
│   │   └── social/         # Social features
│   ├── services/           # API services
│   ├── hooks/              # Custom React hooks
│   ├── config/             # Configuration files
│   ├── contexts/           # React contexts
│   ├── routes/             # Route definitions
│   ├── theme/              # Theme configuration
│   ├── utils/              # Utility functions
│   └── App.tsx             # Main application
├── public/                 # Static assets
├── build/                  # Production build
└── package.json

```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env

REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

```

### API Configuration

API endpoints are configured in `src/config/api.ts`. The frontend automatically:

- Includes JWT tokens in requests
- Handles authentication errors
- Provides fallback mechanisms

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference.

## 🎨 Technology Stack

### Core
- **React 18.2.0** - UI library
- **TypeScript 4.9.5** - Type safety
- **Material-UI 5.17.1** - Component library
- **React Router 6.30.1** - Routing

### State Management
- **TanStack React Query 5.90.2** - Server state
- **Zustand 5.0.8** - Client state (available)
- **React Context** - Global state

### Data Visualization
- **Chart.js 4.5.0** - Charts
- **Recharts 2.8.0** - React charts
- **MUI X Charts** - Advanced charts

### Development Tools
- **Playwright** - E2E testing
- **Storybook** - Component documentation
- **Testing Library** - Unit testing
- **Webpack Bundle Analyzer** - Bundle analysis

## 🔐 Authentication

The app uses JWT-based authentication:

1. User logs in via `/login`
2. Token stored in `localStorage`
3. Token automatically included in API requests
4. Session restored on page reload

### Roles
- **User** - Standard trading access
- **Admin** - Full system access including admin cockpit

## 📡 API Integration

All API calls go through centralized service layer:

```typescript

import { apiCall } from './config/api';

// Example API call
const data = await apiCall('/api/user/portfolio/123');

```

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference.

## 🔄 Real-Time Updates

WebSocket connections provide real-time updates:

- Portfolio updates
- Order status changes
- System health metrics
- Agent status updates

WebSocket connections automatically reconnect on disconnect.

## 🎮 Gamification

Users earn XP and achievements through:

- Completing trades
- Maintaining win streaks
- Reaching milestones
- Learning from Trading Academy

## 📱 Responsive Design

The app is fully responsive:

- Desktop (1920px+)
- Tablet (768px - 1919px)
- Mobile (320px - 767px)

## ♿ Accessibility

- WCAG 2.1 AA compliant
- Keyboard navigation
- Screen reader support
- Reduced motion support
- High contrast mode

## 🧪 Testing

```bash

# Run all tests

npm test

# Run accessibility tests

npm run test:a11y

# Run E2E tests

npx playwright test

```

## 📦 Building for Production

```bash

# Build production bundle

npm run build

# Analyze bundle size

npm run analyze

```

Build output is in the `build/` directory.

## 🐛 Debugging

### Development Mode
- React DevTools recommended
- React Query DevTools available
- Console logging enabled

### Production Mode
- Error boundaries catch errors
- Logger utility for structured logging
- Ready for error monitoring service integration

## 📚 Documentation

- [API Documentation](./API_DOCUMENTATION.md) - Complete API reference
- [Frontend Improvements](./FRONTEND_IMPROVEMENTS.md) - Recent improvements
- [Routing Guide](./ROUTING_GUIDE.md) - Routing documentation

## 🔒 Security

- JWT token authentication
- Protected routes
- Role-based access control
- XSS protection
- CSRF protection ready

## 🚀 Deployment

### Build

```bash

npm run build

```

### Docker

```bash

docker build -f Dockerfile.frontend -t prometheus-frontend .

```

### Static Hosting

The `build/` directory can be served by any static file server:

- Nginx
- Apache
- Cloudflare Pages
- Vercel
- Netlify

## 🤝 Contributing

1. Follow TypeScript best practices
2. Use the logger utility instead of console.log
3. Write tests for new features
4. Update documentation
5. Follow existing code style

## 📝 Code Style

- TypeScript strict mode
- ESLint configuration
- Prettier formatting (recommended)
- Component-based architecture
- Custom hooks for reusable logic

## 🐛 Known Issues

See [FRONTEND_IMPROVEMENTS.md](./FRONTEND_IMPROVEMENTS.md) for known issues and planned improvements.

## 📄 License

Proprietary - Prometheus Trading Platform

## 🆘 Support

For issues or questions:

1. Check [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
2. Review [FRONTEND_IMPROVEMENTS.md](./FRONTEND_IMPROVEMENTS.md)
3. Check console for error messages
4. Verify backend API is running

---

**Version:** 2.0.0  
**Last Updated:** 2025-01-15
