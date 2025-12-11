import React from 'react'
import Hero from './sections/Hero'
import Features from './sections/Features'
import Why from './sections/Why'
import Fqs from "./sections/Fqs"
import Call from './sections/Call'

export default function Home() {
  return (
    <div>
        <Hero />
        <Features />
        <Why />
        <Fqs />
        <Call />
    </div>
  )
}
