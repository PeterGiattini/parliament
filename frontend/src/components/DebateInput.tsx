import React, { useState } from 'react'
import { Send, Loader2, Users, ChevronDown, ChevronUp } from 'lucide-react'
import { Agent } from '../types'
import AgentSelector from './AgentSelector'
import PanelManager from './PanelManager'

interface DebateInputProps {
  onStartDebate: (topic: string, agentIds: string[], panelId?: string) => void
  isDebating: boolean
  currentTopic: string
}

const DebateInput: React.FC<DebateInputProps> = ({ onStartDebate, isDebating, currentTopic }) => {
  const [topic, setTopic] = useState('')
  const [selectedAgents, setSelectedAgents] = useState<Agent[]>([])
  const [showAgentSelector, setShowAgentSelector] = useState(false)
  const [currentPanelId, setCurrentPanelId] = useState<string | null>(null)

  const attemptStartDebate = () => {
    if (!topic.trim() || isDebating) return
    const agentIds = selectedAgents.length > 0 ? selectedAgents.map(agent => agent.id) : []
    // Auto-close the agent selector when starting a debate
    setShowAgentSelector(false)
    onStartDebate(topic.trim(), agentIds, currentPanelId || undefined)
    setTopic('')
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    attemptStartDebate()
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault()
      attemptStartDebate()
    }
  }

  const handleAgentSelect = (agent: Agent) => {
    setSelectedAgents(prev => [...prev, agent])
  }

  const handleAgentDeselect = (agentId: string) => {
    setSelectedAgents(prev => prev.filter(agent => agent.id !== agentId))
  }

  const handleGenerateAgent = async (prompt: string) => {
    // This will be handled by the AgentSelector component
  }

  const handleLoadPanel = async (agentIds: string[]) => {
    // Fetch agents by IDs and set them as selected
    try {
      const response = await fetch('/agents')
      if (response.ok) {
        const data = await response.json()
        const agents = data.agents.filter((agent: Agent) => agentIds.includes(agent.id))
        setSelectedAgents(agents)
      }
    } catch (error) {
      console.error('Error loading panel:', error)
    }
  }

  const handleSetCurrentPanel = (panelId: string) => {
    setCurrentPanelId(panelId)
  }

  return (
    <div className="space-y-6">
      {/* Main Debate Input */}
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

            {/* Agent Selection Toggle */}
            <div className="border-t border-gray-200 pt-6">
              <button
                type="button"
                onClick={() => setShowAgentSelector(!showAgentSelector)}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-3">
                  <Users className="h-5 w-5 text-gray-500" />
                  <div>
                    <div className="font-medium text-gray-900">
                      {selectedAgents.length > 0 
                        ? `${selectedAgents.length} agent${selectedAgents.length !== 1 ? 's' : ''} selected`
                        : 'Select agents (optional)'
                      }
                    </div>
                    <div className="text-sm text-gray-500">
                      {selectedAgents.length > 0 
                        ? selectedAgents.map(agent => agent.name).join(', ')
                        : 'Use default panel if none selected'
                      }
                    </div>
                  </div>
                </div>
                {showAgentSelector ? (
                  <ChevronUp className="h-5 w-5 text-gray-500" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-500" />
                )}
              </button>
            </div>

            {showAgentSelector && !isDebating && (
              <div className="pt-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <AgentSelector
                    selectedAgents={selectedAgents}
                    onAgentSelect={handleAgentSelect}
                    onAgentDeselect={handleAgentDeselect}
                    onGenerateAgent={handleGenerateAgent}
                  />
                  <PanelManager
                    selectedAgents={selectedAgents}
                    onLoadPanel={handleLoadPanel}
                    onSetCurrentPanel={handleSetCurrentPanel}
                  />
                </div>
              </div>
            )}

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
    </div>
  )
}

export default DebateInput 
