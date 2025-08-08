import React from 'react'
import ReactMarkdown from 'react-markdown'
import { DebateMessage } from '../types'

interface DebateMessageProps {
  message: DebateMessage
  isLast: boolean
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const DebateMessageComponent: React.FC<DebateMessageProps> = ({ message, isLast }) => {
  const animateClass = isLast ? 'animate-fade-in' : ''

  switch (message.type) {
    case 'round_header':
      return (
        <div className={`py-4 ${animateClass}`}>
          <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <div className="flex items-center space-x-3">
              <span className="text-xl font-bold text-gray-900">Round {message.round}</span>
              <span className="text-gray-500">•</span>
              <span className="text-gray-900 font-semibold">{message.title}</span>
              <span className="text-xs text-gray-400">{formatTime(message.timestamp)}</span>
            </div>
          </div>
        </div>
      )

    case 'agent_message':
      return (
        <div className={`py-2 ${animateClass}`}>
          <div className="flex items-start space-x-4">
            <div
              className="flex-shrink-0 h-12 w-12 rounded-full flex items-center justify-center text-2xl"
              style={{ backgroundColor: message.color }}
            >
              {message.icon}
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <span className="font-bold text-lg" style={{ color: message.color }}>
                  {message.agent}
                </span>
                <span className="text-xs font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                  Round {message.round}
                </span>
                <span className="text-xs text-gray-400">
                  {formatTime(message.timestamp)}
                </span>
              </div>
              <div className="prose prose-sm max-w-none text-gray-700">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      )

    case 'thinking':
      return (
        <div className={`py-2 ${animateClass}`}>
          <div className="flex items-center space-x-3">
            <div
              className="flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center text-xl animate-pulse"
              style={{ backgroundColor: message.color }}
            >
              {message.icon}
            </div>
            <span className="text-sm text-gray-600">{message.agent} is thinking...</span>
          </div>
        </div>
      )

    case 'synthesis':
      return (
        <div className={`py-4 ${animateClass}`}>
          <div className="bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200 rounded-lg p-6">
            <div className="flex items-start space-x-4">
              <div className="text-3xl bg-white rounded-full p-2 shadow-sm">📋</div>
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-3">
                  <h4 className="font-bold text-lg text-gray-800">Synthesis</h4>
                  <span className="text-xs text-gray-400">
                    {formatTime(message.timestamp)}
                  </span>
                </div>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          </div>
        </div>
      )

    case 'debate_complete':
      return (
        <div className={`text-center py-6 ${animateClass}`}>
          <div className="inline-flex items-center space-x-3 text-gray-600 bg-green-50 px-6 py-3 rounded-full">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="font-semibold">Debate Complete</span>
            <span className="text-xs text-gray-400">
              {formatTime(message.timestamp)}
            </span>
          </div>
        </div>
      )

    case 'error':
      return (
        <div className={`py-4 ${animateClass}`}>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-3 text-red-700">
              <span className="text-xl">⚠️</span>
              <span className="font-medium">{message.content}</span>
            </div>
          </div>
        </div>
      )

    default:
      return null
  }
}

export default DebateMessageComponent 
