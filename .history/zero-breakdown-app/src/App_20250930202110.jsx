import { useState } from 'react'
import './App.css'
import ChatInterface from './components/ChatInterface'
import SensorAnalysis from './components/SensorAnalysis'
import ROICalculator from './components/ROICalculator'
import RepairManual from './components/RepairManual'

function App() {
  const [activeTab, setActiveTab] = useState('chat')

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2> Zero Breakdown</h2>
        </div>

        <nav className="sidebar-nav">
          <button
            className={activeTab === 'chat' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('chat')}
          >
            <span className="nav-icon">💬</span>
            <span className="nav-text">Chat</span>
          </button>
          <button
            className={activeTab === 'sensor' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('sensor')}
          >
            <span className="nav-icon">📊</span>
            <span className="nav-text">วิเคราะห์ Sensor</span>
          </button>
          <button
            className={activeTab === 'roi' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('roi')}
          >
            <span className="nav-icon">💰</span>
            <span className="nav-text">คำนวณ ROI</span>
          </button>
          <button
            className={activeTab === 'manual' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('manual')}
          >
            <span className="nav-icon">📖</span>
            <span className="nav-text">คู่มือซ่อม</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <p></p>
        </div>
      </aside>

      <main className="main-container">
        <header className="main-header">
          <h1>
            {activeTab === 'chat' && '💬 Chat AI Agent'}
            {activeTab === 'sensor' && '📊 วิเคราะห์ข้อมูล Sensor'}
            {activeTab === 'roi' && '💰 คำนวณ ROI'}
            {activeTab === 'manual' && '📖 คู่มือการซ่อม'}
          </h1>
        </header>

        <div className="main-content">
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'sensor' && <SensorAnalysis />}
          {activeTab === 'roi' && <ROICalculator />}
          {activeTab === 'manual' && <RepairManual />}
        </div>
      </main>
    </div>
  )
}

export default App
