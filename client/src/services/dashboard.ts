/**
 * Dashboard API client
 */

import axios from 'axios'

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8001'

export const dashboardAPI = axios.create({
  baseURL: `${API_URL}/api/dashboard`,
  headers: { 'Content-Type': 'application/json' },
})

export interface SystemMetrics {
  cpu_percent: number
  memory_percent: number
  memory_available_gb: number
  uptime_seconds: number
  active_agents: number
  total_requests: number
  success_rate: number
}

export interface AgentStat {
  agent_id: string
  name: string
  model: string
  total_requests: number
  successful_requests: number
  failed_requests: number
  success_rate: number
  avg_response_time: number
  last_used: string
  status: string
}

export interface ActivityItem {
  type: 'request' | 'error'
  agent_id: string
  timestamp: string
  [key: string]: any
}

export interface ErrorLogItem {
  agent_id: string
  error_type: string
  error_message: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  timestamp: string
}

// API Methods
export const dashboardService = {
  async getMetrics(): Promise<SystemMetrics> {
    const { data } = await dashboardAPI.get('/metrics')
    return data
  },

  async getActivity(limit = 20): Promise<ActivityItem[]> {
    const { data } = await dashboardAPI.get('/activity', { params: { limit } })
    return data.activity
  },

  async getAgents(): Promise<AgentStat[]> {
    const { data } = await dashboardAPI.get('/agents')
    return data.agents
  },

  async getErrors(limit = 50): Promise<ErrorLogItem[]> {
    const { data } = await dashboardAPI.get('/errors', { params: { limit } })
    return data.errors
  },

  async logRequest(request: {
    agent_id: string
    agent_name: string
    response_time_ms: number
    success: boolean
    model: string
    tokens_used?: number
  }) {
    return dashboardAPI.post('/log-request', {
      ...request,
      timestamp: new Date().toISOString(),
    })
  },

  async logError(error: {
    agent_id: string
    error_type: string
    error_message: string
    severity?: 'low' | 'medium' | 'high' | 'critical'
  }) {
    return dashboardAPI.post('/log-error', {
      ...error,
      severity: error.severity || 'medium',
      timestamp: new Date().toISOString(),
    })
  },
}
