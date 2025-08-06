export interface DebateMessage {
  type: 'agent_message' | 'synthesis' | 'round_header' | 'debate_complete' | 'error'
  content?: string
  agent?: string
  role?: string
  color?: string
  icon?: string
  round?: number
  title?: string
  timestamp: Date
}

export interface Agent {
  id: string
  name: string
  description: string
  system_prompt: string
  tags: string[]
  is_built_in: boolean
  created_at: number
  usage_count: number
  color: string
  icon: string
}

export interface Panel {
  id: string
  name: string
  description: string
  agent_ids: string[]
  tags: string[]
  is_built_in: boolean
  created_at: number
  usage_count: number
}

export interface AgentGenerationRequest {
  prompt: string
}

export interface AgentCreationRequest {
  name: string
  description: string
  system_prompt: string
  tags: string[]
  color: string
  icon: string
}

export interface PanelCreationRequest {
  name: string
  description: string
  agent_ids: string[]
  tags: string[]
}

export interface DebateRequest {
  topic: string
  agent_ids?: string[]
  panel_id?: string
} 
