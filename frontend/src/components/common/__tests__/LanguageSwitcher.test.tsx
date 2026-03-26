/**
 * Tests for LanguageSwitcher component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LanguageSwitcher from '../LanguageSwitcher';
import { I18nextProvider } from 'react-i18next';
import i18n from 'i18next';

// Mock i18n
jest.mock('../../../i18n/config', () => ({
  languages: [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' }
  ]
}));

// Initialize i18n for testing
i18n.init({
  lng: 'en',
  fallbackLng: 'en',
  resources: {
    en: { translation: {} },
    es: { translation: {} },
    fr: { translation: {} }
  }
});

const renderWithI18n = (component: React.ReactElement) => {
  return render(
    <I18nextProvider i18n={i18n}>
      {component}
    </I18nextProvider>
  );
};

describe('LanguageSwitcher', () => {
  it('should render language switcher button', () => {
    renderWithI18n(<LanguageSwitcher />);
    
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  it('should display current language flag', () => {
    renderWithI18n(<LanguageSwitcher />);
    
    expect(screen.getByText('🇺🇸')).toBeInTheDocument();
  });

  it('should open menu when button is clicked', async () => {
    renderWithI18n(<LanguageSwitcher />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText('English')).toBeInTheDocument();
      expect(screen.getByText('Español')).toBeInTheDocument();
      expect(screen.getByText('Français')).toBeInTheDocument();
    });
  });

  it('should change language when menu item is clicked', async () => {
    const changeLanguageSpy = jest.spyOn(i18n, 'changeLanguage');
    
    renderWithI18n(<LanguageSwitcher />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    await waitFor(() => {
      const spanishOption = screen.getByText('Español');
      fireEvent.click(spanishOption);
    });
    
    expect(changeLanguageSpy).toHaveBeenCalledWith('es');
  });

  it('should close menu after language selection', async () => {
    renderWithI18n(<LanguageSwitcher />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    await waitFor(() => {
      const spanishOption = screen.getByText('Español');
      fireEvent.click(spanishOption);
    });
    
    await waitFor(() => {
      expect(screen.queryByText('English')).not.toBeInTheDocument();
    });
  });

  it('should show check mark for current language', async () => {
    renderWithI18n(<LanguageSwitcher />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      const menuItems = screen.getAllByRole('menuitem');
      // Check that at least one menu item has the selected class
      const selectedItem = menuItems.find(item => item.classList.contains('Mui-selected'));
      expect(selectedItem).toBeTruthy();
    });
  });

  it('should display all language flags', async () => {
    renderWithI18n(<LanguageSwitcher />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      // Use getAllByText since flags appear multiple times (button + menu)
      const usFlags = screen.getAllByText('🇺🇸');
      const esFlags = screen.getAllByText('🇪🇸');
      const frFlags = screen.getAllByText('🇫🇷');
      expect(usFlags.length).toBeGreaterThan(0);
      expect(esFlags.length).toBeGreaterThan(0);
      expect(frFlags.length).toBeGreaterThan(0);
    });
  });
});

