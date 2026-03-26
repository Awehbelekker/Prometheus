import React from 'react';

interface SelectProps {
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  children: React.ReactNode;
  className?: string;
  id?: string;
  name?: string;
  disabled?: boolean;
}

interface SelectContentProps {
  children: React.ReactNode;
}

interface SelectItemProps {
  value: string;
  children: React.ReactNode;
}

interface SelectTriggerProps {
  children: React.ReactNode;
  className?: string;
}

interface SelectValueProps {
  placeholder?: string;
}

export const Select: React.FC<SelectProps> = ({ 
  value, 
  onChange, 
  children, 
  className = '',
  id,
  name,
  disabled = false
}) => {
  return (
    <select
      value={value}
      onChange={onChange}
      id={id}
      name={name}
      disabled={disabled}
      className={`w-full p-3 rounded-lg bg-white/10 border border-white/20 text-white focus:border-orange-400 focus:outline-none ${className}`}
    >
      {children}
    </select>
  );
};

export const SelectContent: React.FC<SelectContentProps> = ({ children }) => {
  return <>{children}</>;
};

export const SelectItem: React.FC<SelectItemProps> = ({ value, children }) => {
  return (
    <option value={value}>
      {children}
    </option>
  );
};

export const SelectTrigger: React.FC<SelectTriggerProps> = ({ children, className = '' }) => {
  return (
    <div className={`w-full p-3 rounded-lg bg-white/10 border border-white/20 text-white focus:border-orange-400 focus:outline-none ${className}`}>
      {children}
    </div>
  );
};

export const SelectValue: React.FC<SelectValueProps> = ({ placeholder }) => {
  return <span className="text-white/50">{placeholder}</span>;
}; 