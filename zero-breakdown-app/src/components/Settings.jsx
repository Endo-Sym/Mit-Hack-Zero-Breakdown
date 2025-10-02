import { useState, useEffect } from 'react'
import axios from 'axios'
import './Settings.css'
import { IoSettings, IoCloudUpload, IoCheckmarkCircle, IoDocumentText } from 'react-icons/io5'
import { BiLoaderAlt } from 'react-icons/bi'
import { MdOutlineFactory } from 'react-icons/md'

const API_URL = 'http://localhost:8000'

function Settings() {
  const [file, setFile] = useState(null)
  const [customFileName, setCustomFileName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [uploadedData, setUploadedData] = useState(() => {
    const saved = localStorage.getItem('settingsUploadedData')
    return saved ? JSON.parse(saved) : null
  })
  const [machines, setMachines] = useState(() => {
    const saved = localStorage.getItem('settingsMachines')
    return saved ? JSON.parse(saved) : []
  })
  const [savedFiles, setSavedFiles] = useState([])

  // PDF upload states
  const [pdfFile, setPdfFile] = useState(null)
  const [pdfCustomName, setPdfCustomName] = useState('')
  const [uploadingPdf, setUploadingPdf] = useState(false)
  const [pdfUploadSuccess, setPdfUploadSuccess] = useState(false)

  // Save to localStorage when data changes
  useEffect(() => {
    if (uploadedData) {
      localStorage.setItem('settingsUploadedData', JSON.stringify(uploadedData))
    }
  }, [uploadedData])

  useEffect(() => {
    if (machines.length > 0) {
      localStorage.setItem('settingsMachines', JSON.stringify(machines))
    }
  }, [machines])

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

  const handlePdfFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setPdfFile(selectedFile)
      setPdfUploadSuccess(false)
    } else {
      alert('กรุณาเลือกไฟล์ PDF เท่านั้น')
    }
  }

  const handlePdfUpload = async () => {
    if (!pdfFile) {
      alert('กรุณาเลือกไฟล์ PDF ก่อน')
      return
    }

    setUploadingPdf(true)
    const formData = new FormData()
    formData.append('file', pdfFile)
    if (pdfCustomName.trim()) {
      formData.append('custom_name', pdfCustomName)
    }

    try {
      const response = await axios.post(`${API_URL}/api/upload-pdf`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setPdfUploadSuccess(true)
      setPdfCustomName('')
      setPdfFile(null)

      setTimeout(() => setPdfUploadSuccess(false), 3000)
      alert(`สร้าง Embeddings สำเร็จ: ${response.data.filename}`)
    } catch (error) {
      alert(`เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploadingPdf(false)
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

      <div className="settings-section">
        <h3><IoDocumentText style={{ marginRight: '0.5rem' }} />อัพโหลดคู่มือซ่อมบำรุง (PDF)</h3>
        <p className="section-description">
          อัพโหลดคู่มือ PDF เพื่อสร้าง Embeddings สำหรับระบบ RAG ที่ช่วยตอบคำถามเกี่ยวกับการซ่อมบำรุง
        </p>

        <div className="upload-box">
          <div className="file-input-wrapper">
            <input
              type="file"
              id="pdf-file"
              accept=".pdf"
              onChange={handlePdfFileChange}
              className="file-input"
            />
            <label htmlFor="pdf-file" className="file-label">
              <IoDocumentText className="upload-icon" />
              <span>{pdfFile ? pdfFile.name : 'เลือกไฟล์ PDF'}</span>
            </label>
          </div>

          <input
            type="text"
            value={pdfCustomName}
            onChange={(e) => setPdfCustomName(e.target.value)}
            placeholder="ตั้งชื่อคู่มือ (ไม่จำเป็น)"
            className="custom-name-input"
          />

          <button
            onClick={handlePdfUpload}
            disabled={uploadingPdf || !pdfFile}
            className="btn-upload"
          >
            {uploadingPdf ? (
              <><BiLoaderAlt className="spin-icon" /> กำลังสร้าง Embeddings...</>
            ) : (
              <><IoCloudUpload style={{ marginRight: '0.5rem' }} /> สร้าง Embeddings</>
            )}
          </button>

          {pdfUploadSuccess && (
            <div className="success-message">
              <IoCheckmarkCircle style={{ marginRight: '0.5rem' }} />
              สร้าง Embeddings สำเร็จ!
            </div>
          )}
        </div>

        <div className="file-format-info">
          <h4>ข้อมูล Embeddings:</h4>
          <ul>
            <li>ไฟล์ PDF จะถูกแปลงเป็น text embeddings ด้วย AWS Bedrock Titan</li>
            <li>บันทึกเป็นไฟล์ JSON ที่ /opt/dlami/nvme/embeddings/</li>
            <li>ใช้สำหรับระบบ RAG ตอบคำถามการซ่อมบำรุง</li>
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