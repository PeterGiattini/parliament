import React, { useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { DebateMessage } from '../types'
import DebateMessageComponent from './DebateMessage'

interface DebateStreamProps {
  messages: DebateMessage[]
  isDebating: boolean
  topic: string
}

const DebateStream: React.FC<DebateStreamProps> = ({ messages, isDebating, topic }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden">
      <div className="p-6 border-b bg-white border-gray-200">
        <h3 className="text-xl font-bold text-gray-900 mb-2">Debate: {topic}</h3>
        {isDebating && (
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-3"></div>
            <span className="text-sm font-medium text-gray-600">Live Debate in Progress</span>
          </div>
        )}
      </div>
      
      <div className="p-6 space-y-6 bg-gray-50">
        {messages.map((message, index) => (
          <DebateMessageComponent 
            key={index} 
            message={message} 
            isLast={index === messages.length - 1}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}

export default DebateStream 
