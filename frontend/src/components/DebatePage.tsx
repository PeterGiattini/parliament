import React, { useState, useRef, useEffect } from 'react'
import { Download, Upload } from 'lucide-react'
import DebateInput from './DebateInput'
import DebateStream from './DebateStream'
import { DebateMessage } from '../types'
import Button from './Button'

const DebatePage: React.FC = () => {
  const [messages, setMessages] = useState<DebateMessage[]>([])
  const [isDebating, setIsDebating] = useState(false)
  const [currentTopic, setCurrentTopic] = useState('')
  const [currentPanelId, setCurrentPanelId] = useState<string | null>(null)

  const handleExportWorkspace = async () => {
    try {
      const response = await fetch('/export')
      if (response.ok) {
        const data = await response.json()
        const blob = new Blob([data.data], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `parliament-workspace-${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Error exporting workspace:', error)
      alert('Failed to export workspace data')
    }
  }

  const handleImportWorkspace = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      const text = await file.text()
      const response = await fetch('/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ json_data: text }),
      })

      if (response.ok) {
        // Refresh the page to show imported data
        window.location.reload()
      } else {
        alert('Failed to import workspace data')
      }
    } catch (error) {
      console.error('Error importing workspace:', error)
      alert('Failed to import workspace data')
    }
  }

  const startDebate = async (topic: string, agentIds: string[], panelId?: string) => {
    setCurrentTopic(topic)
    setMessages([])
    setIsDebating(true)
    setCurrentPanelId(panelId || null)

    try {
      const response = await fetch('/debate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          topic,
          agent_ids: agentIds.length > 0 ? agentIds : undefined,
          panel_id: panelId
        }),
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
      {/* Header with branding and workspace management */}
      <div className="bg-parliament-blue text-white p-6 rounded-lg mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">🏛️</div>
            <div>
              <h1 className="text-2xl font-bold">Parliament</h1>
              <p className="text-sm text-blue-100">Multi-Agent AI Debate System</p>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4">
            <p className="text-xs text-gray-500 mb-2">Import/Export Workspace</p>
            <div className="flex space-x-2">
              <Button
                variant="secondary"
                onClick={handleExportWorkspace}
              >
                <Download className="h-4 w-4 mr-1" />
                Export
              </Button>
              <label className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-parliament-blue cursor-pointer">
                <Upload className="h-4 w-4 mr-1" />
                Import
                <input
                  type="file"
                  accept=".json"
                  onChange={handleImportWorkspace}
                  className="hidden"
                />
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="mb-8 text-center">
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
