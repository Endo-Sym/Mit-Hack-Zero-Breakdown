import { useState, useEffect } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts'
import './SensorAnalysis.css'
import { MdAnalytics, MdOutlineFactory, MdUploadFile } from 'react-icons/md'
import { IoSearch, IoCheckmarkCircle, IoWarning, IoRefresh } from 'react-icons/io5'
import { BiLoaderAlt } from 'react-icons/bi'
import { GiCrystalBall } from 'react-icons/gi'
import { FaTable, FaChartLine } from 'react-icons/fa'

const API_URL = 'http://localhost:8000'

// Threshold values for sensors
const THRESHOLDS = {
  PowerMotor: { min: 290, max: 315, unit: 'kW' },
  CurrentMotor: { min: 280, max: 320, unit: 'Amp' },
  TempBrassBearingDE: { max: 75, unit: '°C' },
  TempBearingMotorNDE: { max: 75, unit: '°C' },
  SpeedMotor: { min: 1470, max: 1500, unit: 'rpm' },
  TempOilGear: { max: 65, unit: '°C' },
  TempWindingMotorPhase_U: { max: 105, unit: '°C' },
  TempWindingMotorPhase_V: { max: 105, unit: '°C' },
  TempWindingMotorPhase_W: { max: 105, unit: '°C' },
  Vibration: { max: 1.8, unit: 'mm/s' }
}

function SensorAnalysis() {
  // Load from localStorage on mount
  const [uploadedCSV, setUploadedCSV] = useState(() => {
    const saved = localStorage.getItem('sensorAnalysisCSV')
    return saved ? JSON.parse(saved) : null
  })
  const [csvData, setCSVData] = useState(() => {
    const saved = localStorage.getItem('sensorAnalysisData')
    return saved ? JSON.parse(saved) : []
  })
  const [selectedRow, setSelectedRow] = useState(() => {
    const saved = localStorage.getItem('sensorAnalysisSelectedRow')
    return saved ? JSON.parse(saved) : null
  })

  const [uploading, setUploading] = useState(false)
  const [viewMode, setViewMode] = useState('table') // 'table' or 'chart'
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [predictionResult, setPredictionResult] = useState(null)

  // Save to localStorage whenever data changes
  useEffect(() => {
    if (uploadedCSV) {
      localStorage.setItem('sensorAnalysisCSV', JSON.stringify(uploadedCSV))
    }
  }, [uploadedCSV])

  useEffect(() => {
    if (csvData.length > 0) {
      localStorage.setItem('sensorAnalysisData', JSON.stringify(csvData))
    }
  }, [csvData])

  useEffect(() => {
    if (selectedRow) {
      localStorage.setItem('sensorAnalysisSelectedRow', JSON.stringify(selectedRow))
    }
  }, [selectedRow])

  const handleCSVUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('custom_name', `sensor_analysis_${Date.now()}`)

    try {
      const response = await axios.post(`${API_URL}/api/upload-csv`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setUploadedCSV({
        filename: response.data.saved_file,
        total_rows: response.data.total_rows,
        machines: response.data.machines,
        date_range: response.data.date_range
      })

      // Fetch and display data
      fetchCSVData(response.data.machines[0])
    } catch (error) {
      alert(`เกิดข้อผิดพลาดในการอัพโหลด: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploading(false)
    }
  }

  const fetchCSVData = async (machineId) => {
    try {
      const response = await axios.get(`${API_URL}/api/machine-data/${machineId}`, {
        params: { limit: 10 }
      })

      // Transform data for table/chart display
      const transformedData = [{
        timestamp: response.data.timestamp,
        machine_id: response.data.machine_id,
        ...response.data.sensor_readings
      }]

      setCSVData(transformedData)
      setSelectedRow(transformedData[0])
    } catch (error) {
      console.error('Error fetching CSV data:', error)
    }
  }

  const handleCellEdit = (field, value) => {
    setSelectedRow(prev => ({
      ...prev,
      [field]: parseFloat(value) || 0
    }))
  }

  const analyzeSensors = async () => {
    if (!selectedRow) {
      alert('กรุณาเลือกข้อมูลที่ต้องการวิเคราะห์')
      return
    }

    setLoading(true)
    try {
      const sensorReadings = { ...selectedRow }
      delete sensorReadings.timestamp
      delete sensorReadings.machine_id

      const response = await axios.post(`${API_URL}/api/analyze-sensors`, {
        timestamp: new Date().toISOString(),
        machine_type: selectedRow.machine_id || 'Feed Mill 1',
        sensor_readings: sensorReadings
      })
      setResult(response.data)
    } catch (error) {
      alert(`เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const predictBreakdown = async () => {
    if (!selectedRow) {
      alert('กรุณาเลือกข้อมูลที่ต้องการทำนาย')
      return
    }

    setLoading(true)
    try {
      const sensorReadings = { ...selectedRow }
      delete sensorReadings.timestamp
      delete sensorReadings.machine_id

      // Use ML Model endpoint
      const response = await axios.post(`${API_URL}/api/predict-ml-breakdown`, {
        timestamp: new Date().toISOString(),
        machine_type: selectedRow.machine_id || 'Feed Mill 1',
        sensor_readings: sensorReadings
      })
      setPredictionResult(response.data)
    } catch (error) {
      alert(`เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const checkThreshold = (field, value) => {
    const threshold = THRESHOLDS[field]
    if (!threshold) return 'normal'

    if (threshold.min && value < threshold.min) return 'warning'
    if (threshold.max && value > threshold.max) return 'warning'
    return 'normal'
  }

  const prepareChartData = () => {
    if (!selectedRow) return []

    return Object.entries(selectedRow)
      .filter(([key]) => key !== 'timestamp' && key !== 'machine_id')
      .map(([key, value]) => ({
        name: key.replace(/([A-Z])/g, ' $1').trim(),
        value: value,
        threshold: THRESHOLDS[key]?.max || THRESHOLDS[key]?.min || null
      }))
  }

  return (
    <div className="sensor-analysis-container">
      <h2><MdAnalytics style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />วิเคราะห์ข้อมูล Sensor</h2>

      {/* CSV Upload Section */}
      <div className="csv-upload-section glass-panel">
        <h3><MdUploadFile style={{ marginRight: '0.5rem' }} />อัพโหลดข้อมูล CSV</h3>
        <div className="upload-area">
          <input
            type="file"
            accept=".csv"
            onChange={handleCSVUpload}
            disabled={uploading}
            id="csv-upload"
            style={{ display: 'none' }}
          />
          <label htmlFor="csv-upload" className={`upload-button ${uploading ? 'disabled' : ''}`}>
            {uploading ? (
              <><BiLoaderAlt className="spin-icon" /> กำลังอัพโหลด...</>
            ) : (
              <><MdUploadFile /> เลือกไฟล์ CSV</>
            )}
          </label>
          {uploadedCSV && (
            <div className="upload-info">
              <IoCheckmarkCircle style={{ color: '#4ade80' }} />
              <span>
                อัพโหลดสำเร็จ: {uploadedCSV.total_rows} แถว |
                เครื่องจักร: {uploadedCSV.machines.join(', ')} |
                ช่วงเวลา: {uploadedCSV.date_range}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Data Display Section */}
      {selectedRow && (
        <>
          <div className="view-toggle glass-panel">
            <button
              className={viewMode === 'table' ? 'active' : ''}
              onClick={() => setViewMode('table')}
            >
              <FaTable /> ตาราง
            </button>
            <button
              className={viewMode === 'chart' ? 'active' : ''}
              onClick={() => setViewMode('chart')}
            >
              <FaChartLine /> กราฟ
            </button>
          </div>

          {viewMode === 'table' ? (
            <div className="data-table-section glass-panel">
              <h3><FaTable style={{ marginRight: '0.5rem' }} />ข้อมูล Sensor (แก้ไขได้)</h3>
              <div className="sensor-table">
                <table>
                  <thead>
                    <tr>
                      <th>Sensor</th>
                      <th>ค่าปัจจุบัน</th>
                      <th>ค่าปกติ</th>
                      <th>สถานะ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(selectedRow)
                      .filter(([key]) => key !== 'timestamp' && key !== 'machine_id')
                      .map(([key, value]) => {
                        const threshold = THRESHOLDS[key]
                        const status = checkThreshold(key, value)
                        return (
                          <tr key={key} className={status}>
                            <td>{key.replace(/([A-Z])/g, ' $1').trim()}</td>
                            <td>
                              <input
                                type="number"
                                step="0.1"
                                value={value}
                                onChange={(e) => handleCellEdit(key, e.target.value)}
                                className="editable-cell"
                              />
                              {threshold?.unit && <span className="unit"> {threshold.unit}</span>}
                            </td>
                            <td>
                              {threshold?.min && threshold?.max
                                ? `${threshold.min} - ${threshold.max}`
                                : threshold?.max
                                ? `< ${threshold.max}`
                                : threshold?.min
                                ? `> ${threshold.min}`
                                : '-'}
                            </td>
                            <td>
                              {status === 'warning' ? (
                                <span className="status-badge warning">
                                  <IoWarning /> เกินค่า
                                </span>
                              ) : (
                                <span className="status-badge normal">
                                  <IoCheckmarkCircle /> ปกติ
                                </span>
                              )}
                            </td>
                          </tr>
                        )
                      })}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="data-chart-section glass-panel">
              <h3><FaChartLine style={{ marginRight: '0.5rem' }} />กราฟแสดงข้อมูล Sensor</h3>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={prepareChartData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="name" stroke="#fff" angle={-45} textAnchor="end" height={100} />
                  <YAxis stroke="#fff" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(17, 24, 39, 0.95)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#8b5cf6"
                    strokeWidth={3}
                    dot={{ r: 5, fill: '#8b5cf6' }}
                    name="ค่าปัจจุบัน"
                  />
                  {prepareChartData().map((item, idx) =>
                    item.threshold ? (
                      <ReferenceLine
                        key={idx}
                        y={item.threshold}
                        stroke="#ef4444"
                        strokeDasharray="3 3"
                        strokeWidth={2}
                        label={{ value: 'Threshold', fill: '#ef4444', position: 'insideTopRight' }}
                      />
                    ) : null
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Action Buttons */}
          <div className="button-group">
            <button onClick={analyzeSensors} disabled={loading} className="btn-analyze">
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
        </>
      )}

      {/* Results Section */}
      {result && (
        <div className="result-section glass-panel">
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
        <div className="result-section prediction-result glass-panel">
          <h3><GiCrystalBall style={{ marginRight: '0.5rem' }} />ผลการทำนาย ML Model (Zero Breakdown)</h3>

          {/* Risk Score & Model Info */}
          <div className="ml-prediction-header">
            <div className="risk-score-box">
              <div className={`risk-badge risk-${predictionResult.risk_level}`}>
                <div className="risk-score">{predictionResult.risk_score}/100</div>
                <div className="risk-label">ระดับความเสี่ยง: {predictionResult.risk_level}</div>
                {predictionResult.risk_probability && (
                  <div className="risk-probability">ความน่าจะเป็น: {(predictionResult.risk_probability * 100).toFixed(2)}%</div>
                )}
              </div>
            </div>

            {/* Model Type Badge */}
            <div className="model-info-badge">
              <div className="model-type">{predictionResult.model_type || 'ML Stacked Ensemble'}</div>
              {predictionResult.anomaly_flag === 1 && (
                <div className="anomaly-detected">
                  <IoWarning /> Anomaly Detected
                  {predictionResult.anomaly_score && (
                    <span className="anomaly-score-value">Score: {predictionResult.anomaly_score.toFixed(3)}</span>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Base Model Predictions */}
          {predictionResult.base_predictions && (
            <div className="base-predictions-section">
              <h4><MdAnalytics style={{ marginRight: '0.5rem' }} />ผลการทำนายจากโมเดลพื้นฐาน:</h4>
              <div className="base-models-grid">
                {predictionResult.base_predictions.xgb !== null && predictionResult.base_predictions.xgb !== undefined && (
                  <div className="base-model-card">
                    <div className="model-name">XGBoost</div>
                    <div className="model-probability">{(predictionResult.base_predictions.xgb * 100).toFixed(2)}%</div>
                  </div>
                )}
                {predictionResult.base_predictions.lgb !== null && predictionResult.base_predictions.lgb !== undefined && (
                  <div className="base-model-card">
                    <div className="model-name">LightGBM</div>
                    <div className="model-probability">{(predictionResult.base_predictions.lgb * 100).toFixed(2)}%</div>
                  </div>
                )}
                {predictionResult.base_predictions.rf !== null && predictionResult.base_predictions.rf !== undefined && (
                  <div className="base-model-card">
                    <div className="model-name">Random Forest</div>
                    <div className="model-probability">{(predictionResult.base_predictions.rf * 100).toFixed(2)}%</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Prediction Text */}
          <div className="prediction-box">
            <h4><MdAnalytics style={{ marginRight: '0.5rem' }} />การทำนาย:</h4>
            <div className="prediction-text">
              {predictionResult.prediction}
            </div>
          </div>

          {/* Alerts */}
          {predictionResult.alerts && predictionResult.alerts.length > 0 && (
            <div className="alerts-box">
              <h4><IoWarning style={{ marginRight: '0.5rem' }} />ปัญหาที่พบ ({predictionResult.alerts.length} รายการ):</h4>
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