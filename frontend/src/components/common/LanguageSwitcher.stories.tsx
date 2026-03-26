/**
 * Storybook Stories for LanguageSwitcher Component
 */

import type { Meta, StoryObj } from '@storybook/react';
import LanguageSwitcher from './LanguageSwitcher';
import { I18nextProvider } from 'react-i18next';
import i18n from 'i18next';

// Initialize i18n for Storybook
i18n.init({
  lng: 'en',
  fallbackLng: 'en',
  resources: {
    en: { translation: { welcome: 'Welcome' } },
    es: { translation: { welcome: 'Bienvenido' } },
    fr: { translation: { welcome: 'Bienvenue' } },
    de: { translation: { welcome: 'Willkommen' } },
    zh: { translation: { welcome: '欢迎' } },
    ja: { translation: { welcome: 'ようこそ' } },
  },
});

const meta: Meta<typeof LanguageSwitcher> = {
  title: 'Components/Common/LanguageSwitcher',
  component: LanguageSwitcher,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'LanguageSwitcher component allows users to change the application language. Supports 6 languages: English, Spanish, French, German, Chinese, and Japanese. The selected language is persisted across sessions.',
      },
    },
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#1a1a1a' },
      ],
    },
  },
  tags: ['autodocs'],
  decorators: [
    (Story: any) => (
      <I18nextProvider i18n={i18n}>
        <div style={{ padding: '20px' }}>
          <Story />
        </div>
      </I18nextProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof LanguageSwitcher>;

// Default story
export const Default: Story = {};

// English
export const English: Story = {
  decorators: [
    (Story: any) => {
      i18n.changeLanguage('en');
      return (
        <I18nextProvider i18n={i18n}>
          <Story />
        </I18nextProvider>
      );
    },
  ],
};

// Spanish
export const Spanish: Story = {
  decorators: [
    (Story: any) => {
      i18n.changeLanguage('es');
      return (
        <I18nextProvider i18n={i18n}>
          <Story />
        </I18nextProvider>
      );
    },
  ],
};

// French
export const French: Story = {
  decorators: [
    (Story: any) => {
      i18n.changeLanguage('fr');
      return (
        <I18nextProvider i18n={i18n}>
          <Story />
        </I18nextProvider>
      );
    },
  ],
};

// German
export const German: Story = {
  decorators: [
    (Story: any) => {
      i18n.changeLanguage('de');
      return (
        <I18nextProvider i18n={i18n}>
          <Story />
        </I18nextProvider>
      );
    },
  ],
};

// Chinese
export const Chinese: Story = {
  decorators: [
    (Story: any) => {
      i18n.changeLanguage('zh');
      return (
        <I18nextProvider i18n={i18n}>
          <Story />
        </I18nextProvider>
      );
    },
  ],
};

// Japanese
export const Japanese: Story = {
  decorators: [
    (Story: any) => {
      i18n.changeLanguage('ja');
      return (
        <I18nextProvider i18n={i18n}>
          <Story />
        </I18nextProvider>
      );
    },
  ],
};

// Interactive
export const Interactive: Story = {
  parameters: {
    docs: {
      description: {
        story: 'Click the language switcher to see all available languages. The current language is indicated with a checkmark.',
      },
    },
  },
};

