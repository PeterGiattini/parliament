import React, { useState, useRef, useEffect } from 'react'
import DebateInput from './DebateInput'
import DebateStream from './DebateStream'
import { DebateMessage } from '../types'

const DebatePage: React.FC = () => {
  const [messages, setMessages] = useState<DebateMessage[]>([])
  const [isDebating, setIsDebating] = useState(false)
  const [currentTopic, setCurrentTopic] = useState('')

  const startDebate = async (topic: string) => {
    setCurrentTopic(topic)
    setMessages([])
    setIsDebating(true)

    try {
      const response = await fetch('/debate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      const decoder = new TextDecoder()
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              handleStreamMessage(data)
            } catch (e) {
              console.error('Error parsing stream data:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('Error starting debate:', error)
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'An error occurred while starting the debate. Please try again.',
        timestamp: new Date()
      }])
    } finally {
      setIsDebating(false)
    }
  }

  const handleStreamMessage = (data: any) => {
    switch (data.type) {
      case 'round_start':
        setMessages(prev => [...prev, {
          type: 'round_header',
          round: data.round,
          title: data.title,
          timestamp: new Date()
        }])
        break
      
      case 'agent_response':
        setMessages(prev => [...prev, {
          type: 'agent_message',
          agent: data.agent,
          role: data.role,
          content: data.content,
          color: data.color,
          icon: data.icon,
          round: data.round,
          timestamp: new Date()
        }])
        break
      
      case 'synthesis':
        setMessages(prev => [...prev, {
          type: 'synthesis',
          content: data.content,
          timestamp: new Date()
        }])
        break
      
      case 'debate_complete':
        setMessages(prev => [...prev, {
          type: 'debate_complete',
          timestamp: new Date()
        }])
        break
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-12 text-center">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          What should we debate?
        </h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
          Pose a question or dilemma, and our panel of AI experts will analyze it from multiple perspectives.
        </p>
      </div>
      
      <div className="mb-8">
        <DebateInput 
          onStartDebate={startDebate} 
          isDebating={isDebating}
          currentTopic={currentTopic}
        />
      </div>
      
      {messages.length > 0 && (
        <DebateStream 
          messages={messages} 
          isDebating={isDebating}
          topic={currentTopic}
        />
      )}
    </div>
  )
}

export default DebatePage 
