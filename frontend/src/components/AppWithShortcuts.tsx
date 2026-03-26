import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import KeyboardShortcuts, { useKeyboardShortcuts } from './common/KeyboardShortcuts';
import GlobalSearch from './common/GlobalSearch';

/**
 * Wrapper component to add keyboard shortcuts and global search to App
 * This is needed because useNavigate must be used within BrowserRouter
 */
export const AppWithShortcuts: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const { shortcutsOpen, setShortcutsOpen } = useKeyboardShortcuts();
  const [searchOpen, setSearchOpen] = useState(false);

  return (
    <>
      {children}
      <KeyboardShortcuts 
        open={shortcutsOpen} 
        onClose={() => setShortcutsOpen(false)} 
      />
      <GlobalSearch 
        open={searchOpen} 
        onClose={() => setSearchOpen(false)}
        onNavigate={(path) => {
          navigate(path);
          setSearchOpen(false);
        }}
      />
    </>
  );
};

