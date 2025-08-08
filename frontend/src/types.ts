// Base message type with common fields
interface BaseMessage {
  timestamp: Date
  type: 'round_header' | 'agent_message' | 'thinking' | 'synthesis' | 'debate_complete' | 'error'
}

// Round header message (shown when rounds start)
interface RoundHeaderMessage extends BaseMessage {
  type: 'round_header'
  round: number
  title: string
  round_type: 'parallel' | 'sequential' | 'moderator'
}

// Agent message (responses from agents)
interface AgentMessage extends BaseMessage {
  type: 'agent_message'
  agent: string
  role: string
  content: string
  round: number
  color: string
  icon: string
}

// Thinking message (shown while agent is generating response)
interface ThinkingMessage extends BaseMessage {
  type: 'thinking'
  agent: string
  icon: string
  color: string
}

// Synthesis message (from moderator)
interface SynthesisMessage extends BaseMessage {
  type: 'synthesis'
  content: string
}

// Debate complete message
interface DebateCompleteMessage extends BaseMessage {
  type: 'debate_complete'
}

// Error message
interface ErrorMessage extends BaseMessage {
  type: 'error'
  content: string
}

// Union type for all possible message types
export type DebateMessage = 
  | RoundHeaderMessage 
  | AgentMessage 
  | ThinkingMessage 
  | SynthesisMessage 
  | DebateCompleteMessage 
  | ErrorMessage

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
