import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [isListening, setIsListening] = useState(false)
  const [messages, setMessages] = useState([])
  const [error, setError] = useState(null)
  const [status, setStatus] = useState('disconnected')
  const [debug, setDebug] = useState([])
  
  const websocket = useRef(null)
  const mediaRecorder = useRef(null)
  const audioChunks = useRef([])
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const addDebugMessage = (message) => {
    console.log(message)
    setDebug(prev => [...prev, `${new Date().toISOString()}: ${message}`])
  }

  const connectWebSocket = () => {
    if (websocket.current?.readyState === WebSocket.OPEN) {
      addDebugMessage('WebSocket already connected')
      return
    }

    addDebugMessage('Connecting to WebSocket...')
    websocket.current = new WebSocket('ws://localhost:8000/ws')

    websocket.current.onopen = () => {
      addDebugMessage('WebSocket connected')
      setStatus('connected')
      reconnectAttempts.current = 0
    }

    websocket.current.onclose = () => {
      addDebugMessage('WebSocket disconnected')
      setStatus('disconnected')
      if (isListening) {
        handleReconnect()
      }
    }

    websocket.current.onerror = (error) => {
      addDebugMessage(`WebSocket error: ${error.message}`)
      setError(`Connection error: ${error.message}`)
    }

    websocket.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.error) {
        addDebugMessage(`Server error: ${data.error}`)
        setError(data.error)
      } else {
        addDebugMessage('Received transcription and analysis')
        setMessages(prev => [...prev, {
          transcription: data.transcription,
          analysis: data.analysis,
          timestamp: new Date().toISOString()
        }])
      }
    }
  }

  const handleReconnect = () => {
    if (reconnectAttempts.current >= maxReconnectAttempts) {
      addDebugMessage('Max reconnection attempts reached')
      setError('Unable to reconnect to server')
      setIsListening(false)
      return
    }

    reconnectAttempts.current++
    addDebugMessage(`Reconnection attempt ${reconnectAttempts.current}/${maxReconnectAttempts}`)
    setTimeout(connectWebSocket, 1000 * reconnectAttempts.current)
  }

  const startListening = async () => {
    try {
      addDebugMessage('Requesting microphone access')
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      })
      
      connectWebSocket()
      
      mediaRecorder.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      })
      
      mediaRecorder.current.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data)
          addDebugMessage('Audio chunk received')
          
          // Convert to WAV and send
          const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' })
          const reader = new FileReader()
          
          reader.onloadend = () => {
            if (websocket.current?.readyState === WebSocket.OPEN) {
              addDebugMessage('Sending audio data')
              websocket.current.send(JSON.stringify({
                audio: reader.result
              }))
            } else {
              addDebugMessage(`WebSocket not ready: ${websocket.current?.readyState}`)
            }
          }
          
          reader.readAsDataURL(audioBlob)
          audioChunks.current = []
        }
      }
      
      mediaRecorder.current.start(1000) // Capture audio every second
      addDebugMessage('Started recording')
      setIsListening(true)
      setError(null)
      
    } catch (err) {
      const errorMsg = `Error accessing microphone: ${err.message}`
      addDebugMessage(errorMsg)
      setError(errorMsg)
      setIsListening(false)
    }
  }

  const stopListening = () => {
    addDebugMessage('Stopping recording')
    if (mediaRecorder.current) {
      mediaRecorder.current.stop()
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop())
    }
    if (websocket.current) {
      websocket.current.close()
    }
    setIsListening(false)
  }

  useEffect(() => {
    return () => {
      if (mediaRecorder.current) {
        mediaRecorder.current.stream.getTracks().forEach(track => track.stop())
      }
      if (websocket.current) {
        websocket.current.close()
      }
    }
  }, [])

  return (
    <div className="app">
      <header>
        <h1>Real-time Audio Analysis</h1>
        <div className="controls">
          <div className={`status-indicator ${status}`} title={`Status: ${status}`} />
          <button 
            onClick={isListening ? stopListening : startListening}
            className={isListening ? 'active' : ''}
          >
            {isListening ? 'Stop Listening' : 'Start Listening'}
          </button>
        </div>
      </header>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
          <button className="close-error" onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="debug-panel">
        <div className="debug-header">
          <h3>Debug Log</h3>
          <button onClick={() => setDebug([])}>Clear</button>
        </div>
        <div className="debug-log">
          {debug.map((log, index) => (
            <div key={index} className="debug-entry">{log}</div>
          ))}
        </div>
      </div>

      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className="message">
            <div className="transcription">
              <strong>Transcription:</strong> {msg.transcription}
            </div>
            <div className="analysis">
              <div><strong>Topic:</strong> {msg.analysis.topic}</div>
              <div><strong>Concerns:</strong> {msg.analysis.concerns}</div>
              <div><strong>Suggestion:</strong> {msg.analysis.suggestion}</div>
            </div>
            <div className="timestamp">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
