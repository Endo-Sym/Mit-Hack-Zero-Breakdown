import { useState, useEffect } from 'react'
import axios from 'axios'
import './EmbeddingsManager.css'
import { FaFileAlt, FaTrash, FaEdit, FaCheck, FaTimes, FaPlus } from 'react-icons/fa'
import { IoCloudUpload } from 'react-icons/io5'
import { BiLoaderAlt } from 'react-icons/bi'
import { MdLibraryBooks } from 'react-icons/md'

const API_URL = 'http://localhost:8000'

function EmbeddingsManager() {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploadingPdf, setUploadingPdf] = useState(false)
  const [editingFile, setEditingFile] = useState(null)
  const [newName, setNewName] = useState('')
  const [pdfFile, setPdfFile] = useState(null)
  const [customName, setCustomName] = useState('')

  useEffect(() => {
    fetchEmbeddingFiles()
  }, [])

  const fetchEmbeddingFiles = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_URL}/api/embeddings`)
      setFiles(response.data.files)
    } catch (error) {
      console.error('Error fetching embeddings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePdfUpload = async () => {
    if (!pdfFile) {
      alert('กรุณาเลือกไฟล์ PDF')
      return
    }

    setUploadingPdf(true)
    const formData = new FormData()
    formData.append('file', pdfFile)
    if (customName.trim()) {
      formData.append('custom_name', customName)
    }

    try {
      await axios.post(`${API_URL}/api/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setPdfFile(null)
      setCustomName('')
      fetchEmbeddingFiles()
      alert('สร้าง Embeddings สำเร็จ!')
    } catch (error) {
      alert(`เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploadingPdf(false)
    }
  }

  const handleRename = async (filename) => {
    if (!newName.trim()) {
      alert('กรุณาใส่ชื่อใหม่')
      return
    }

    try {
      await axios.post(`${API_URL}/api/embeddings/rename`, {
        old_filename: filename,
        new_name: newName
      })

      setEditingFile(null)
      setNewName('')
      fetchEmbeddingFiles()
    } catch (error) {
      alert(`เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleDelete = async (filename) => {
    if (!confirm(`คุณต้องการลบไฟล์ ${filename} ใช่หรือไม่?`)) {
      return
    }

    try {
      await axios.delete(`${API_URL}/api/embeddings/${filename}`)
      fetchEmbeddingFiles()
    } catch (error) {
      alert(`เกิดข้อผิดพลาด: ${error.response?.data?.detail || error.message}`)
    }
  }

  const startEdit = (file) => {
    setEditingFile(file.filename)
    setNewName(file.custom_name)
  }

  const cancelEdit = () => {
    setEditingFile(null)
    setNewName('')
  }

  return (
    <div className="embeddings-manager">
      <div className="manager-header">
        <h3>
          <MdLibraryBooks className="section-icon" />
          จัดการไฟล์ Embeddings (RAG)
        </h3>
        <p className="section-description">
          อัพโหลดและจัดการคู่มือการซ่อมบำรุงในรูปแบบ PDF เพื่อสร้าง embeddings สำหรับระบบ RAG
        </p>
      </div>

      {/* Upload PDF Section */}
      <div className="upload-pdf-section">
        <h4>
          <IoCloudUpload style={{ marginRight: '0.5rem' }} />
          อัพโหลดคู่มือ PDF
        </h4>

        <div className="upload-form">
          <div className="form-group">
            <label className="file-label-custom">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setPdfFile(e.target.files[0])}
                className="file-input-hidden"
              />
              <FaPlus className="icon" />
              <span>{pdfFile ? pdfFile.name : 'เลือกไฟล์ PDF'}</span>
            </label>
          </div>

          <div className="form-group">
            <input
              type="text"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              placeholder="ชื่อไฟล์ (ไม่จำเป็น)"
              className="custom-name-input"
            />
          </div>

          <button
            onClick={handlePdfUpload}
            disabled={!pdfFile || uploadingPdf}
            className="btn-upload-pdf"
          >
            {uploadingPdf ? (
              <>
                <BiLoaderAlt className="spin-icon" />
                กำลังสร้าง Embeddings...
              </>
            ) : (
              <>
                <IoCloudUpload className="icon" />
                สร้าง Embeddings
              </>
            )}
          </button>
        </div>
      </div>

      {/* Files List */}
      <div className="files-section">
        <h4>
          <FaFileAlt style={{ marginRight: '0.5rem' }} />
          ไฟล์ Embeddings ({files.length})
        </h4>

        {loading ? (
          <div className="loading-state">
            <BiLoaderAlt className="spin-icon" />
            <span>กำลังโหลด...</span>
          </div>
        ) : files.length === 0 ? (
          <div className="empty-state">
            <MdLibraryBooks className="empty-icon" />
            <p>ยังไม่มีไฟล์ Embeddings</p>
            <p className="empty-hint">อัพโหลดไฟล์ PDF เพื่อสร้าง Embeddings</p>
          </div>
        ) : (
          <div className="files-grid">
            {files.map((file) => (
              <div key={file.filename} className="file-card">
                <div className="file-icon-wrapper">
                  <FaFileAlt className="file-icon" />
                </div>

                <div className="file-info">
                  {editingFile === file.filename ? (
                    <div className="edit-mode">
                      <input
                        type="text"
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                        className="edit-input"
                        autoFocus
                      />
                      <div className="edit-actions">
                        <button
                          onClick={() => handleRename(file.filename)}
                          className="btn-save"
                          title="บันทึก"
                        >
                          <FaCheck />
                        </button>
                        <button
                          onClick={cancelEdit}
                          className="btn-cancel"
                          title="ยกเลิก"
                        >
                          <FaTimes />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="file-name">{file.custom_name}</div>
                      <div className="file-meta">
                        <span className="file-source">{file.source_file}</span>
                        <span className="file-size">{file.size_mb.toFixed(2)} MB</span>
                        <span className="file-embeddings">{file.num_embeddings} embeddings</span>
                      </div>
                      <div className="file-date">
                        {new Date(file.created_at).toLocaleDateString('th-TH', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </>
                  )}
                </div>

                {editingFile !== file.filename && (
                  <div className="file-actions">
                    <button
                      onClick={() => startEdit(file)}
                      className="btn-edit"
                      title="แก้ไขชื่อ"
                    >
                      <FaEdit />
                    </button>
                    <button
                      onClick={() => handleDelete(file.filename)}
                      className="btn-delete"
                      title="ลบ"
                    >
                      <FaTrash />
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default EmbeddingsManager