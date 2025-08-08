// Represents a message or event in the debate transcript.
export interface DebateMessage {
  agent: string
  role: string
  content: string
  round: number
  color: string
  icon: string
  timestamp: Date
}

// Represents a structured status update from the orchestrator.
export interface StatusUpdate {
  code: 'ROUND_STARTING' | 'AGENT_TURN_STARTING' | 'SYNTHESIS' | 'END'
  round_number?: number
  round_title?: string
  round_type?: 'parallel' | 'sequential' | 'moderator'
  agent?: {
    name: string
    icon: string
  }
}

// Represents the structured data received from the SSE stream.
export interface StreamEvent {
  type: 'status_update' | 'agent_response' | 'debate_complete' | 'error'
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any // Allows for flexible data properties
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