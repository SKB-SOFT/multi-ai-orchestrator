// src/types/dashboard.ts
/**
 * TypeScript type definitions for the Multi-AI Orchestrator Dashboard
 */

export interface SystemMetrics {
  total_requests: number
  active_agents: number
  uptime_seconds: number
  cpu_percent: number
  memory_percent: number
  memory_available_gb: number
  avg_response_time?: number
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
  status: 'active' | 'idle' | 'error' | 'offline'
}

export interface ErrorLogItem {
  agent_id: string
  error_type: string
  error_message: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  timestamp: string
}

export interface ActivityItem {
  type: 'request' | 'error'
  agent_id: string
  agent_name?: string
  timestamp: string
  response_time_ms?: number
  success?: boolean
  model?: string
  error_type?: string
  error_message?: string
  severity?: 'low' | 'medium' | 'high' | 'critical'
}

export interface MetricDataPoint {
  timestamp: string
  value: number
  label?: string
}

export interface MetricsData {
  requests: MetricDataPoint[]
  responseTime: MetricDataPoint[]
  errors: MetricDataPoint[]
}

export interface LiveActivity {
  id: string
  timestamp: string
  agentName: string
  action: string
  duration: number
  status: 'success' | 'failure' | 'pending'
}

export interface ActiveRequest {
  id: string
  agentId: string
  agentName: string
  startTime: string
  requestType: string
  status: 'processing' | 'queued'
}

export interface WebSocketMessage {
  type: 'stats_update' | 'agent_update' | 'error_log' | 'live_activity' | 'connected' | 'error_resolved' | 'request' | 'error'
  payload?: any
  data?: any
  message?: string
}

export interface DashboardConfig {
  refreshInterval: number
  maxErrorLogs: number
  maxLiveActivities: number
  chartTimeRange: '1h' | '6h' | '24h' | '7d'
}

export interface AgentMetrics {
  agentId: string
  timeRange: string
  requestCount: number
  avgResponseTime: number
  successRate: number
  errorCount: number
}
