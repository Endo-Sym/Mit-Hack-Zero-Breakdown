import { useState } from 'react'
import './App.css'
import ChatInterface from './components/ChatInterface'
import SensorAnalysis from './components/SensorAnalysis'
import RepairManual from './components/RepairManual'
import Dashboard from './components/Dashboard'
import Settings from './components/Settings'
import { IoChatbubbleEllipses, IoSettings } from "react-icons/io5"
import { MdAnalytics, MdDashboard } from "react-icons/md"
import { FaTools } from "react-icons/fa"

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
            className={activeTab === 'dashboard' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('dashboard')}
          >
            <MdDashboard className="nav-icon" />
            <span className="nav-text">Dashboard</span>
          </button>
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
            className={activeTab === 'manual' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('manual')}
          >
            <FaTools className="nav-icon" />
            <span className="nav-text">คู่มือซ่อม</span>
          </button>
          <button
            className={activeTab === 'settings' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('settings')}
          >
            <IoSettings className="nav-icon" />
            <span className="nav-text">การตั้งค่า</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <p></p>
        </div>
      </aside>

      <main className="main-container">
        <header className="main-header">
          <h1>
            {activeTab === 'dashboard' && (
              <><MdDashboard style={{ marginRight: '0.5rem' }} /> Dashboard</>
            )}
            {activeTab === 'chat' && (
              <><IoChatbubbleEllipses style={{ marginRight: '0.5rem' }} /> Chat AI Agent</>
            )}
            {activeTab === 'sensor' && (
              <><MdAnalytics style={{ marginRight: '0.5rem' }} /> วิเคราะห์ข้อมูล Sensor</>
            )}
            {activeTab === 'manual' && (
              <><FaTools style={{ marginRight: '0.5rem' }} /> คู่มือการซ่อม</>
            )}
            {activeTab === 'settings' && (
              <><IoSettings style={{ marginRight: '0.5rem' }} /> การตั้งค่า</>
            )}
          </h1>
        </header>

        <div className="main-content">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'sensor' && <SensorAnalysis />}
          {activeTab === 'manual' && <RepairManual />}
          {activeTab === 'settings' && <Settings />}
        </div>
      </main>
    </div>
  )
}

export default App
