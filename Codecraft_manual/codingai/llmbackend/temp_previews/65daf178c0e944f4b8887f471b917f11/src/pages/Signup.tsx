import React from 'react'
import Button from '../components/Button'
import Input from '../components/Input'

const Signup = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Signup</h1>
      <form>
        <Input type="text" placeholder="Username" />
        <Input type="email" placeholder="Email" />
        <Input type="password" placeholder="Password" />
        <Button>Signup</Button>
      </form>
    </div>
  )
}

export default Signup