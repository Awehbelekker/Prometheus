/**
 * Storybook Stories for EmptyState Component
 */

import type { Meta, StoryObj } from '@storybook/react';
import EmptyState from './EmptyState';

const meta: Meta<typeof EmptyState> = {
  title: 'Components/Common/EmptyState',
  component: EmptyState,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'EmptyState component displays a message when there is no data to show. Supports 8 different variants with customizable actions.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['portfolio', 'trades', 'achievements', 'analytics', 'positions', 'notifications', 'users', 'custom'],
      description: 'The type of empty state to display',
    },
    title: {
      control: 'text',
      description: 'Custom title (only for custom variant)',
    },
    description: {
      control: 'text',
      description: 'Custom description (only for custom variant)',
    },
    actionText: {
      control: 'text',
      description: 'Text for the action button',
    },
    onAction: {
      action: 'clicked',
      description: 'Callback when action button is clicked',
    },
  },
};

export default meta;
type Story = StoryObj<typeof EmptyState>;

// Default story
export const Portfolio: Story = {
  args: {
    variant: 'portfolio',
  },
};

export const Trades: Story = {
  args: {
    variant: 'trades',
  },
};

export const Achievements: Story = {
  args: {
    variant: 'achievements',
  },
};

export const Analytics: Story = {
  args: {
    variant: 'analytics',
  },
};

export const Positions: Story = {
  args: {
    variant: 'positions',
  },
};

export const Notifications: Story = {
  args: {
    variant: 'notifications',
  },
};

export const Users: Story = {
  args: {
    variant: 'users',
  },
};

export const CustomWithAction: Story = {
  args: {
    variant: 'custom',
    title: 'No Data Available',
    description: 'There is currently no data to display. Try adjusting your filters or check back later.',
    actionText: 'Refresh Data',
    onAction: () => alert('Refresh clicked!'),
  },
};

export const CustomWithoutAction: Story = {
  args: {
    variant: 'custom',
    title: 'Coming Soon',
    description: 'This feature is currently under development and will be available soon.',
  },
};

// Interactive example
export const Interactive: Story = {
  args: {
    variant: 'portfolio',
    actionText: 'Get Started',
    onAction: () => console.log('Action clicked'),
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive example with a custom action button.',
      },
    },
  },
};

