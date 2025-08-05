import React from 'react'

const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-gray-900 to-gray-800 shadow-xl border-b border-gray-700">
      <div className="container mx-auto px-6 py-8">
        <div className="flex items-center space-x-4">
          <div className="text-4xl">
            🏛️
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">Parliament</h1>
            <p className="text-gray-300 font-medium">Multi-Agent AI Debate System</p>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 
