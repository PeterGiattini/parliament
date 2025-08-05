import React, { useState } from 'react'
import DebatePage from './components/DebatePage'
import Header from './components/Header'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      <Header />
      <main className="container mx-auto px-6 py-12">
        <DebatePage />
      </main>
    </div>
  )
}

export default App 
