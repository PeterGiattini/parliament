import React, { useState } from 'react'
import { Send, Loader2 } from 'lucide-react'

interface DebateInputProps {
  onStartDebate: (topic: string) => void
  isDebating: boolean
  currentTopic: string
}

const DebateInput: React.FC<DebateInputProps> = ({ onStartDebate, isDebating, currentTopic }) => {
  const [topic, setTopic] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (topic.trim() && !isDebating) {
      onStartDebate(topic.trim())
      setTopic('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault()
      if (topic.trim() && !isDebating) {
        onStartDebate(topic.trim())
        setTopic('')
      }
    }
  }

  return (
    <div className="bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-lg border border-gray-200 p-8">
      {isDebating ? (
        <div className="flex items-center space-x-4 text-gray-700">
          <div className="relative">
            <Loader2 className="animate-spin h-6 w-6 text-parliament-blue" />
          </div>
          <div>
            <p className="font-semibold text-lg">Debate in progress...</p>
            <p className="text-sm text-gray-500 mt-1">Topic: {currentTopic}</p>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="topic" className="block text-sm font-semibold text-gray-700 mb-3">
              Debate Topic
            </label>
            <textarea
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g., Should we replace fossil fuels with 100% nuclear energy?"
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-parliament-blue focus:border-parliament-blue resize-none transition-all duration-200 hover:border-gray-300"
              rows={4}
              disabled={isDebating}
            />
          </div>
          <button
            type="submit"
            disabled={!topic.trim() || isDebating}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-semibold rounded-lg shadow-md text-white bg-gradient-to-r from-parliament-blue to-blue-600 hover:from-blue-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-parliament-blue disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
          >
            <Send className="h-5 w-5 mr-2" />
            Begin Debate
          </button>
        </form>
      )}
    </div>
  )
}

export default DebateInput 
