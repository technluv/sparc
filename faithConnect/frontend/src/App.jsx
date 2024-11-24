import React, { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [isRecording, setIsRecording] = useState(false)
  const [messages, setMessages] = useState([])
  const [status, setStatus] = useState('')
  const [silenceDetected, setSilenceDetected] = useState(false)
  const [privacyEnabled, setPrivacyEnabled] = useState(true)
  const wsRef = useRef(null)

  useEffect(() => {
    // Initialize WebSocket connection
    wsRef.current = new WebSocket('ws://localhost:8000/ws')

    wsRef.current.onopen = () => {
      setStatus('Connected to server')
    }

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
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
      }
    }

    wsRef.current.onclose = () => {
      setStatus('Disconnected from server')
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const toggleRecording = () => {
    if (!isRecording) {
      wsRef.current.send(JSON.stringify({ action: 'start_recording' }))
      setIsRecording(true)
    } else {
      wsRef.current.send(JSON.stringify({ action: 'stop_recording' }))
      setIsRecording(false)
    }
  }

  const togglePrivacy = () => {
    setPrivacyEnabled(!privacyEnabled)
    wsRef.current.send(JSON.stringify({ 
      action: 'set_privacy',
      enabled: !privacyEnabled 
    }))
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
      .then(() => {
        // Visual feedback could be added here
        const el = document.activeElement
        if (el) {
          el.classList.add('copied')
          setTimeout(() => el.classList.remove('copied'), 1000)
        }
      })
  }

  return (
    <div className="app">
      <header>
        <h1>FaithConnect Meeting Assistant</h1>
        <div className="status-container">
          <p className="status">
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
          </div>
        </div>
      </header>

      <div className="controls">
        <button 
          onClick={toggleRecording}
          className={isRecording ? 'recording' : ''}
        >
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </button>
        <button 
          onClick={togglePrivacy}
          className={`privacy-toggle ${privacyEnabled ? 'enabled' : ''}`}
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
