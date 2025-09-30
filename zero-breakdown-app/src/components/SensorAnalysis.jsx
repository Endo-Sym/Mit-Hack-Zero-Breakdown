import { useState } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import './SensorAnalysis.css'
import { MdAnalytics } from 'react-icons/md'
import { IoSearch, IoCheckmarkCircle, IoWarning } from 'react-icons/io5'
import { BiLoaderAlt } from 'react-icons/bi'
import { GiCrystalBall } from 'react-icons/gi'

const API_URL = 'http://localhost:8000'

function SensorAnalysis() {
  const [machineType, setMachineType] = useState('Feed Mill 1')
  const [sensorData, setSensorData] = useState({
    PowerMotor: 295,
    CurrentMotor: 300,
    TempBrassBearingDE: 65,
    SpeedMotor: 1485,
    SpeedRoller: 5.5,
    TempOilGear: 60,
    TempBearingMotorNDE: 70,
    TempWindingMotorPhase_U: 100,
    TempWindingMotorPhase_V: 98,
    TempWindingMotorPhase_W: 97,
    Vibration: 1.5
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [predictionResult, setPredictionResult] = useState(null)

  const handleInputChange = (field, value) => {
    setSensorData(prev => ({ ...prev, [field]: parseFloat(value) || 0 }))
  }

  const analyzeSensors = async () => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_URL}/api/analyze-sensors`, {
        timestamp: new Date().toISOString(),
        machine_type: machineType,
        sensor_readings: sensorData
      })
      setResult(response.data)
    } catch (error) {
      alert(`เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const predictBreakdown = async () => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_URL}/api/predict-breakdown`, {
        timestamp: new Date().toISOString(),
        machine_type: machineType,
        sensor_readings: sensorData
      })
      setPredictionResult(response.data)
    } catch (error) {
      alert(`เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="sensor-analysis-container">
      <h2><MdAnalytics style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />วิเคราะห์ข้อมูล Sensor</h2>

      <div className="form-section">
        <label>
          <strong>ประเภทเครื่องจักร:</strong>
          <input
            type="text"
            value={machineType}
            onChange={(e) => setMachineType(e.target.value)}
            placeholder="Feed Mill 1"
          />
        </label>

        <div className="sensor-grid">
          <label>
            PowerMotor (kW):
            <input
              type="number"
              step="0.1"
              value={sensorData.PowerMotor}
              onChange={(e) => handleInputChange('PowerMotor', e.target.value)}
            />
            <small>ปกติ: 280-320</small>
          </label>

          <label>
            CurrentMotor (Amp):
            <input
              type="number"
              step="0.1"
              value={sensorData.CurrentMotor}
              onChange={(e) => handleInputChange('CurrentMotor', e.target.value)}
            />
            <small>ปกติ: 270-330</small>
          </label>

          <label>
            TempBrassBearingDE (°C):
            <input
              type="number"
              step="0.1"
              value={sensorData.TempBrassBearingDE}
              onChange={(e) => handleInputChange('TempBrassBearingDE', e.target.value)}
            />
            <small>ปกติ: &lt;75</small>
          </label>

          <label>
            SpeedMotor (rpm):
            <input
              type="number"
              step="0.1"
              value={sensorData.SpeedMotor}
              onChange={(e) => handleInputChange('SpeedMotor', e.target.value)}
            />
            <small>ปกติ: 1470-1500</small>
          </label>

          <label>
            SpeedRoller (rpm):
            <input
              type="number"
              step="0.1"
              value={sensorData.SpeedRoller}
              onChange={(e) => handleInputChange('SpeedRoller', e.target.value)}
            />
          </label>

          <label>
            TempOilGear (°C):
            <input
              type="number"
              step="0.1"
              value={sensorData.TempOilGear}
              onChange={(e) => handleInputChange('TempOilGear', e.target.value)}
            />
            <small>ปกติ: &lt;65</small>
          </label>

          <label>
            TempBearingMotorNDE (°C):
            <input
              type="number"
              step="0.1"
              value={sensorData.TempBearingMotorNDE}
              onChange={(e) => handleInputChange('TempBearingMotorNDE', e.target.value)}
            />
            <small>ปกติ: &lt;75</small>
          </label>

          <label>
            TempWindingMotorPhase_U (°C):
            <input
              type="number"
              step="0.1"
              value={sensorData.TempWindingMotorPhase_U}
              onChange={(e) => handleInputChange('TempWindingMotorPhase_U', e.target.value)}
            />
            <small>ปกติ: &lt;115</small>
          </label>

          <label>
            TempWindingMotorPhase_V (°C):
            <input
              type="number"
              step="0.1"
              value={sensorData.TempWindingMotorPhase_V}
              onChange={(e) => handleInputChange('TempWindingMotorPhase_V', e.target.value)}
            />
            <small>ปกติ: &lt;115</small>
          </label>

          <label>
            TempWindingMotorPhase_W (°C):
            <input
              type="number"
              step="0.1"
              value={sensorData.TempWindingMotorPhase_W}
              onChange={(e) => handleInputChange('TempWindingMotorPhase_W', e.target.value)}
            />
            <small>ปกติ: &lt;115</small>
          </label>

          <label>
            Vibration (mm/s):
            <input
              type="number"
              step="0.01"
              value={sensorData.Vibration}
              onChange={(e) => handleInputChange('Vibration', e.target.value)}
            />
            <small>ดี: &lt;1.8</small>
          </label>
        </div>

        <div className="button-group">
          <button onClick={analyzeSensors} disabled={loading}>
            {loading ? (
              <><BiLoaderAlt className="spin-icon" /> กำลังวิเคราะห์...</>
            ) : (
              <><IoSearch style={{ marginRight: '0.5rem' }} /> วิเคราะห์ Sensor</>
            )}
          </button>
          <button onClick={predictBreakdown} disabled={loading} className="btn-predict">
            {loading ? (
              <><BiLoaderAlt className="spin-icon" /> กำลังทำนาย...</>
            ) : (
              <><GiCrystalBall style={{ marginRight: '0.5rem' }} /> ทำนาย Zero Breakdown</>
            )}
          </button>
        </div>
      </div>

      {result && (
        <div className="result-section">
          <h3><MdAnalytics style={{ marginRight: '0.5rem' }} />ผลการวิเคราะห์</h3>

          {result.alerts.length > 0 ? (
            <div className="alerts-box">
              <h4><IoWarning style={{ marginRight: '0.5rem' }} />แจ้งเตือน ({result.alerts.length} รายการ)</h4>
              <ul>
                {result.alerts.map((alert, idx) => (
                  <li key={idx}>{alert}</li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="success-box">
              <p><IoCheckmarkCircle style={{ marginRight: '0.5rem' }} />เครื่องจักรทำงานปกติ ไม่พบความผิดปกติ</p>
            </div>
          )}

          <div className="recommendation-box">
            <h4><MdAnalytics style={{ marginRight: '0.5rem' }} />คำแนะนำ:</h4>
            <ReactMarkdown>{result.recommended_action}</ReactMarkdown>
          </div>
        </div>
      )}

      {predictionResult && (
        <div className="result-section prediction-result">
          <h3><GiCrystalBall style={{ marginRight: '0.5rem' }} />ผลการทำนาย Zero Breakdown</h3>

          <div className="risk-score-box">
            <div className={`risk-badge risk-${predictionResult.risk_level}`}>
              <div className="risk-score">{predictionResult.risk_score}/100</div>
              <div className="risk-label">ระดับความเสี่ยง: {predictionResult.risk_level}</div>
            </div>
          </div>

          <div className="prediction-box">
            <h4><MdAnalytics style={{ marginRight: '0.5rem' }} />การทำนาย:</h4>
            <ReactMarkdown>{predictionResult.prediction}</ReactMarkdown>
          </div>

          {predictionResult.alerts.length > 0 && (
            <div className="alerts-box">
              <h4><IoWarning style={{ marginRight: '0.5rem' }} />ปัญหาที่พบ:</h4>
              <ul>
                {predictionResult.alerts.map((alert, idx) => (
                  <li key={idx}>{alert}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default SensorAnalysis