// LockedIn AI - WebSocket Client
// Manages WebSocket connections for Duo mode and real-time features

class WebSocketClient {
  constructor(url, options = {}) {
    this.url = url;
    this.options = options;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
    this.reconnectDelay = options.reconnectDelay || 3000;
    this.autoReconnect = options.autoReconnect !== false;
    this.messageHandlers = [];
    this.connectionHandlers = [];
    this.errorHandlers = [];
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        console.log('WebSocket: Connecting to', this.url);

        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket: Connected');
          this.reconnectAttempts = 0;
          this.connectionHandlers.forEach(handler => handler('connected'));
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('WebSocket: Message received', data);
            this.messageHandlers.forEach(handler => handler(data));
          } catch (e) {
            console.error('WebSocket: Failed to parse message', e);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket: Error', error);
          this.errorHandlers.forEach(handler => handler(error));
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket: Closed', event.code, event.reason);
          this.connectionHandlers.forEach(handler => handler('disconnected'));

          // Auto reconnect if enabled
          if (this.autoReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`WebSocket: Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
              this.connect().catch(err => {
                console.error('WebSocket: Reconnection failed', err);
              });
            }, this.reconnectDelay);
          }
        };

      } catch (error) {
        console.error('WebSocket: Connection failed', error);
        reject(error);
      }
    });
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      console.log('WebSocket: Sending message', data);
      this.ws.send(message);
      return true;
    } else {
      console.warn('WebSocket: Cannot send - not connected');
      return false;
    }
  }

  disconnect() {
    if (this.ws) {
      console.log('WebSocket: Disconnecting');
      this.autoReconnect = false;
      this.ws.close();
      this.ws = null;
    }
  }

  onMessage(handler) {
    this.messageHandlers.push(handler);
  }

  onConnection(handler) {
    this.connectionHandlers.push(handler);
  }

  onError(handler) {
    this.errorHandlers.push(handler);
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Make WebSocketClient globally available
if (typeof window !== 'undefined') {
  window.WebSocketClient = WebSocketClient;
}
