/**
 * LanguageSwitcher Component
 * Dropdown to switch between supported languages
 */

import React, { useState } from 'react';
import {
  Box,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Typography
} from '@mui/material';
import { Language, Check } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { languages } from '../../i18n/config';

const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLanguageChange = (languageCode: string) => {
    i18n.changeLanguage(languageCode);
    handleClose();
  };

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];

  return (
    <>
      <IconButton
        onClick={handleClick}
        sx={{
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}
      >
        <Typography variant="body2" sx={{ fontSize: 20 }}>
          {currentLanguage.flag}
        </Typography>
        <Language />
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            background: 'rgba(26, 26, 26, 0.98)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 2,
            mt: 1,
            minWidth: 200
          }
        }}
      >
        {languages.map((language) => (
          <MenuItem
            key={language.code}
            onClick={() => handleLanguageChange(language.code)}
            selected={i18n.language === language.code}
            sx={{
              '&:hover': {
                bgcolor: 'rgba(0, 212, 255, 0.1)'
              },
              '&.Mui-selected': {
                bgcolor: 'rgba(0, 212, 255, 0.2)',
                '&:hover': {
                  bgcolor: 'rgba(0, 212, 255, 0.3)'
                }
              }
            }}
          >
            <ListItemIcon>
              <Typography variant="body1" sx={{ fontSize: 24 }}>
                {language.flag}
              </Typography>
            </ListItemIcon>
            <ListItemText>
              <Typography variant="body2" sx={{ color: '#fff' }}>
                {language.name}
              </Typography>
            </ListItemText>
            {i18n.language === language.code && (
              <Check sx={{ color: '#00d4ff', ml: 2 }} />
            )}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

export default LanguageSwitcher;

