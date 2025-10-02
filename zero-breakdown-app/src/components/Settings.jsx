import { useState } from 'react'
import axios from 'axios'
import './Settings.css'
import { IoSettings, IoCloudUpload, IoCheckmarkCircle } from 'react-icons/io5'
import { BiLoaderAlt } from 'react-icons/bi'
import { MdOutlineFactory } from 'react-icons/md'

const API_URL = 'http://localhost:8000'

function Settings() {
  const [file, setFile] = useState(null)
  const [customFileName, setCustomFileName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [uploadedData, setUploadedData] = useState(null)
  const [machines, setMachines] = useState([])
  const [savedFiles, setSavedFiles] = useState([])

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile)
      setUploadSuccess(false)
    } else {
      alert('กรุณาเลือกไฟล์ CSV เท่านั้น')
    }
  }

  const handleUpload = async () => {
    if (!file) {
      alert('กรุณาเลือกไฟล์ CSV ก่อน')
      return
    }

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    if (customFileName.trim()) {
      formData.append('custom_name', customFileName)
    }

    try {
      const response = await axios.post(`${API_URL}/api/upload-csv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setUploadedData(response.data)
      setMachines(response.data.machines || [])
      setUploadSuccess(true)
      setCustomFileName('')

      setTimeout(() => setUploadSuccess(false), 3000)
    } catch (error) {
      alert(`เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="settings-container">
      <h2><IoSettings style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />การตั้งค่า</h2>

      <div className="settings-section">
        <h3><IoCloudUpload style={{ marginRight: '0.5rem' }} />อัพโหลดข้อมูลโรงงาน</h3>
        <p className="section-description">
          เชื่อมต่อข้อมูลจากโรงงานผ่านไฟล์ CSV เพื่อวิเคราะห์และทำนายการเสียหายของเครื่องจักร
        </p>

        <div className="upload-box">
          <div className="file-input-wrapper">
            <input
              type="file"
              id="csv-file"
              accept=".csv"
              onChange={handleFileChange}
              className="file-input"
            />
            <label htmlFor="csv-file" className="file-label">
              <IoCloudUpload className="upload-icon" />
              <span>{file ? file.name : 'เลือกไฟล์ CSV'}</span>
            </label>
          </div>

          <input
            type="text"
            value={customFileName}
            onChange={(e) => setCustomFileName(e.target.value)}
            placeholder="ตั้งชื่อไฟล์ (ไม่จำเป็น)"
            className="custom-name-input"
          />

          <button
            onClick={handleUpload}
            disabled={uploading || !file}
            className="btn-upload"
          >
            {uploading ? (
              <><BiLoaderAlt className="spin-icon" /> กำลังอัพโหลด...</>
            ) : (
              <><IoCloudUpload style={{ marginRight: '0.5rem' }} /> อัพโหลดข้อมูล</>
            )}
          </button>

          {uploadSuccess && (
            <div className="success-message">
              <IoCheckmarkCircle style={{ marginRight: '0.5rem' }} />
              อัพโหลดสำเร็จ!
            </div>
          )}
        </div>

        <div className="file-format-info">
          <h4>รูปแบบไฟล์ CSV ที่รองรับ:</h4>
          <ul>
            <li>ต้องมีคอลัมน์: Timestamp, Machine_ID, PowerMotor, CurrentMotor, TempBrassBearingDE, SpeedMotor, TempOilGear, TempBearingMotorNDE</li>
            <li>ต้องมีคอลัมน์: TempWindingMotorPhase_U, TempWindingMotorPhase_V, TempWindingMotorPhase_W, Vibration</li>
            <li>รูปแบบวันที่: YYYY-MM-DD HH:MM:SS</li>
          </ul>
        </div>
      </div>

      {uploadedData && (
        <div className="settings-section">
          <h3><MdOutlineFactory style={{ marginRight: '0.5rem' }} />ข้อมูลที่อัพโหลด</h3>

          <div className="data-summary">
            <div className="summary-item">
              <span className="summary-label">จำนวนแถว:</span>
              <span className="summary-value">{uploadedData.total_rows}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">จำนวนเครื่องจักร:</span>
              <span className="summary-value">{uploadedData.total_machines}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">ช่วงเวลา:</span>
              <span className="summary-value">{uploadedData.date_range}</span>
            </div>
          </div>

          {machines.length > 0 && (
            <div className="machines-list">
              <h4>รายการเครื่องจักร:</h4>
              <div className="machines-grid">
                {machines.map((machine, idx) => (
                  <div key={idx} className="machine-card">
                    <MdOutlineFactory className="machine-icon" />
                    <span>{machine}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {uploadedData.data_quality && (
            <div className="data-quality">
              <h4>คุณภาพข้อมูล:</h4>
              <div className="quality-item">
                <span>ข้อมูลสมบูรณ์:</span>
                <span className={uploadedData.data_quality.completeness > 90 ? 'quality-good' : 'quality-warning'}>
                  {uploadedData.data_quality.completeness}%
                </span>
              </div>
              <div className="quality-item">
                <span>ค่าที่ขาดหาย:</span>
                <span>{uploadedData.data_quality.missing_values} แถว</span>
              </div>
            </div>
          )}
        </div>
      )}

    </div>
  )
}

export default Settings