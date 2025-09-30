import { useState } from 'react'
import './App.css'
import ChatInterface from './components/ChatInterface'
import SensorAnalysis from './components/SensorAnalysis'
import ROICalculator from './components/ROICalculator'
import RepairManual from './components/RepairManual'
import { IoChatbubbleEllipses } from "react-icons/io5"
import { MdAnalytics } from "react-icons/md"
import { FaCalculator, FaTools } from "react-icons/fa"

function App() {
  const [activeTab, setActiveTab] = useState('chat')

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Zero Breakdown</h2>
        </div>

        <nav className="sidebar-nav">
          <button
            className={activeTab === 'chat' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('chat')}
          >
            <IoChatbubbleEllipses className="nav-icon" />
            <span className="nav-text">Chat</span>
          </button>
          <button
            className={activeTab === 'sensor' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('sensor')}
          >
            <MdAnalytics className="nav-icon" />
            <span className="nav-text">วิเคราะห์ Sensor</span>
          </button>
          <button
            className={activeTab === 'roi' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('roi')}
          >
            <FaCalculator className="nav-icon" />
            <span className="nav-text">คำนวณ ROI</span>
          </button>
          <button
            className={activeTab === 'manual' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('manual')}
          >
            <FaTools className="nav-icon" />
            <span className="nav-text">คู่มือซ่อม</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <p>Pow</p>
        </div>
      </aside>

      <main className="main-container">
        <header className="main-header">
          <h1>
            {activeTab === 'chat' && (
              <><IoChatbubbleEllipses style={{ marginRight: '0.5rem' }} /> Chat AI Agent</>
            )}
            {activeTab === 'sensor' && (
              <><MdAnalytics style={{ marginRight: '0.5rem' }} /> วิเคราะห์ข้อมูล Sensor</>
            )}
            {activeTab === 'roi' && (
              <><FaCalculator style={{ marginRight: '0.5rem' }} /> คำนวณ ROI</>
            )}
            {activeTab === 'manual' && (
              <><FaTools style={{ marginRight: '0.5rem' }} /> คู่มือการซ่อม</>
            )}
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
