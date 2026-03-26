/**
 * Storybook Stories for LoadingOverlay Component
 */

import type { Meta, StoryObj } from '@storybook/react';
import LoadingOverlay from './LoadingOverlay';
import { Box, Typography } from '@mui/material';

const meta: Meta<typeof LoadingOverlay> = {
  title: 'Components/Common/LoadingOverlay',
  component: LoadingOverlay,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'LoadingOverlay component displays a loading indicator with optional progress and message. Can be used as a full-screen overlay or within a container.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    open: {
      control: 'boolean',
      description: 'Whether the overlay is visible',
    },
    message: {
      control: 'text',
      description: 'Loading message to display',
    },
    progress: {
      control: { type: 'range', min: 0, max: 100, step: 1 },
      description: 'Progress percentage (0-100). If not provided, shows indeterminate progress.',
    },
  },
  decorators: [
    (Story: any) => (
      <Box sx={{ position: 'relative', width: '100vw', height: '100vh', bgcolor: '#1a1a1a' }}>
        <Box sx={{ p: 4 }}>
          <Typography variant="h4" sx={{ color: '#fff', mb: 2 }}>
            Sample Content
          </Typography>
          <Typography sx={{ color: '#888' }}>
            This is the content behind the loading overlay. When the overlay is open, this content will be obscured.
          </Typography>
        </Box>
        <Story />
      </Box>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof LoadingOverlay>;

// Default story - Indeterminate
export const Indeterminate: Story = {
  args: {
    open: true,
    message: 'Loading...',
  },
};

// With progress
export const WithProgress: Story = {
  args: {
    open: true,
    message: 'Loading data...',
    progress: 45,
  },
};

// Different progress values
export const Progress0: Story = {
  args: {
    open: true,
    message: 'Starting...',
    progress: 0,
  },
};

export const Progress50: Story = {
  args: {
    open: true,
    message: 'Halfway there...',
    progress: 50,
  },
};

export const Progress100: Story = {
  args: {
    open: true,
    message: 'Almost done...',
    progress: 100,
  },
};

// Custom messages
export const FetchingData: Story = {
  args: {
    open: true,
    message: 'Fetching market data...',
  },
};

export const ProcessingTrade: Story = {
  args: {
    open: true,
    message: 'Processing your trade...',
    progress: 75,
  },
};

export const SavingSettings: Story = {
  args: {
    open: true,
    message: 'Saving your settings...',
    progress: 90,
  },
};

// Closed state
export const Closed: Story = {
  args: {
    open: false,
    message: 'This should not be visible',
  },
};

// Interactive example
export const Interactive: Story = {
  args: {
    open: true,
    message: 'Loading...',
    progress: 30,
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive example. Toggle the controls to see different states.',
      },
    },
  },
};

