import { useState, useEffect } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import './Dashboard.css'
import { MdDashboard } from 'react-icons/md'
import { BiLoaderAlt } from 'react-icons/bi'
import { IoAlertCircle, IoCheckmarkCircle } from 'react-icons/io5'

const API_URL = 'http://localhost:8000'

function Dashboard() {
  const [machineData, setMachineData] = useState({
    'Feed Mill 1': [],
    'Feed Mill 2': [],
    'Feed Mill 3': [],
    'Feed Mill 4': []
  })
  const [loading, setLoading] = useState(false)
  const [alarmStatus, setAlarmStatus] = useState({
    'Feed Mill 1': 'normal',
    'Feed Mill 2': 'normal',
    'Feed Mill 3': 'normal',
    'Feed Mill 4': 'alarm'
  })

  // Generate sample time-series data
  const generateSampleData = () => {
    const data = {}
    const machines = ['Feed Mill 1', 'Feed Mill 2', 'Feed Mill 3', 'Feed Mill 4']

    machines.forEach((machine, machineIdx) => {
      const dataPoints = []
      const now = new Date()

      for (let i = 30; i >= 0; i--) {
        const date = new Date(now)
        date.setDate(date.getDate() - i)
        const dateStr = `Oct ${date.getDate()}`

        // Generate different patterns for each machine
        const baseVibration = machineIdx === 3 ? 2.5 : 1.2
        const variation = Math.random() * 0.5 - 0.25
        const spike = (machineIdx === 3 && i < 5) ? Math.random() * 2 : 0

        dataPoints.push({
          date: dateStr,
          vibration: +(baseVibration + variation + spike).toFixed(2),
          temperature: +(65 + Math.random() * 10).toFixed(1),
          power: +(290 + Math.random() * 20).toFixed(1),
          current: +(295 + Math.random() * 15).toFixed(1)
        })
      }

      data[machine] = dataPoints
    })

    setMachineData(data)
  }

  useEffect(() => {
    generateSampleData()
    // Refresh data every 30 seconds
    const interval = setInterval(generateSampleData, 30000)
    return () => clearInterval(interval)
  }, [])

  const getMachineStatus = (machineName) => {
    return alarmStatus[machineName] || 'normal'
  }

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

      <div className="machines-grid">
        {Object.entries(machineData).map(([machineName, data]) => {
          const status = getMachineStatus(machineName)

          return (
            <div key={machineName} className="machine-card">
              <div className="machine-header">
                <div className={`alarm-indicator ${status}`}>
                  {status === 'alarm' ? (
                    <IoAlertCircle className="alarm-icon" />
                  ) : (
                    <IoCheckmarkCircle className="normal-icon" />
                  )}
                </div>
                <h3>{machineName}</h3>
                <span className={`status-badge ${status}`}>
                  {status === 'alarm' ? 'มีแจ้งเตือน' : 'ปกติ'}
                </span>
              </div>

              <div className="charts-container">
                {/* Vibration Chart */}
                <div className="chart-box">
                  <h4>Vibration (mm/s)</h4>
                  <ResponsiveContainer width="100%" height={180}>
                    <LineChart data={data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                      <XAxis
                        dataKey="date"
                        tick={{ fontSize: 11 }}
                        interval={4}
                      />
                      <YAxis
                        domain={[0, 5]}
                        tick={{ fontSize: 11 }}
                      />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="vibration"
                        stroke={status === 'alarm' ? '#e53e3e' : '#48bb78'}
                        strokeWidth={2}
                        dot={false}
                      />
                      {/* Threshold lines */}
                      <Line
                        type="monotone"
                        dataKey={() => 1.8}
                        stroke="#48bb78"
                        strokeWidth={1}
                        strokeDasharray="5 5"
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey={() => 4.5}
                        stroke="#ed8936"
                        strokeWidth={1}
                        strokeDasharray="5 5"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Temperature Chart */}
                <div className="chart-box">
                  <h4>Temperature (°C)</h4>
                  <ResponsiveContainer width="100%" height={180}>
                    <LineChart data={data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                      <XAxis
                        dataKey="date"
                        tick={{ fontSize: 11 }}
                        interval={4}
                      />
                      <YAxis
                        domain={[0, 100]}
                        tick={{ fontSize: 11 }}
                      />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="temperature"
                        stroke="#667eea"
                        strokeWidth={2}
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey={() => 75}
                        stroke="#ed8936"
                        strokeWidth={1}
                        strokeDasharray="5 5"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Power Chart */}
                <div className="chart-box">
                  <h4>Power (kW)</h4>
                  <ResponsiveContainer width="100%" height={180}>
                    <LineChart data={data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                      <XAxis
                        dataKey="date"
                        tick={{ fontSize: 11 }}
                        interval={4}
                      />
                      <YAxis
                        domain={[250, 350]}
                        tick={{ fontSize: 11 }}
                      />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="power"
                        stroke="#f59e0b"
                        strokeWidth={2}
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey={() => 280}
                        stroke="#48bb78"
                        strokeWidth={1}
                        strokeDasharray="5 5"
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey={() => 320}
                        stroke="#48bb78"
                        strokeWidth={1}
                        strokeDasharray="5 5"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Current Chart */}
                <div className="chart-box">
                  <h4>Current (Amp)</h4>
                  <ResponsiveContainer width="100%" height={180}>
                    <LineChart data={data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                      <XAxis
                        dataKey="date"
                        tick={{ fontSize: 11 }}
                        interval={4}
                      />
                      <YAxis
                        domain={[250, 350]}
                        tick={{ fontSize: 11 }}
                      />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="current"
                        stroke="#9333ea"
                        strokeWidth={2}
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey={() => 270}
                        stroke="#48bb78"
                        strokeWidth={1}
                        strokeDasharray="5 5"
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey={() => 330}
                        stroke="#48bb78"
                        strokeWidth={1}
                        strokeDasharray="5 5"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default Dashboard