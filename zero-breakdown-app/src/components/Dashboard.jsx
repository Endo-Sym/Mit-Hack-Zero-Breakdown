import { useState, useEffect } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import GaugeChart from 'react-gauge-chart'
import './Dashboard.css'
import { MdDashboard } from 'react-icons/md'

const API_URL = 'http://localhost:8000'

function Dashboard() {
  const [selectedMachine, setSelectedMachine] = useState('Feed Mill 1')
  const [currentValues, setCurrentValues] = useState({
    currentMotor: 305,
    temperature: 68
  })
  const [machineData, setMachineData] = useState({
    'Feed Mill 1': [],
    'Feed Mill 2': [],
    'Feed Mill 3': [],
    'Feed Mill 4': []
  })

  // Generate sample time-series data
  const generateSampleData = () => {
    const data = {}
    const machines = ['Feed Mill 1', 'Feed Mill 2', 'Feed Mill 3', 'Feed Mill 4']

    machines.forEach((machine, machineIdx) => {
      const dataPoints = []
      const now = new Date()

      for (let i = 100; i >= 0; i--) {
        const timestamp = i

        dataPoints.push({
          timestamp: timestamp,
          current: +(280 + Math.random() * 40).toFixed(1),
          temperature: +(60 + Math.random() * 20).toFixed(1)
        })
      }

      data[machine] = dataPoints
    })

    setMachineData(data)

    // Update current values
    setCurrentValues({
      currentMotor: +(280 + Math.random() * 40).toFixed(1),
      temperature: +(60 + Math.random() * 20).toFixed(1)
    })
  }

  useEffect(() => {
    generateSampleData()
    const interval = setInterval(generateSampleData, 5000)
    return () => clearInterval(interval)
  }, [])

  const data = machineData[selectedMachine] || []

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>
          <MdDashboard style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
          Dashboard - Factory One Vibration
        </h2>
        <p className="description">
          แดชบอร์ดแสดงข้อมูลการสั่นสะเทือนและสถานะเครื่องจักรแบบเรียลไทม์
        </p>
      </div>

      {/* Machine Selector */}
      <div className="machine-selector">
        {Object.keys(machineData).map((machineName) => (
          <button
            key={machineName}
            className={`machine-btn ${selectedMachine === machineName ? 'active' : ''}`}
            onClick={() => setSelectedMachine(machineName)}
          >
            {machineName}
          </button>
        ))}
      </div>

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
              <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
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
              <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
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