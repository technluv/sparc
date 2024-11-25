import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [isListening, setIsListening] = useState(false)
  const [messages, setMessages] = useState([])
  const [error, setError] = useState(null)
  const websocket = useRef(null)
  const mediaRecorder = useRef(null)
  const audioChunks = useRef([])

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (websocket.current) {
        websocket.current.close()
      }
      if (mediaRecorder.current) {
        mediaRecorder.current.stop()
      }
    }
  }, [])

  const startListening = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Setup WebSocket connection
      websocket.current = new WebSocket('ws://localhost:8000/ws')
      
      websocket.current.onopen = () => {
        // Setup MediaRecorder
        mediaRecorder.current = new MediaRecorder(stream)
        
        mediaRecorder.current.ondataavailable = async (event) => {
          audioChunks.current.push(event.data)
          
          // Convert to base64 and send to server
          const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' })
          const reader = new FileReader()
          
          reader.onloadend = () => {
            if (websocket.current.readyState === WebSocket.OPEN) {
              websocket.current.send(JSON.stringify({
                audio: reader.result
              }))
            }
          }
          
          reader.readAsDataURL(audioBlob)
          audioChunks.current = []
        }
        
        // Start recording in chunks
        mediaRecorder.current.start(1000) // Send audio every second
        setIsListening(true)
        setError(null)
      }
      
      websocket.current.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.error) {
          setError(data.error)
        } else {
          setMessages(prev => [...prev, {
            transcription: data.transcription,
            analysis: data.analysis,
            timestamp: new Date().toISOString()
          }])
        }
      }
      
      websocket.current.onerror = (error) => {
        setError('WebSocket error: ' + error.message)
        setIsListening(false)
      }
      
      websocket.current.onclose = () => {
        setIsListening(false)
      }
      
    } catch (err) {
      setError('Error accessing microphone: ' + err.message)
      setIsListening(false)
    }
  }

  const stopListening = () => {
    if (mediaRecorder.current) {
      mediaRecorder.current.stop()
    }
    if (websocket.current) {
      websocket.current.close()
    }
    setIsListening(false)
  }

  return (
    <div className="app">
      <header>
        <h1>Real-time Audio Analysis</h1>
        <button 
          onClick={isListening ? stopListening : startListening}
          className={isListening ? 'active' : ''}
        >
          {isListening ? 'Stop Listening' : 'Start Listening'}
        </button>
      </header>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

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
