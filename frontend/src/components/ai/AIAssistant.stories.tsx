/**
 * Storybook Stories for AIAssistant Component
 */

import type { Meta, StoryObj } from '@storybook/react';
import AIAssistant from './AIAssistant';

const meta: Meta<typeof AIAssistant> = {
  title: 'Components/AI/AIAssistant',
  component: AIAssistant,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'AI Assistant component provides an interactive chat interface for users to get trading insights, ask questions, and receive AI-powered recommendations. Features include suggestion chips, conversation history, and real-time responses.',
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
      <div style={{ height: '100vh', position: 'relative' }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof AIAssistant>;

// Default story
export const Default: Story = {};

// With description
export const WithDescription: Story = {
  parameters: {
    docs: {
      description: {
        story: 'The AI Assistant appears as a floating action button (FAB) in the bottom-right corner. Click it to open the chat interface and interact with the AI.',
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
    docs: {
      description: {
        story: 'On mobile devices, the AI Assistant chat takes up the full screen for better usability.',
      },
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

