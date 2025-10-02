import { useState } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import './ChatInterface.css'

const API_URL = 'http://localhost:8000'

function ChatInterface({ messages, setMessages }) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      // ใช้ Orchestrator endpoint แทน
      const response = await axios.post(`${API_URL}/api/orchestrator-chat`, {
        message: input
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        tools_used: response.data.tools_used,
        stop_reason: response.data.stop_reason
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `❌ เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}\n\nกรุณาตรวจสอบว่า Backend API กำลังทำงานอยู่ที่ http://localhost:8000`
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message message-${msg.role}`}>
            {msg.role === 'assistant' && (
              <div className="message-avatar assistant-avatar">AI</div>
            )}
            <div className="message-bubble">
              {msg.tools_used && msg.tools_used.length > 0 && (
                <div className="function-badge">
                  🔧 Tools: {msg.tools_used.join(', ')}
                </div>
              )}
              {msg.detected_function && (
                <div className="function-badge">{msg.detected_function}</div>
              )}
              <div className="message-content">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            </div>
            {msg.role === 'user' && (
              <div className="message-avatar user-avatar">You</div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message message-assistant">
            <div className="message-avatar assistant-avatar">AI</div>
            <div className="message-bubble">
              <div className="message-content loading">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="chat-input-container">
        <div className="input-wrapper">
          <button className="attach-button" title="Attach file">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
            </svg>
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Start typing"
            disabled={loading}
            className="chat-input"
          />
          <button
            className="send-button"
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            title="Send message"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface