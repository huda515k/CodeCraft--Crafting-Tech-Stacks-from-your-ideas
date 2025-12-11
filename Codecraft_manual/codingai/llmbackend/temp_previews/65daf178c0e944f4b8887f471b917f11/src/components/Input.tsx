import React from 'react'

type InputProps = {
  type?: string
  placeholder?: string
}

const Input: React.FC<InputProps> = ({ type, placeholder }) => {
  return (
    <input className="w-full px-3 py-2 border rounded-md" type={type} placeholder={placeholder} />
  )
}

export default Input