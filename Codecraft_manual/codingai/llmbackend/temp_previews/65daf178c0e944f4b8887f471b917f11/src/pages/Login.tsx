import React from 'react'
import Button from '../components/Button'
import Input from '../components/Input'

const Login = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Login</h1>
      <form>
        <Input type="email" placeholder="Email" />
        <Input type="password" placeholder="Password" />
        <Button>Login</Button>
      </form>
    </div>
  )
}

export default Login