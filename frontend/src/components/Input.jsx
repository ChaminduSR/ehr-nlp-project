import React from 'react'

export default function Input({ type = 'text', placeholder, value, onChange, required = false, style = {}, id, className = '', ...props }) {
  return (
    <input
      id={id}
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      required={required}
      className={`input ${className}`}
      style={style}
      {...props}
    />
  )
}
