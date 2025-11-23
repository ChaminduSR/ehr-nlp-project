import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'error' | 'draft';
  size?: 'default' | 'large';
  fullWidth?: boolean;
  children: React.ReactNode;
}

export function Button({ 
  variant = 'primary', 
  size = 'default',
  fullWidth = false,
  children, 
  className = '', 
  disabled = false,
  ...props 
}: ButtonProps) {
  const baseStyles = "inline-flex items-center justify-center border-2 cursor-pointer transition-colors duration-100";
  const heightStyle = size === 'large' ? 'h-14' : 'h-12'; // 48px minimum, 56px large
  const widthStyle = fullWidth ? 'w-full' : '';
  const paddingStyle = 'px-6';
  const borderRadius = 'rounded';
  
  const variantStyles = {
    primary: disabled 
      ? 'bg-gray-300 text-gray-600 border-gray-300 cursor-not-allowed'
      : 'bg-[#0066CC] text-white border-[#0066CC] hover:bg-[#004C99] hover:border-[#004C99]',
    secondary: disabled
      ? 'bg-gray-300 text-gray-600 border-gray-300 cursor-not-allowed'
      : 'bg-white text-black border-[#CCCCCC] hover:bg-[#F5F5F5]',
    success: disabled
      ? 'bg-gray-300 text-gray-600 border-gray-300 cursor-not-allowed'
      : 'bg-[#00AA00] text-white border-[#00AA00] hover:bg-[#008800]',
    error: disabled
      ? 'bg-gray-300 text-gray-600 border-gray-300 cursor-not-allowed'
      : 'bg-[#CC0000] text-white border-[#CC0000] hover:bg-[#990000]',
    draft: disabled
      ? 'bg-gray-300 text-gray-600 border-gray-300 cursor-not-allowed'
      : 'bg-[#FF9900] text-white border-[#FF9900] hover:bg-[#CC7700]',
  };
  
  return (
    <button
      className={`${baseStyles} ${heightStyle} ${widthStyle} ${paddingStyle} ${borderRadius} ${variantStyles[variant]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
