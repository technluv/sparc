import React, { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [isRecording, setIsRecording] = useState(false)
  const [messages, setMessages] = useState([])
  const [status, setStatus] = useState('')
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
      } else if (data.type === 'analysis') {
        setMessages(prev => [...prev, {
          transcript: data.transcript,
          analysis: JSON.parse(data.analysis.analysis)
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

  return (
    <div className="app">
      <header>
        <h1>FaithConnect Meeting Assistant</h1>
        <p className="status">{status}</p>
      </header>

      <div className="controls">
        <button 
          onClick={toggleRecording}
          className={isRecording ? 'recording' : ''}
        >
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </button>
      </div>

      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className="message">
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
                <ul>
                  {msg.analysis.suggestions?.map((suggestion, i) => (
                    <li key={i}>{suggestion}</li>
                  ))}
                </ul>
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
