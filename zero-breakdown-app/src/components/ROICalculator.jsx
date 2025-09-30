import { useState } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import './ROICalculator.css'
import { FaCalculator } from 'react-icons/fa'
import { MdAnalytics } from 'react-icons/md'
import { BiLoaderAlt } from 'react-icons/bi'
import { IoCheckmarkCircle, IoWarning } from 'react-icons/io5'

const API_URL = 'http://localhost:8000'

function ROICalculator() {
  const [formData, setFormData] = useState({
    current_health_percentage: 70,
    comparison_health_percentage: 50,
    repair_cost: 50000,
    daily_production_value: 100000
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: parseFloat(value) || 0 }))
  }

  const calculateROI = async () => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_URL}/api/calculate-roi`, formData)
      setResult(response.data)
    } catch (error) {
      alert(`เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="roi-calculator-container">
      <h2><FaCalculator style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />คำนวณ ROI (Return on Investment)</h2>
      <p className="description">
        เปรียบเทียบผลตอบแทนของการซ่อมเครื่องจักรในช่วงเวลาต่างๆ
      </p>

      <div className="form-section">
        <div className="form-row">
          <label>
            <strong>สุขภาพเครื่องจักรปัจจุบัน (%):</strong>
            <input
              type="number"
              min="0"
              max="100"
              step="1"
              value={formData.current_health_percentage}
              onChange={(e) => handleInputChange('current_health_percentage', e.target.value)}
            />
            <small>0-100% (100% = สภาพดีที่สุด)</small>
          </label>

          <label>
            <strong>สุขภาพเครื่องจักรเปรียบเทียบ (%):</strong>
            <input
              type="number"
              min="0"
              max="100"
              step="1"
              value={formData.comparison_health_percentage}
              onChange={(e) => handleInputChange('comparison_health_percentage', e.target.value)}
            />
            <small>ถ้าซ่อมตอนที่ค่านี้</small>
          </label>
        </div>

        <div className="form-row">
          <label>
            <strong>ค่าใช้จ่ายในการซ่อม (บาท):</strong>
            <input
              type="number"
              min="0"
              step="1000"
              value={formData.repair_cost}
              onChange={(e) => handleInputChange('repair_cost', e.target.value)}
            />
          </label>

          <label>
            <strong>มูลค่าการผลิตต่อวัน (บาท):</strong>
            <input
              type="number"
              min="0"
              step="1000"
              value={formData.daily_production_value}
              onChange={(e) => handleInputChange('daily_production_value', e.target.value)}
            />
          </label>
        </div>

        <button onClick={calculateROI} disabled={loading} className="btn-calculate">
          {loading ? (
            <><BiLoaderAlt className="spin-icon" /> กำลังคำนวณ...</>
          ) : (
            <><FaCalculator style={{ marginRight: '0.5rem' }} /> คำนวณ ROI</>
          )}
        </button>
      </div>

      {result && (
        <div className="result-section">
          <h3><MdAnalytics style={{ marginRight: '0.5rem' }} />ผลการคำนวณ ROI</h3>

          <div className="comparison-grid">
            <div className="scenario-box current">
              <h4>🔹 สถานการณ์ปัจจุบัน ({result.current_scenario.health_percentage}%)</h4>
              <div className="stat-row">
                <span>วันก่อนเสียหาย:</span>
                <strong>{result.current_scenario.days_until_breakdown} วัน</strong>
              </div>
              <div className="stat-row">
                <span>การสูญเสีย:</span>
                <strong className="loss">{result.current_scenario.production_loss.toLocaleString()} บาท</strong>
              </div>
            </div>

            <div className="scenario-box comparison">
              <h4>🔸 สถานการณ์เปรียบเทียบ ({result.comparison_scenario.health_percentage}%)</h4>
              <div className="stat-row">
                <span>วันก่อนเสียหาย:</span>
                <strong>{result.comparison_scenario.days_until_breakdown} วัน</strong>
              </div>
              <div className="stat-row">
                <span>การสูญเสีย:</span>
                <strong className="loss">{result.comparison_scenario.production_loss.toLocaleString()} บาท</strong>
              </div>
            </div>
          </div>

          <div className="roi-summary">
            <div className="roi-box">
              <div className="roi-stat">
                <label>ค่าซ่อม:</label>
                <span className="cost">{result.repair_cost.toLocaleString()} บาท</span>
              </div>
              <div className="roi-stat">
                <label>เงินที่ประหยัดได้:</label>
                <span className={result.savings >= 0 ? 'savings' : 'loss'}>
                  {result.savings.toLocaleString()} บาท
                </span>
              </div>
              <div className="roi-stat highlight">
                <label>ROI:</label>
                <span className={result.roi_percentage >= 0 ? 'positive' : 'negative'}>
                  {result.roi_percentage.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>

          <div className="analysis-box">
            <h4>💡 การวิเคราะห์และคำแนะนำ:</h4>
            <ReactMarkdown>{result.analysis}</ReactMarkdown>
          </div>

          <div className="recommendation-badge">
            {result.roi_percentage > 0 ? (
              <div className="badge-positive">
                <IoCheckmarkCircle style={{ marginRight: '0.5rem' }} />คุ้มค่าที่จะซ่อมตอนนี้ (ROI เป็นบวก)
              </div>
            ) : (
              <div className="badge-negative">
                <IoWarning style={{ marginRight: '0.5rem' }} />อาจไม่คุ้มค่าที่จะซ่อมตอนนี้ (ROI เป็นลบ)
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ROICalculator