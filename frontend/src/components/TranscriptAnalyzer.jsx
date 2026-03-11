import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { FiUpload, FiZap, FiLoader } from 'react-icons/fi'
import './TranscriptAnalyzer.css'

const TranscriptAnalyzer = ({ onAnalysisComplete }) => {
  const [transcript, setTranscript] = useState('')
  const [meetingTitle, setMeetingTitle] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState(null)
  const [sampleTranscripts, setSampleTranscripts] = useState([])
  const [loadingSamples, setLoadingSamples] = useState(false)

  useEffect(() => {
    fetchSampleTranscripts()
  }, [])

  const fetchSampleTranscripts = async () => {
    try {
      setLoadingSamples(true)
      const response = await axios.get('/api/sample-transcripts')
      setSampleTranscripts(response.data.transcripts)
    } catch (err) {
      console.error('Failed to load sample transcripts:', err)
    } finally {
      setLoadingSamples(false)
    }
  }

  const loadSampleTranscript = async (filename) => {
    try {
      setLoadingSamples(true)
      const response = await axios.get(`/api/sample-transcripts/${filename}`)
      setTranscript(response.data.content)
      setMeetingTitle(response.data.title)
      setError(null)
    } catch (err) {
      setError('Failed to load sample transcript. Please try again.')
    } finally {
      setLoadingSamples(false)
    }
  }

  const analyzeTranscript = async () => {
    if (!transcript.trim()) {
      setError('Please enter a meeting transcript')
      return
    }

    setIsAnalyzing(true)
    setError(null)

    try {
      const response = await axios.post('/api/analyze-transcript', {
        transcript: transcript,
        meeting_title: meetingTitle || 'Untitled Meeting',
        meeting_date: new Date().toISOString().split('T')[0]
      })

      onAnalysisComplete(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze transcript. Please check your API connection.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="transcript-analyzer">
      <div className="analyzer-header">
        <h2 className="text-gradient">Meeting Intelligence Engine</h2>
        <p className="analyzer-subtitle">
          Upload your raw meeting transcript and let AI extract action items, detect conflicts, and prioritize tasks
        </p>
      </div>

      <div className="analyzer-grid">
        <motion.div 
          className="input-section glass-card"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="input-header">
            <FiUpload className="input-icon" />
            <h3>Meeting Transcript</h3>
          </div>

          <input 
            type="text"
            placeholder="Meeting title (optional)"
            value={meetingTitle}
            onChange={(e) => setMeetingTitle(e.target.value)}
            className="meeting-title-input"
          />

          <textarea
            className="transcript-input"
            placeholder="Paste your meeting transcript here...

Example format:
**Speaker Name**: Their comments
**Another Speaker**: Their response
..."
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            rows={18}
          />

          <div className="input-actions">
            <div className="sample-loader">
              <label htmlFor="sample-select">Load Sample: </label>
              <select 
                id="sample-select"
                onChange={(e) => e.target.value && loadSampleTranscript(e.target.value)}
                disabled={loadingSamples}
              >
                <option value="">-- Select a transcript --</option>
                {sampleTranscripts.map((sample) => (
                  <option key={sample.filename} value={sample.filename}>
                    {sample.title}
                  </option>
                ))}
              </select>
            </div>

            <motion.button
              className="btn-primary"
              onClick={analyzeTranscript}
              disabled={isAnalyzing}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isAnalyzing ? (
                <>
                  <FiLoader className="spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <FiZap />
                  Analyze with AI
                </>
              )}
            </motion.button>
          </div>

          {error && (
            <motion.div 
              className="error-message"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {error}
            </motion.div>
          )}
        </motion.div>

        <motion.div 
          className="features-section glass-card"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <h3>AI-Powered Analysis</h3>
          
          <div className="feature-list">
            <div className="feature-item">
              <div className="feature-icon" style={{background: 'linear-gradient(135deg, #10b981, #059669)'}}>
                ✓
              </div>
              <div>
                <h4>Action Item Extraction</h4>
                <p>Automatically identifies tasks, assignees, and deadlines from natural conversation</p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon" style={{background: 'linear-gradient(135deg, #3b82f6, #2563eb)'}}>
                ★
              </div>
              <div>
                <h4>Smart Prioritization</h4>
                <p>Assigns priority scores (1-10) based on urgency and business impact</p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon" style={{background: 'linear-gradient(135deg, #f59e0b, #d97706)'}}>
                ⚠
              </div>
              <div>
                <h4>Conflict Detection</h4>
                <p>Flags contradicting information between speakers or inconsistent data</p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon" style={{background: 'linear-gradient(135deg, #ec4899, #db2777)'}}>
                🎯
              </div>
              <div>
                <h4>Risk Identification</h4>
                <p>Detects mentioned risks, blockers, and potential delays</p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon" style={{background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)'}}>
                📊
              </div>
              <div>
                <h4>Key Decisions</h4>
                <p>Extracts important decisions and agreements from discussion</p>
              </div>
            </div>
          </div>

          <div className="llm-status glass-card">
            <h4>LLM Status</h4>
            <div className="status-indicator">
              <div className="status-dot" />
              <span>Ready (Fallback Mode Available)</span>
            </div>
            <p className="status-note">
              💡 Tip: Set OPENAI_API_KEY environment variable for enhanced AI analysis
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default TranscriptAnalyzer
