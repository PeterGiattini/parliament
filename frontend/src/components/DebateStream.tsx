import React, { useRef, useEffect, useState } from 'react'
import { DebateMessage, StatusUpdate } from '../types'
import DebateMessageComponent from './DebateMessage'

interface DebateStreamProps {
  messages: DebateMessage[]
  isDebating: boolean
  topic: string
  status: StatusUpdate | null
}

const DebateStream: React.FC<DebateStreamProps> = ({ messages, isDebating, topic, status }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [dots, setDots] = useState(1)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Animate the ellipsis while debating
  useEffect(() => {
    if (!isDebating) {
      setDots(1)
      return
    }
    const id = setInterval(() => {
      setDots((prev) => ((prev % 3) + 1))
    }, 500)
    return () => clearInterval(id)
  }, [isDebating])

  const renderStatus = () => {
    if (!isDebating && messages.length > 0) {
      return <span className="text-sm font-medium text-gray-600">Debate Complete</span>
    }
    if (!status) {
      return (
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-3"></div>
          <span className="text-sm font-medium text-gray-600">Live Debate in Progress</span>
        </div>
      )
    }

    let statusText = ''
    switch (status.code) {
      case 'ROUND_STARTING':
        statusText = `Starting ${status.round_title}...`
        break
      case 'AGENT_TURN_STARTING':
        statusText = `${status.agent?.name} is thinking...`
        break
      case 'SYNTHESIS':
        statusText = 'Generating Synthesis...'
        break
      default:
        statusText = 'Live Debate in Progress'
    }

    return (
      <div className="flex items-center">
        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-3"></div>
        <span className="text-sm font-medium text-gray-600">{statusText}</span>
      </div>
    )
  }

  const footerThinkingLabel = () => {
    if (!isDebating) return null
    const isModerator = status?.code === 'SYNTHESIS'
    const label = isModerator ? 'Moderator is thinking' : 'Thinking'
    return (
      <div className="flex justify-center py-4">
        <div className="inline-flex items-center space-x-3 text-gray-600 bg-gray-100 px-6 py-2 rounded-full">
          <div className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium">
            {label}
            <span className="relative inline-block align-baseline">
              <span className="invisible">...</span>
              <span className="absolute left-0 top-0" aria-hidden>
                {'.'.repeat(dots)}
              </span>
            </span>
          </span>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden">
      <div className="p-6 border-b bg-white border-gray-200">
        <h3 className="text-xl font-bold text-gray-900 mb-2">Debate: {topic}</h3>
        {renderStatus()}
      </div>

      <div className="p-6 space-y-6 bg-gray-50">
        {messages.map((message, index) => (
          <DebateMessageComponent
            key={index}
            message={message}
            isLast={index === messages.length - 1}
          />
        ))}

        {footerThinkingLabel()}

        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}

export default DebateStream 
