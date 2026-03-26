/**
 * Storybook Stories for Leaderboard Component
 */

import type { Meta, StoryObj } from '@storybook/react';
import Leaderboard from './Leaderboard';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const meta: Meta<typeof Leaderboard> = {
  title: 'Components/Social/Leaderboard',
  component: Leaderboard,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Leaderboard component displays rankings of users based on different metrics (XP, Returns, Win Rate, Streak). Features real-time updates and interactive tabs.',
      },
    },
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#0a0a0a' },
      ],
    },
  },
  tags: ['autodocs'],
  decorators: [
    (Story: any) => (
      <QueryClientProvider client={queryClient}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <Story />
        </div>
      </QueryClientProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof Leaderboard>;

// Default story
export const Default: Story = {};

// With description
export const WithDescription: Story = {
  parameters: {
    docs: {
      description: {
        story: 'The leaderboard shows top performers across different categories. Users can switch between XP, Returns, Win Rate, and Streak rankings.',
      },
    },
  },
};

// Mobile view
export const Mobile: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'mobile1',
    },
  },
};

// Tablet view
export const Tablet: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'tablet',
    },
  },
};

