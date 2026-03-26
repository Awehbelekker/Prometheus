import React from 'react';

interface LabelProps {
  children: React.ReactNode;
  htmlFor?: string;
  className?: string;
}

export const Label: React.FC<LabelProps> = ({ children, htmlFor, className = '' }) => {
  return (
    <label 
      htmlFor={htmlFor}
      className={`block text-white text-sm mb-2 ${className}`}
    >
      {children}
    </label>
  );
}; 