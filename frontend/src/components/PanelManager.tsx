import React, { useState, useEffect } from 'react'
import { Save, FolderOpen } from 'lucide-react'
import { Panel, Agent } from '../types'
import TagList from './TagList'
import Card from './Card'
import Button from './Button'

interface PanelManagerProps {
  selectedAgents: Agent[]
  onLoadPanel: (agentIds: string[]) => void
  onSetCurrentPanel: (panelId: string) => void
}

const PanelManager: React.FC<PanelManagerProps> = ({
  selectedAgents,
  onLoadPanel,
  onSetCurrentPanel
}) => {
  const [panels, setPanels] = useState<Panel[]>([])
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [panelName, setPanelName] = useState('')
  const [panelDescription, setPanelDescription] = useState('')
  const [panelTags, setPanelTags] = useState('')


  useEffect(() => {
    fetchPanels()
  }, [])

  const fetchPanels = async () => {
    try {
      const response = await fetch('/panels')
      if (response.ok) {
        const data = await response.json()
        setPanels(data.panels)
      }
    } catch (error) {
      console.error('Error fetching panels:', error)
    }
  }

  const handleSavePanel = async () => {
    if (!panelName.trim() || selectedAgents.length === 0) return

    try {
      const response = await fetch('/panels', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: panelName,
          description: panelDescription,
          agent_ids: selectedAgents.map(agent => agent.id),
          tags: panelTags.split(',').map(tag => tag.trim()).filter(tag => tag)
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setPanels(prev => [data.panel, ...prev])
        setShowSaveModal(false)
        setPanelName('')
        setPanelDescription('')
        setPanelTags('')
      }
    } catch (error) {
      console.error('Error saving panel:', error)
    }
  }

  const handleLoadPanel = async (panel: Panel) => {
    // First, increment the usage count
    try {
      await fetch(`/panels/${panel.id}/use`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
    } catch (error) {
      console.error('Error updating panel usage:', error)
    }
    
    // Then load the panel agents
    onLoadPanel(panel.agent_ids)
    onSetCurrentPanel(panel.id) // Set the current panel ID
    
    // Refresh the panels list to show updated usage count
    fetchPanels()
  }



  return (
    <Card className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Panel Management</h3>
      </div>

      {/* Save Current Panel */}
      {selectedAgents.length > 0 && (
        <div className="mb-6">
          <Button
            onClick={() => setShowSaveModal(true)}
            className="w-full"
          >
            <Save className="h-4 w-4 mr-2" />
            Save Current Panel ({selectedAgents.length} agents)
          </Button>
        </div>
      )}

      {/* Saved Panels */}
      <div className="flex-1 flex flex-col">
        <h4 className="text-sm font-medium text-gray-700 mb-3">
          Saved Panels ({panels.length})
        </h4>
        <div className="space-y-3 flex-1 overflow-y-auto min-h-0">
          {panels.map(panel => (
            <div
              key={panel.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all"
            >
              <div className="flex-1">
                <div className="font-medium text-gray-900">{panel.name}</div>
                <div className="text-sm text-gray-600">{panel.description}</div>
                <TagList tags={panel.tags} />
                <div className="text-xs text-gray-500 mt-1">
                  {panel.agent_ids.length} agents • Used {panel.usage_count} {panel.usage_count === 1 ? 'time' : 'times'}
                </div>
              </div>
              <Button
                variant="secondary"
                onClick={() => handleLoadPanel(panel)}
              >
                <FolderOpen className="h-4 w-4 mr-1" />
                Load
              </Button>
            </div>
          ))}
          {panels.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <FolderOpen className="h-12 w-12 mx-auto mb-2 text-gray-300" />
              <p>No saved panels yet</p>
              <p className="text-sm">Save your first panel to get started</p>
            </div>
          )}
        </div>
      </div>

      {/* Save Panel Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Save Panel</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Panel Name *
                </label>
                <input
                  type="text"
                  value={panelName}
                  onChange={(e) => setPanelName(e.target.value)}
                  placeholder="e.g., Economic Policy Panel"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-parliament-blue focus:border-parliament-blue"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={panelDescription}
                  onChange={(e) => setPanelDescription(e.target.value)}
                  placeholder="Brief description of this panel's purpose"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-parliament-blue focus:border-parliament-blue resize-none"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={panelTags}
                  onChange={(e) => setPanelTags(e.target.value)}
                  placeholder="economics, policy, debate"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-parliament-blue focus:border-parliament-blue"
                />
              </div>
            </div>
            <div className="flex space-x-3 mt-6">
              <Button
                variant="secondary"
                onClick={() => setShowSaveModal(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleSavePanel}
                disabled={!panelName.trim()}
                className="flex-1"
              >
                Save Panel
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  )
}

export default PanelManager 
