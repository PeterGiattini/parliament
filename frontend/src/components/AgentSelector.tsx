import React, { useState, useEffect } from 'react'
import { Search, Plus, X, Check } from 'lucide-react'
import { Agent } from '../types'
import TagList from './TagList'
import Card from './Card'
import Button from './Button'

interface AgentSelectorProps {
  selectedAgents: Agent[]
  onAgentSelect: (agent: Agent) => void
  onAgentDeselect: (agentId: string) => void
  onGenerateAgent: (prompt: string) => void
}

const AgentSelector: React.FC<AgentSelectorProps> = ({
  selectedAgents,
  onAgentSelect,
  onAgentDeselect,
  onGenerateAgent
}) => {
  const [agents, setAgents] = useState<Agent[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [showGenerateModal, setShowGenerateModal] = useState(false)
  const [generatePrompt, setGeneratePrompt] = useState('')
  const [agentName, setAgentName] = useState('')


  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      const response = await fetch('/agents')
      if (response.ok) {
        const data = await response.json()
        setAgents(data.agents)
      }
    } catch (error) {
      console.error('Error fetching agents:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }

  const clearSearch = () => {
    setSearchQuery('')
  }

  const handleGenerateAgent = async () => {
    if (!generatePrompt.trim()) return

    try {
      console.log('Generating agent with prompt:', generatePrompt)
      const response = await fetch('/agents/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt: generatePrompt,
          name: agentName.trim() || undefined // Only send if provided
        }),
      })

      console.log('Response status:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('Generated agent data:', data)
        const newAgent = data.agent
        
        // Add to agents list
        setAgents(prev => [newAgent, ...prev])
        
        // Auto-add to selected agents
        onAgentSelect(newAgent)
        
        setShowGenerateModal(false)
        setGeneratePrompt('')
        setAgentName('')
      } else {
        const errorText = await response.text()
        console.error('Error response:', errorText)
        alert(`Failed to generate agent: ${errorText}`)
      }
    } catch (error) {
      console.error('Error generating agent:', error)
      alert(`Error generating agent: ${error}`)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault()
      handleGenerateAgent()
    }
  }

  const isAgentSelected = (agentId: string) => {
    return selectedAgents.some(agent => agent.id === agentId)
  }



  // Live filtering based on search query
  const filteredAgents = agents.filter(agent => {
    if (!searchQuery.trim()) return !isAgentSelected(agent.id)
    
    const queryLower = searchQuery.toLowerCase()
    const matchesSearch = (
      agent.name.toLowerCase().includes(queryLower) ||
      agent.description.toLowerCase().includes(queryLower) ||
      agent.tags.some(tag => tag.toLowerCase().includes(queryLower))
    )
    
    return matchesSearch && !isAgentSelected(agent.id)
  })

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Select Agents</h3>
        <Button onClick={() => setShowGenerateModal(true)}>
          <Plus className="h-4 w-4 mr-1" />
          Generate Agent
        </Button>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="Search agents..."
            value={searchQuery}
            onChange={handleSearchChange}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-parliament-blue focus:border-parliament-blue"
          />
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          {searchQuery && (
            <button
              onClick={clearSearch}
              className="absolute right-3 top-2.5 h-4 w-4 text-gray-400 hover:text-gray-600"
            >
              <X />
            </button>
          )}
        </div>
      </div>

      {/* Selected Agents */}
      {selectedAgents.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Selected Agents ({selectedAgents.length})</h4>
          <div className="space-y-2">
            {selectedAgents.map(agent => (
              <div
                key={agent.id}
                className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{agent.icon}</span>
                  <div>
                    <div className="font-medium text-gray-900">{agent.name}</div>
                    <div className="text-sm text-gray-600">{agent.description}</div>
                  </div>
                </div>
                <button
                  onClick={() => onAgentDeselect(agent.id)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Available Agents */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-3">
          Available Agents ({filteredAgents.length})
        </h4>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredAgents.map(agent => (
            <div
              key={agent.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all"
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{agent.icon}</span>
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{agent.name}</div>
                  <div className="text-sm text-gray-600">{agent.description}</div>
                  <TagList tags={agent.tags} />
                </div>
              </div>
              <button
                onClick={() => onAgentSelect(agent)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Generate Agent Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Generate New Agent</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Agent Name (optional)
                </label>
                <input
                  type="text"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  placeholder="e.g., The Economist, Abraham Lincoln, etc."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-parliament-blue focus:border-parliament-blue"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Agent Description *
                </label>
                <textarea
                  placeholder="Describe the agent you want to create (e.g., 'A Keynesian economist', 'Abraham Lincoln oration style', etc.)"
                  value={generatePrompt}
                  onChange={(e) => setGeneratePrompt(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-parliament-blue focus:border-parliament-blue resize-none"
                  rows={4}
                />
              </div>
            </div>
            <div className="flex space-x-3 mt-6">
              <Button
                variant="secondary"
                onClick={() => {
                  setShowGenerateModal(false)
                  setGeneratePrompt('')
                  setAgentName('')
                }}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleGenerateAgent}
                disabled={!generatePrompt.trim()}
                className="flex-1"
              >
                Generate
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  )
}

export default AgentSelector 
