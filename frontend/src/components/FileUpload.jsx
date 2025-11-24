import React, { useState } from 'react'
import axios from 'axios'
import './FileUpload.css'

const API_BASE =
  (import.meta.env.VITE_API_BASE_URL && import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '')) ||
  ''

function FileUpload({ onUpload }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [duplicateInfo, setDuplicateInfo] = useState(null)
  const [showDuplicateModal, setShowDuplicateModal] = useState(false)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      const fileExt = selectedFile.name.split('.').pop().toLowerCase()
      if (fileExt === 'pdf' || fileExt === 'docx') {
        setFile(selectedFile)
        setError(null)
        setSuccess(false)
      } else {
        setError('Please upload a PDF or DOCX file')
        setFile(null)
      }
    }
  }

  const handleContinueExisting = () => {
    if (duplicateInfo) {
      setSuccess(true)
      onUpload({
        documentId: duplicateInfo.existingDocumentId,
        filename: duplicateInfo.existingFilename
      })
      setShowDuplicateModal(false)
      setDuplicateInfo(null)
    }
  }

  const handleReprocess = async () => {
    if (!file) return
    
    setShowDuplicateModal(false)
    setUploading(true)
    setError(null)
    setSuccess(false)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('reprocess', 'true')

      const response = await axios.post(`${API_BASE}/api/upload/document`, formData)

      if (response.data.success) {
        setSuccess(true)
        onUpload({
          documentId: response.data.document_id,
          filename: response.data.filename || file.name
        })
      } else {
        setError(response.data.error || 'Upload failed')
      }
    } catch (err) {
      const backendError = err.response?.data?.error
      let displayError = backendError || 'Upload failed. Please try again.'
      if (displayError && displayError.toLowerCase().includes('textract')) {
        displayError = 'Failed to process the PDF. Please ensure the file is readable and try again.'
      }
      setError(displayError)
      console.error('Upload error:', err)
    } finally {
      setUploading(false)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError(null)
    setSuccess(false)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(`${API_BASE}/api/upload/document`, formData)

      if (response.data.success) {
        // Check if duplicate
        if (response.data.duplicate) {
          setDuplicateInfo({
            existingDocumentId: response.data.existing_document_id,
            existingFilename: response.data.existing_filename || file.name
          })
          setShowDuplicateModal(true)
        } else {
          setSuccess(true)
          onUpload({
            documentId: response.data.document_id,
            filename: response.data.filename || file.name
          })
        }
      } else {
        setError(response.data.error || 'Upload failed')
      }
    } catch (err) {
      const backendError = err.response?.data?.error
      let displayError = backendError || 'Upload failed. Please try again.'
      if (displayError && displayError.toLowerCase().includes('textract')) {
          displayError = 'Failed to process the PDF. Please ensure the file is readable and try again.'
      }
      setError(displayError)
      console.error('Upload error:', err)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="file-upload">
      <div className="upload-container">
        <h2>Upload Your Textbook</h2>
        <p>Upload a PDF or DOCX file to start learning</p>
        
        <div className="upload-box">
          <input
            type="file"
            id="file-input"
            accept=".pdf,.docx"
            onChange={handleFileChange}
            disabled={uploading}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-input" className="file-input-label">
            {file ? file.name : 'Choose File'}
          </label>
          
          {file && (
            <button
              className="upload-button"
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : 'Upload Document'}
            </button>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">Document uploaded successfully!</div>}
        
        {uploading && (
          <div className="upload-progress">
            <div className="spinner"></div>
            <p>Processing document and generating embeddings...</p>
          </div>
        )}
      </div>

      {/* Duplicate Detection Modal */}
      {showDuplicateModal && duplicateInfo && (
        <div className="modal-overlay" onClick={() => setShowDuplicateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Textbook Already Exists</h3>
            <p>This textbook has already been uploaded to the system.</p>
            <p className="modal-filename"><strong>{duplicateInfo.existingFilename}</strong></p>
            <div className="modal-buttons">
              <button className="modal-button primary" onClick={handleContinueExisting}>
                Continue with Existing
              </button>
              <button className="modal-button secondary" onClick={handleReprocess}>
                Reprocess & Replace
              </button>
              <button className="modal-button cancel" onClick={() => setShowDuplicateModal(false)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default FileUpload

