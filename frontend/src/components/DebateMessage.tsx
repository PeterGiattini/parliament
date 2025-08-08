import React from 'react'
import ReactMarkdown from 'react-markdown'
import { DebateMessage } from '../types'

interface DebateMessageProps {
  message: DebateMessage
  isLast: boolean
}

const DebateMessageComponent: React.FC<DebateMessageProps> = ({ message, isLast }) => {
  const { agent, role, content, color, icon } = message

  return (
    <div className={`flex items-start space-x-4 ${isLast ? 'animate-fade-in' : ''}`}>
      <div
        className="flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center text-white text-xl"
        style={{ backgroundColor: color }}
      >
        {icon}
      </div>
      <div className="flex-1">
        <div className="font-bold text-gray-800">{agent}</div>
        <div className="text-sm text-gray-500 mb-2">{role}</div>
        <div className="prose prose-sm max-w-none text-gray-700">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    </div>
  )
}

export default DebateMessageComponent 
