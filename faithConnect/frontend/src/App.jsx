import React, { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [isRecording, setIsRecording] = useState(false)
  const [messages, setMessages] = useState([])
  const [status, setStatus] = useState('Connecting...')
  const [silenceDetected, setSilenceDetected] = useState(false)
  const [privacyEnabled, setPrivacyEnabled] = useState(true)
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)

  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      wsRef.current = new WebSocket('ws://localhost:8000/ws')

      wsRef.current.onopen = () => {
        console.log('WebSocket connected')
        setStatus('Connected to server')
        setIsConnected(true)
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current)
          reconnectTimeoutRef.current = null
        }
      }

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('Received message:', data)
          
          if (data.type === 'status') {
            setStatus(data.message)
            if (data.message.includes('silence')) {
              setSilenceDetected(true)
              setTimeout(() => setSilenceDetected(false), 2000)
            }
          } else if (data.type === 'analysis') {
            setMessages(prev => [...prev, {
              transcript: data.transcript,
              analysis: JSON.parse(data.analysis.analysis),
              timestamp: new Date().toLocaleTimeString()
            }])
          } else if (data.type === 'error') {
            console.error('Server error:', data.message)
            setStatus(`Error: ${data.message}`)
          }
        } catch (error) {
          console.error('Error parsing message:', error)
        }
      }

      wsRef.current.onclose = (event) => {
        console.log('WebSocket closed:', event)
        setStatus('Disconnected from server - Reconnecting...')
        setIsConnected(false)
        // Attempt to reconnect after 2 seconds
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 2000)
      }

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setStatus('Connection error - Retrying...')
      }
    } catch (error) {
      console.error('Error creating WebSocket:', error)
      setStatus('Failed to create WebSocket connection')
    }
  }

  useEffect(() => {
    connectWebSocket()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [])

  const toggleRecording = () => {
    if (!isConnected) {
      setStatus('Cannot start recording - Not connected to server')
      return
    }

    try {
      if (!isRecording) {
        wsRef.current.send(JSON.stringify({ action: 'start_recording' }))
        setIsRecording(true)
      } else {
        wsRef.current.send(JSON.stringify({ action: 'stop_recording' }))
        setIsRecording(false)
      }
    } catch (error) {
      console.error('Error sending command:', error)
      setStatus('Error sending command to server')
    }
  }

  const togglePrivacy = () => {
    if (!isConnected) {
      setStatus('Cannot toggle privacy - Not connected to server')
      return
    }

    try {
      setPrivacyEnabled(!privacyEnabled)
      wsRef.current.send(JSON.stringify({ 
        action: 'set_privacy',
        enabled: !privacyEnabled 
      }))
    } catch (error) {
      console.error('Error toggling privacy:', error)
      setStatus('Error toggling privacy mode')
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
      .then(() => {
        const el = document.activeElement
        if (el) {
          el.classList.add('copied')
          setTimeout(() => el.classList.remove('copied'), 1000)
        }
      })
      .catch(error => {
        console.error('Error copying to clipboard:', error)
        setStatus('Error copying to clipboard')
      })
  }

  return (
    <div className="app">
      <header>
        <h1>FaithConnect Meeting Assistant</h1>
        <div className="status-container">
          <p className={`status ${!isConnected ? 'disconnected' : ''}`}>
            {status}
            {silenceDetected && <span className="silence-indicator">Silence Detected</span>}
          </p>
          <div className="status-indicators">
            <div className={`indicator ${isRecording ? 'active' : ''}`}>
              Recording
            </div>
            <div className={`indicator ${privacyEnabled ? 'active' : ''}`}>
              Privacy Mode
            </div>
            <div className={`indicator ${isConnected ? 'active' : ''}`}>
              Server Connection
            </div>
          </div>
        </div>
      </header>

      <div className="controls">
        <button 
          onClick={toggleRecording}
          className={`${isRecording ? 'recording' : ''} ${!isConnected ? 'disabled' : ''}`}
          disabled={!isConnected}
        >
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </button>
        <button 
          onClick={togglePrivacy}
          className={`privacy-toggle ${privacyEnabled ? 'enabled' : ''} ${!isConnected ? 'disabled' : ''}`}
          disabled={!isConnected}
        >
          {privacyEnabled ? 'Privacy Mode On' : 'Privacy Mode Off'}
        </button>
      </div>

      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className="message">
            <div className="message-header">
              <span className="timestamp">{msg.timestamp}</span>
            </div>
            <div className="transcript">
              <h3>Transcript:</h3>
              <p>{msg.transcript}</p>
            </div>
            <div className="analysis">
              <h3>Analysis:</h3>
              <div className="topics">
                <h4>Key Topics & Concerns:</h4>
                <ul>
                  {msg.analysis.topics?.map((topic, i) => (
                    <li key={i}>{topic}</li>
                  ))}
                </ul>
              </div>
              <div className="suggestions">
                <h4>Suggested Responses:</h4>
                <div className="quick-responses">
                  {msg.analysis.suggestions?.map((suggestion, i) => (
                    <button 
                      key={i} 
                      className="response-option"
                      onClick={() => copyToClipboard(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
              <div className="insights">
                <h4>Communication Insights:</h4>
                <ul>
                  {msg.analysis.insights?.map((insight, i) => (
                    <li key={i}>{insight}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
