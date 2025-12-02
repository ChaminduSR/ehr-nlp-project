import React from 'react'

export default function Button({ children, onClick, type = 'button', disabled = false, variant = 'primary', style = {}, className = '' }) {
  const variantClass = variant === 'secondary' ? 'btn-secondary' : ''

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`btn ${variantClass} ${className}`}
      style={style}
    >
      {children}
    </button>
  )
}
