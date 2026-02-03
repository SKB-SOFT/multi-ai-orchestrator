// src/services/websocket.ts
/**
 * WebSocket service for real-time dashboard updates
 * Handles connection, reconnection, and message broadcasting
 */

export class DashboardWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private heartbeatInterval: NodeJS.Timeout | null = null
  private messageHandlers: ((data: any) => void)[] = []
  private errorHandlers: ((error: Event) => void)[] = []
  private closeHandlers: (() => void)[] = []

  constructor(private url: string) {}

  /**
   * Establish WebSocket connection
   */
  connect(
    onMessage: (data: any) => void,
    onError?: (error: Event) => void,
    onClose?: () => void
  ): void {
    try {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        console.log('[WebSocket] Connected to dashboard')
        this.reconnectAttempts = 0
        this.startHeartbeat()
      }

      this.ws.onmessage = (event) => {
        try {
          let data: any = event.data;
          // Only parse if it looks like JSON
          if (typeof data === 'string' && (data.startsWith('{') || data.startsWith('['))) {
            data = JSON.parse(data);
          }
          onMessage(data);
          this.messageHandlers.forEach(handler => handler(data));
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
        }
      }

      this.ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
        if (onError) onError(error)
        this.errorHandlers.forEach(handler => handler(error))
      }

      this.ws.onclose = (event) => {
        console.log('[WebSocket] Disconnected')
        if (onClose) onClose()
        this.closeHandlers.forEach(handler => handler())
        this.stopHeartbeat()
        this.attemptReconnect(onMessage, onError, onClose)
      }
    } catch (error) {
      console.error('[WebSocket] Connection failed:', error)
      this.attemptReconnect(onMessage, onError, onClose)
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(
    onMessage: (data: any) => void,
    onError?: (error: Event) => void,
    onClose?: () => void
  ): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1)

      console.log(
        `[WebSocket] Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`
      )

      setTimeout(() => {
        this.connect(onMessage, onError, onClose)
      }, delay)
    } else {
      console.error('[WebSocket] Max reconnection attempts reached')
    }
  }

  /**
   * Send heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected()) {
        this.send('ping')
      }
    }, 30000) // Send heartbeat every 30 seconds
  }

  /**
   * Stop heartbeat interval
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * Close WebSocket connection
   */
  disconnect(): void {
    this.stopHeartbeat()

    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting')
      this.ws = null
    }

    this.reconnectAttempts = 0
  }

  /**
   * Send data through WebSocket
   */
  send(data: any): void {
    if (this.isConnected()) {
      try {
        const message = typeof data === 'string' ? data : JSON.stringify(data)
        this.ws!.send(message)
      } catch (error) {
        console.error('[WebSocket] Failed to send message:', error)
      }
    } else {
      console.warn('[WebSocket] Cannot send message: Not connected')
    }
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }

  /**
   * Get connection state
   */
  getReadyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED
  }

  /**
   * Register a message handler
   */
  onMessage(handler: (data: any) => void): () => void {
    this.messageHandlers.push(handler)
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler)
    }
  }

  /**
   * Register an error handler
   */
  onError(handler: (error: Event) => void): () => void {
    this.errorHandlers.push(handler)
    return () => {
      this.errorHandlers = this.errorHandlers.filter(h => h !== handler)
    }
  }

  /**
   * Register a close handler
   */
  onClose(handler: () => void): () => void {
    this.closeHandlers.push(handler)
    return () => {
      this.closeHandlers = this.closeHandlers.filter(h => h !== handler)
    }
  }

  /**
   * Reset reconnection attempts (useful for manual reconnection)
   */
  resetReconnectAttempts(): void {
    this.reconnectAttempts = 0
  }
}

/**
 * Singleton instance for dashboard WebSocket
 */
let dashboardWsInstance: DashboardWebSocket | null = null

export const getDashboardWebSocket = (url?: string): DashboardWebSocket => {
  if (!dashboardWsInstance) {
    const wsUrl = url || process.env.REACT_APP_WS_URL || 'ws://localhost:8001/api/dashboard/ws'
    dashboardWsInstance = new DashboardWebSocket(wsUrl)
  }
  return dashboardWsInstance
}

/**
 * Close and reset the singleton instance
 */
export const closeDashboardWebSocket = (): void => {
  if (dashboardWsInstance) {
    dashboardWsInstance.disconnect()
    dashboardWsInstance = null
  }
}
