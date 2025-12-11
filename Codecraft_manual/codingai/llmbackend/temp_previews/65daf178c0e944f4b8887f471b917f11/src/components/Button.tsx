import React from 'react'

type ButtonProps = {
  children: React.ReactNode
  variant?: 'primary' | 'secondary'
}

const Button: React.FC<ButtonProps> = ({ children, variant = 'primary' }) => {
  return (
    <button className={`px-4 py-2 rounded ${variant === 'primary' ? 'bg-blue-500' : 'bg-gray-300'} text-white`}>
      {children}
    </button>
  )
}

export default Button