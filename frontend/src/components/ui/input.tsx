import React from 'react';

interface InputProps {
  type?: string;
  value?: string | number;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  className?: string;
  id?: string;
  name?: string;
  disabled?: boolean;
}

export const Input: React.FC<InputProps> = ({ 
  type = 'text',
  value,
  onChange,
  placeholder,
  className = '',
  id,
  name,
  disabled = false
}) => {
  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      id={id}
      name={name}
      disabled={disabled}
      className={`w-full p-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:border-orange-400 focus:outline-none ${className}`}
    />
  );
}; 