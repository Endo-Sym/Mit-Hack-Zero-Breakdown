import { useState, useEffect } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import GaugeChart from 'react-gauge-chart'
import './Dashboard.css'
import { MdDashboard } from 'react-icons/md'
import { IoWarning } from 'react-icons/io5'

const API_URL = 'http://localhost:8000'

// Thresholds from BreakdownPredictionTool.py and BreakdownMaintenanceAdviceTool.py
const THRESHOLDS = {
  CurrentMotor: { min: 280, max: 320, danger_min: 240, danger_max: 360 },
  TempBrassBearingDE: { max: 75, warning: 85, danger: 95 }
}

function Dashboard() {
  const [machines, setMachines] = useState([])
  const [selectedMachine, setSelectedMachine] = useState(null)
  const [currentValues, setCurrentValues] = useState({
    currentMotor: 0,
    temperature: 0
  })
  const [machineData, setMachineData] = useState([])
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  // Load machines list
  useEffect(() => {
    loadMachines()
  }, [])

  // Load machine data when selected machine changes
  useEffect(() => {
    if (selectedMachine) {
      loadMachineData(selectedMachine)
    }
  }, [selectedMachine])

  const loadMachines = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/machines`)
      if (response.data.machines && response.data.machines.length > 0) {
        setMachines(response.data.machines)
        setSelectedMachine(response.data.machines[0])
      }
    } catch (error) {
      console.error('Error loading machines:', error)
    }
  }

  const loadMachineData = async (machineId) => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/api/machine-data/${machineId}`, {
        params: { limit: 100 }
      })

      if (response.data) {
        const sensorReadings = response.data.sensor_readings

        // Update current values
        setCurrentValues({
          currentMotor: sensorReadings.CurrentMotor || 0,
          temperature: sensorReadings.TempBrassBearingDE || 0
        })

        // Check for threshold violations and create alerts
        const newAlerts = []

        // Check CurrentMotor
        if (sensorReadings.CurrentMotor < THRESHOLDS.CurrentMotor.danger_min ||
            sensorReadings.CurrentMotor > THRESHOLDS.CurrentMotor.danger_max) {
          newAlerts.push(`CurrentMotor อยู่ในระดับอันตราย: ${sensorReadings.CurrentMotor} A`)
        } else if (sensorReadings.CurrentMotor < THRESHOLDS.CurrentMotor.min ||
                   sensorReadings.CurrentMotor > THRESHOLDS.CurrentMotor.max) {
          newAlerts.push(`CurrentMotor ผิดปกติ: ${sensorReadings.CurrentMotor} A`)
        }

        // Check Temperature
        if (sensorReadings.TempBrassBearingDE > THRESHOLDS.TempBrassBearingDE.danger) {
          newAlerts.push(`อุณหภูมิสูงเกินไปมาก: ${sensorReadings.TempBrassBearingDE}°C`)
        } else if (sensorReadings.TempBrassBearingDE > THRESHOLDS.TempBrassBearingDE.warning) {
          newAlerts.push(`อุณหภูมิสูงกว่าปกติ: ${sensorReadings.TempBrassBearingDE}°C`)
        } else if (sensorReadings.TempBrassBearingDE > THRESHOLDS.TempBrassBearingDE.max) {
          newAlerts.push(`อุณหภูมิเกินค่าปกติ: ${sensorReadings.TempBrassBearingDE}°C`)
        }

        setAlerts(newAlerts)

        // Generate time series data (simulate history with current values)
        const dataPoints = []
        for (let i = 100; i >= 0; i--) {
          dataPoints.push({
            timestamp: i,
            current: sensorReadings.CurrentMotor + (Math.random() - 0.5) * 10,
            temperature: sensorReadings.TempBrassBearingDE + (Math.random() - 0.5) * 5
          })
        }

        setMachineData(dataPoints)
      }
    } catch (error) {
      console.error('Error loading machine data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Auto-refresh every 5 seconds
  useEffect(() => {
    if (selectedMachine) {
      const interval = setInterval(() => {
        loadMachineData(selectedMachine)
      }, 5000)
      return () => clearInterval(interval)
    }
  }, [selectedMachine])

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>
          <MdDashboard style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
          Dashboard - Factory Real-time Monitoring
        </h2>
        <p className="description">
          แดชบอร์ดแสดงข้อมูลเครื่องจักรแบบเรียลไทม์จากไฟล์ที่อัพโหลด
        </p>
      </div>

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="alerts-banner">
          <IoWarning style={{ marginRight: '0.5rem', fontSize: '1.5rem' }} />
          <div className="alerts-content">
            <strong>แจ้งเตือน: เครื่องมีสถานะเกินเกณฑ์</strong>
            <ul>
              {alerts.map((alert, idx) => (
                <li key={idx}>{alert}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Machine Selector */}
      {machines.length > 0 ? (
        <div className="machine-selector">
          {machines.map((machineName) => (
            <button
              key={machineName}
              className={`machine-btn ${selectedMachine === machineName ? 'active' : ''}`}
              onClick={() => setSelectedMachine(machineName)}
            >
              {machineName}
            </button>
          ))}
        </div>
      ) : (
        <div className="no-data-message">
          <p>ยังไม่มีข้อมูล กรุณาอัพโหลดไฟล์ CSV ที่หน้า "วิเคราะห์ข้อมูล Sensor"</p>
        </div>
      )}

      {/* Main Dashboard Layout */}
      <div className="dashboard-main">
        {/* Left Side - Gauges */}
        <div className="gauges-section">
          {/* Current Motor Gauge */}
          <div className="gauge-card">
            <GaugeChart
              id="current-motor-gauge"
              nrOfLevels={3}
              percent={currentValues.currentMotor / 400}
              textColor="#F3F4F6"
              colors={["#10b981", "#FBBF24", "#EF4444"]}
              arcWidth={0.3}
              needleColor="#A78BFA"
              needleBaseColor="#F472B6"
              hideText={true}
            />
            <div className="gauge-label">CURRENT MOTOR</div>
            <div className="gauge-value">{currentValues.currentMotor.toFixed(1)} A</div>
          </div>

          {/* Temperature Bearing Motor Gauge */}
          <div className="gauge-card">
            <GaugeChart
              id="temperature-gauge"
              nrOfLevels={3}
              percent={currentValues.temperature / 100}
              textColor="#F3F4F6"
              colors={["#10b981", "#FBBF24", "#EF4444"]}
              arcWidth={0.3}
              needleColor="#A78BFA"
              needleBaseColor="#F472B6"
              hideText={true}
            />
            <div className="gauge-label">TEMPERATURE<br/>BEARING MOTOR</div>
            <div className="gauge-value">{currentValues.temperature.toFixed(1)} °C</div>
          </div>
        </div>

        {/* Right Side - Charts */}
        <div className="charts-section">
          {/* Current Motor Chart */}
          <div className="chart-card">
            <div className="chart-header">
              <h3>Current Motor (Amp)</h3>
              <div className="status-indicator">แจ้งเตือนเกินขีดจำกัด</div>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={machineData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(167, 139, 250, 0.2)" />
                <XAxis
                  dataKey="timestamp"
                  tick={{ fontSize: 11, fill: '#C4B5FD' }}
                  stroke="rgba(167, 139, 250, 0.3)"
                  interval={10}
                  label={{ value: 'Time', position: 'insideBottom', offset: -5, fill: '#C4B5FD' }}
                />
                <YAxis
                  domain={[0, 400]}
                  tick={{ fontSize: 11, fill: '#C4B5FD' }}
                  stroke="rgba(167, 139, 250, 0.3)"
                  ticks={[0, 100, 200, 300, 400]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(26, 22, 37, 0.95)',
                    border: '1px solid rgba(167, 139, 250, 0.3)',
                    borderRadius: '8px',
                    color: '#F3F4F6'
                  }}
                />
                {/* Threshold lines for CurrentMotor */}
                <ReferenceLine
                  y={THRESHOLDS.CurrentMotor.max}
                  stroke="#FBBF24"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  label={{ value: `Max: ${THRESHOLDS.CurrentMotor.max}A`, fill: '#FBBF24', fontSize: 11, position: 'right' }}
                />
                <ReferenceLine
                  y={THRESHOLDS.CurrentMotor.min}
                  stroke="#FBBF24"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  label={{ value: `Min: ${THRESHOLDS.CurrentMotor.min}A`, fill: '#FBBF24', fontSize: 11, position: 'right' }}
                />
                <ReferenceLine
                  y={THRESHOLDS.CurrentMotor.danger_max}
                  stroke="#EF4444"
                  strokeWidth={2}
                  strokeDasharray="3 3"
                  label={{ value: `Danger: ${THRESHOLDS.CurrentMotor.danger_max}A`, fill: '#EF4444', fontSize: 11, position: 'right' }}
                />
                <ReferenceLine
                  y={THRESHOLDS.CurrentMotor.danger_min}
                  stroke="#EF4444"
                  strokeWidth={2}
                  strokeDasharray="3 3"
                  label={{ value: `Danger: ${THRESHOLDS.CurrentMotor.danger_min}A`, fill: '#EF4444', fontSize: 11, position: 'right' }}
                />
                <Line
                  type="monotone"
                  dataKey="current"
                  stroke="#60A5FA"
                  strokeWidth={3}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Temperature Bearing Motor Chart */}
          <div className="chart-card">
            <div className="chart-header">
              <h3>Temperature Bearing Motor DE C</h3>
              <div className="status-indicator">แจ้งเตือนเกินขีดจำกัด</div>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={machineData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(167, 139, 250, 0.2)" />
                <XAxis
                  dataKey="timestamp"
                  tick={{ fontSize: 11, fill: '#C4B5FD' }}
                  stroke="rgba(167, 139, 250, 0.3)"
                  interval={10}
                  label={{ value: 'Time', position: 'insideBottom', offset: -5, fill: '#C4B5FD' }}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 11, fill: '#C4B5FD' }}
                  stroke="rgba(167, 139, 250, 0.3)"
                  ticks={[0, 20, 40, 60, 80, 100]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(26, 22, 37, 0.95)',
                    border: '1px solid rgba(167, 139, 250, 0.3)',
                    borderRadius: '8px',
                    color: '#F3F4F6'
                  }}
                />
                {/* Threshold lines for Temperature */}
                <ReferenceLine
                  y={THRESHOLDS.TempBrassBearingDE.max}
                  stroke="#10b981"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  label={{ value: `Normal Max: ${THRESHOLDS.TempBrassBearingDE.max}°C`, fill: '#10b981', fontSize: 11, position: 'right' }}
                />
                <ReferenceLine
                  y={THRESHOLDS.TempBrassBearingDE.warning}
                  stroke="#FBBF24"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  label={{ value: `Warning: ${THRESHOLDS.TempBrassBearingDE.warning}°C`, fill: '#FBBF24', fontSize: 11, position: 'right' }}
                />
                <ReferenceLine
                  y={THRESHOLDS.TempBrassBearingDE.danger}
                  stroke="#EF4444"
                  strokeWidth={2}
                  strokeDasharray="3 3"
                  label={{ value: `Danger: ${THRESHOLDS.TempBrassBearingDE.danger}°C`, fill: '#EF4444', fontSize: 11, position: 'right' }}
                />
                <Line
                  type="monotone"
                  dataKey="temperature"
                  stroke="#F472B6"
                  strokeWidth={3}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard