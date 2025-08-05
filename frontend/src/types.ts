export interface DebateMessage {
  type: 'round_header' | 'agent_message' | 'synthesis' | 'debate_complete' | 'error'
  timestamp: Date
  content?: string
  agent?: string
  role?: string
  color?: string
  icon?: string
  round?: number
  title?: string
}

export interface Agent {
  name: string
  role: string
  system_prompt: string
  color: string
  icon: string
} 
