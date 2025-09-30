import { useState } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import './RepairManual.css'
import { FaTools } from 'react-icons/fa'
import { IoHelpCircle } from 'react-icons/io5'
import { HiBookOpen } from 'react-icons/hi'
import { BiLoaderAlt } from 'react-icons/bi'

const API_URL = 'http://localhost:8000'

function RepairManual() {
  const [question, setQuestion] = useState('')
  const [conversations, setConversations] = useState([
    {
      question: 'ยินดีต้อนรับ',
      answer: '# 📖 คู่มือการซ่อมบำรุงเครื่องจักร\n\nระบบนี้จะช่วยตอบคำถามเกี่ยวกับการซ่อมบำรุงเครื่องจักรโรงงานน้ำตาล โดยเฉพาะระบบ Feed Mill\n\n**ตัวอย่างคำถาม:**\n- วิธีการเปลี่ยนน้ำมันเกียร์\n- อาการที่แสดงว่า bearing เสียหาย\n- ขั้นตอนการตรวจสอบมอเตอร์\n- วิธีแก้ปัญหาอุณหภูมิสูง\n- การบำรุงรักษาป้องกัน\n\nถามได้เลยครับ!'
    }
  ])
  const [loading, setLoading] = useState(false)

  const askQuestion = async () => {
    if (!question.trim()) return

    setLoading(true)
    setConversations(prev => [...prev, { question, answer: null }])
    const currentQuestion = question
    setQuestion('')

    try {
      const response = await axios.post(`${API_URL}/api/repair-manual`, {
        message: currentQuestion
      })

      setConversations(prev =>
        prev.map((conv, idx) =>
          idx === prev.length - 1
            ? { ...conv, answer: response.data.answer }
            : conv
        )
      )
    } catch (error) {
      setConversations(prev =>
        prev.map((conv, idx) =>
          idx === prev.length - 1
            ? { ...conv, answer: `❌ เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}\n\nกรุณาตรวจสอบว่า Backend API กำลังทำงานอยู่` }
            : conv
        )
      )
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      askQuestion()
    }
  }

  const quickQuestions = [
    'วิธีการเปลี่ยนน้ำมันเกียร์',
    'อาการที่แสดงว่า bearing เสียหาย',
    'ขั้นตอนการตรวจสอบมอเตอร์',
    'วิธีแก้ปัญหาอุณหภูมิสูง',
    'แนวทางการบำรุงรักษาเชิงป้องกัน'
  ]

  return (
    <div className="repair-manual-container">
      <h2><FaTools style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />คู่มือการซ่อมบำรุง</h2>
      <p className="description">
        ถามคำถามเกี่ยวกับการซ่อมบำรุงเครื่องจักรโรงงานน้ำตาล
      </p>

      <div className="quick-questions">
        <strong>คำถามที่ถูกถามบ่อย:</strong>
        <div className="quick-buttons">
          {quickQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => setQuestion(q)}
              className="quick-button"
              disabled={loading}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      <div className="manual-conversations">
        {conversations.map((conv, idx) => (
          <div key={idx} className="conversation-block">
            {conv.question !== 'ยินดีต้อนรับ' && (
              <div className="question-block">
                <div className="question-header">
                  <strong>❓ คำถาม:</strong>
                </div>
                <div className="question-content">{conv.question}</div>
              </div>
            )}

            {conv.answer ? (
              <div className="answer-block">
                <div className="answer-header">
                  <strong>📚 คำตอบ:</strong>
                </div>
                <div className="answer-content">
                  <ReactMarkdown>{conv.answer}</ReactMarkdown>
                </div>
              </div>
            ) : (
              <div className="answer-block loading">
                <div className="answer-header">
                  <strong>📚 กำลังค้นหาคำตอบ...</strong>
                </div>
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="manual-input-container">
        <div className="input-wrapper">
          <button className="attach-button" title="Attach file">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
            </svg>
          </button>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Start typing"
            disabled={loading}
            className="manual-input"
          />
          <button
            className="send-button"
            onClick={askQuestion}
            disabled={loading || !question.trim()}
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

export default RepairManual