import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Breadcrumbs, Typography, Box } from '@mui/material';
import { NavigateNext as NavigateNextIcon } from '@mui/icons-material';
import './Navigation.css';

interface NavigationProps {
  title?: string;
}

const Navigation: React.FC<NavigationProps> = ({ title }) => {
  const location = useLocation();
  
  const getBreadcrumbs = () => {
    const pathnames = location.pathname.split('/').filter((x) => x);
    const breadcrumbs = pathnames.map((value, index) => {
      const to = `/${pathnames.slice(0, index + 1).join('/')}`;
      const label = value
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
      
      return { to, label };
    });
    
    return breadcrumbs;
  };

  const breadcrumbs = getBreadcrumbs();

  return (
    <Box sx={{ p: 2, backgroundColor: 'background.paper', borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
      <Breadcrumbs 
        separator={<NavigateNextIcon fontSize="small" />}
        aria-label="breadcrumb"
        sx={{ color: 'text.secondary' }}
      >
        <Link to="/" className="nav-link">
          Home
        </Link>
        {breadcrumbs.map((breadcrumb, index) => {
          const isLast = index === breadcrumbs.length - 1;
          return isLast ? (
            <Typography key={breadcrumb.to} color="text.primary">
              {breadcrumb.label}
            </Typography>
          ) : (
            <Link
              key={breadcrumb.to}
              to={breadcrumb.to}
              className="nav-link"
            >
              {breadcrumb.label}
            </Link>
          );
        })}
      </Breadcrumbs>
      {title && (
        <Typography variant="h4" sx={{ mt: 1, color: 'text.primary' }}>
          {title}
        </Typography>
      )}
    </Box>
  );
};

export default Navigation; 