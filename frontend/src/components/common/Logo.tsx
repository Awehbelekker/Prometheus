import React from 'react';
import './Logo.css';

interface LogoProps {
  size?: 'small' | 'medium' | 'large';
  className?: string;
  theme?: 'dark' | 'light';
}

const Logo: React.FC<LogoProps> = ({ size = 'medium', className = '', theme = 'dark' }) => {
  const getSizeValue = () => {
    switch (size) {
      case 'small': return 40;
      case 'large': return 96;
      default: return 64;
    }
  };

  const logoSize = getSizeValue();
  const logoSrc = '/LogoNew.png'; // Use new PROMETHEUS flame logo

  return (
    <div className={`logo-container logo-${size} ${theme === 'dark' ? 'logo-dark' : 'logo-light'} ${className}`}>
      <img
        src={logoSrc}
        alt="PROMETHEUS NeuroForge™ Logo"
        width={logoSize}
        height={logoSize}
        className="logo-image"
        style={{
          background: 'transparent',
          backgroundColor: 'transparent'
        }}
      />
    </div>
  );
};

export default Logo; 