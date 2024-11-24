import React, { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [isRecording, setIsRecording] = useState(false)
  const [messages, setMessages] = useState([])
  const [status, setStatus] = useState('Connecting...')
  const [silenceDetected, setSilenceDetected] = useState(false)
  const [privacyEnabled, setPrivacyEnabled] = useState(true)
  const [isConnected, setIsConnected] = useState(false)
  const [audioDeviceAvailable, setAudioDeviceAvailable] = useState(false)
  const [error, setError] = useState('')
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)

  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8001/ws'

  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      console.log('Connecting to WebSocket at:', WS_URL)
      wsRef.current = new WebSocket(WS_URL)

      wsRef.current.onopen = () => {
        console.log('WebSocket connected')
        setStatus('Connected to server')
        setIsConnected(true)
        setError('')
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
            if (data.audio_status) {
              setAudioDeviceAvailable(data.audio_status.audio_device_available)
              if (!data.audio_status.audio_device_available) {
                setError('No audio device available. Please check your microphone settings.')
              }
            }
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
            setError(data.message)
            if (data.message.includes('audio device') || data.message.includes('microphone')) {
              setAudioDeviceAvailable(false)
              setIsRecording(false)
            }
          }
        } catch (error) {
          console.error('Error parsing message:', error)
          setError('Error processing server message')
        }
      }

      wsRef.current.onclose = (event) => {
        console.log('WebSocket closed:', event)
        setStatus('Disconnected from server - Reconnecting...')
        setIsConnected(false)
        setAudioDeviceAvailable(false)
        // Attempt to reconnect after 2 seconds
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 2000)
      }

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setStatus('Connection error - Retrying...')
        setError('Connection error occurred')
      }
    } catch (error) {
      console.error('Error creating WebSocket:', error)
      setStatus('Failed to create WebSocket connection')
      setError('Failed to connect to server')
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
      setError('Cannot start recording - Not connected to server')
      return
    }

    if (!audioDeviceAvailable && !isRecording) {
      setError('Cannot start recording - No audio device available')
      return
    }

    try {
      if (!isRecording) {
        wsRef.current.send(JSON.stringify({ action: 'start_recording' }))
        setIsRecording(true)
        setError('')
      } else {
        wsRef.current.send(JSON.stringify({ action: 'stop_recording' }))
        setIsRecording(false)
      }
    } catch (error) {
      console.error('Error sending command:', error)
      setError('Error sending command to server')
    }
  }

  const togglePrivacy = () => {
    if (!isConnected) {
      setError('Cannot toggle privacy - Not connected to server')
      return
    }

    try {
      setPrivacyEnabled(!privacyEnabled)
      wsRef.current.send(JSON.stringify({ 
        action: 'set_privacy',
        enabled: !privacyEnabled 
      }))
      setError('')
    } catch (error) {
      console.error('Error toggling privacy:', error)
      setError('Error toggling privacy mode')
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
        setError('Error copying to clipboard')
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
          {error && <p className="error-message">{error}</p>}
          {!audioDeviceAvailable && isConnected && (
            <p className="device-warning">
              No audio device detected. Please connect a microphone to use recording features.
            </p>
          )}
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
            <div className={`indicator ${audioDeviceAvailable ? 'active' : ''}`}>
              Audio Device
            </div>
          </div>
        </div>
      </header>

      <div className="controls">
        <button 
          onClick={toggleRecording}
          className={`${isRecording ? 'recording' : ''} ${!isConnected || (!audioDeviceAvailable && !isRecording) ? 'disabled' : ''}`}
          disabled={!isConnected || (!audioDeviceAvailable && !isRecording)}
          title={!audioDeviceAvailable ? 'No audio device available' : ''}
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
