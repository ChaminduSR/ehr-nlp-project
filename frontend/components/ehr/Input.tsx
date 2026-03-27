import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export function Input({ label, error, helperText, className = '', ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-2 w-full">
      {label && (
        <label htmlFor={props.id} className="block">
          {label}
        </label>
      )}
      <input
        className={`h-12 px-4 border-2 border-[#CCCCCC] rounded bg-white text-black w-full
          focus:border-[#0066CC] focus:outline-none
          disabled:bg-gray-200 disabled:text-gray-600 disabled:cursor-not-allowed
          ${error ? 'border-[#CC0000]' : ''}
          ${className}`}
        {...props}
      />
      {error && <p className="text-[#CC0000] text-sm">{error}</p>}
      {helperText && !error && <p className="text-[#333333] text-sm">{helperText}</p>}
    </div>
  );
}

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export function Textarea({ label, error, helperText, className = '', ...props }: TextareaProps) {
  return (
    <div className="flex flex-col gap-2 w-full">
      {label && (
        <label htmlFor={props.id} className="block">
          {label}
        </label>
      )}
      <textarea
        className={`min-h-32 p-4 border-2 border-[#CCCCCC] rounded bg-white text-black w-full
          focus:border-[#0066CC] focus:outline-none
          disabled:bg-gray-200 disabled:text-gray-600 disabled:cursor-not-allowed
          ${error ? 'border-[#CC0000]' : ''}
          ${className}`}
        {...props}
      />
      {error && <p className="text-[#CC0000] text-sm">{error}</p>}
      {helperText && !error && <p className="text-[#333333] text-sm">{helperText}</p>}
    </div>
  );
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: { value: string; label: string }[];
}

export function Select({ label, error, options, className = '', ...props }: SelectProps) {
  return (
    <div className="flex flex-col gap-2 w-full">
      {label && (
        <label htmlFor={props.id} className="block">
          {label}
        </label>
      )}
      <select
        className={`h-12 px-4 border-2 border-[#CCCCCC] rounded bg-white text-black w-full
          focus:border-[#0066CC] focus:outline-none
          disabled:bg-gray-200 disabled:text-gray-600 disabled:cursor-not-allowed
          ${error ? 'border-[#CC0000]' : ''}
          ${className}`}
        {...props}
      >
        {options.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="text-[#CC0000] text-sm">{error}</p>}
    </div>
  );
}
