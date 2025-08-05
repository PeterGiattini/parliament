import React from 'react'
import ReactMarkdown from 'react-markdown'
import { DebateMessage as DebateMessageType } from '../types'

interface DebateMessageProps {
  message: DebateMessageType
  isLast: boolean
}

const DebateMessage: React.FC<DebateMessageProps> = ({ message, isLast }) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  switch (message.type) {
    case 'round_header':
      return (
        <div className="round-header bg-white border border-gray-300 rounded-lg p-4 shadow-sm">
          <div className="flex items-center space-x-3">
            <span className="text-xl font-bold text-gray-900">Round {message.round}</span>
            <span className="text-gray-500">•</span>
            <span className="text-gray-900 font-semibold">{message.title}</span>
          </div>
        </div>
      )

    case 'agent_message':
      return (
        <div className={`debate-bubble agent-bubble bg-white border-2 shadow-lg rounded-xl p-6 max-w-4xl mx-auto`} style={{ borderLeftColor: message.color }}>
          <div className="flex items-start space-x-4">
            <div className="text-3xl bg-gray-100 rounded-full w-12 h-12 flex items-center justify-center flex-shrink-0 leading-none">{message.icon}</div>
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-3">
                <h4 className="font-bold text-lg" style={{ color: message.color }}>
                  {message.agent}
                </h4>
                <span className="text-xs font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                  Round {message.round}
                </span>
                <span className="text-xs text-gray-400">
                  {formatTime(message.timestamp)}
                </span>
              </div>
              <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed">
                <ReactMarkdown>{message.content || ''}</ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      )

    case 'synthesis':
      return (
        <div className="debate-bubble synthesis-bubble bg-gradient-to-br from-gray-50 to-gray-100 border-2 border-gray-300 rounded-xl p-6 max-w-4xl mx-auto">
          <div className="flex items-start space-x-4">
            <div className="text-3xl bg-white rounded-full p-2 shadow-sm">📋</div>
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-3">
                <h4 className="font-bold text-lg text-gray-800">Synthesis</h4>
                <span className="text-xs text-gray-400">
                  {formatTime(message.timestamp)}
                </span>
              </div>
              <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed">
                <ReactMarkdown>{message.content || ''}</ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      )

    case 'debate_complete':
      return (
        <div className="text-center py-6">
          <div className="inline-flex items-center space-x-3 text-gray-600 bg-green-50 px-6 py-3 rounded-full">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="font-semibold">Debate Complete</span>
          </div>
        </div>
      )

    case 'error':
      return (
        <div className="debate-bubble bg-red-50 border-2 border-red-200 rounded-xl p-4 max-w-4xl mx-auto">
          <div className="flex items-center space-x-3 text-red-700">
            <span className="text-xl">⚠️</span>
            <span className="font-medium">{message.content}</span>
          </div>
        </div>
      )

    default:
      return null
  }
}

export default DebateMessage 
