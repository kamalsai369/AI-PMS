import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { FiTrendingUp, FiUsers, FiAlertCircle, FiCheckCircle, FiClock, FiZap } from 'react-icons/fi'
import './ProjectOverview.css'

const ProjectOverview = ({ onNavigate }) => {
  const [projectData, setProjectData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProjectStatus()
  }, [])

  const fetchProjectStatus = async () => {
    try {
      const response = await axios.get('/api/project-status')
      setProjectData(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch project status:', error)
      setLoading(false)
      // Show error state instead of fallback data
    }
  }

  const getHealthColor = (health) => {
    const colors = {
      'Excellent': '#10b981',
      'Good': '#3b82f6',
      'At Risk': '#f59e0b',
      'Critical': '#ef4444'
    }
    return colors[health] || colors['Good']
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner" />
        <p>Loading project data...</p>
      </div>
    )
  }

  if (!projectData) {
    return (
      <div className="loading-container">
        <FiAlertCircle size={48} color="#ef4444" />
        <p>Failed to load project data. Please check backend connection.</p>
        <button onClick={fetchProjectStatus} className="retry-button">Retry</button>
      </div>
    )
  }

  const completionRate = projectData ? ((projectData.completed_tasks / projectData.total_tasks) * 100).toFixed(1) : 0

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  }

  return (
    <div className="project-overview">
      <motion.div 
        className="hero-section"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="hero-title">
          Welcome to <span className="text-gradient">AI-PMS</span>
        </h1>
        <p className="hero-subtitle">
          15km Metro Rail Project - AI-Powered Intelligence Dashboard
        </p>
      </motion.div>

      <motion.div 
        className="metrics-grid"
        variants={container}
        initial="hidden"
        animate="show"
      >
        <motion.div className="metric-card glass-card" variants={item}>
          <div className="metric-icon" style={{background: 'linear-gradient(135deg, #6366f1, #818cf8)'}}>
            <FiCheckCircle />
          </div>
          <div className="metric-content">
            <h3>Project Progress</h3>
            <div className="metric-value">{completionRate}%</div>
            <p className="metric-label">{projectData?.completed_tasks} of {projectData?.total_tasks} tasks completed</p>
            <div className="progress-bar">
              <motion.div 
                className="progress-fill"
                initial={{ width: 0 }}
                animate={{ width: `${completionRate}%` }}
                transition={{ duration: 1, delay: 0.5 }}
              />
            </div>
          </div>
        </motion.div>

        <motion.div className="metric-card glass-card" variants={item}>
          <div className="metric-icon" style={{background: 'linear-gradient(135deg, #10b981, #059669)'}}>
            <FiClock />
          </div>
          <div className="metric-content">
            <h3>In Progress</h3>
            <div className="metric-value">{projectData?.in_progress_tasks}</div>
            <p className="metric-label">Active tasks</p>
          </div>
        </motion.div>

        <motion.div className="metric-card glass-card" variants={item}>
          <div className="metric-icon" style={{background: 'linear-gradient(135deg, #f59e0b, #d97706)'}}>
            <FiUsers />
          </div>
          <div className="metric-content">
            <h3>Resource Conflicts</h3>
            <div className="metric-value">{projectData?.overallocated_resources}</div>
            <p className="metric-label">Over-allocation instances</p>
          </div>
        </motion.div>

        <motion.div className="metric-card glass-card" variants={item}>
          <div className="metric-icon" style={{background: 'linear-gradient(135deg, #ef4444, #dc2626)'}}>
            <FiAlertCircle />
          </div>
          <div className="metric-content">
            <h3>Critical Issues</h3>
            <div className="metric-value">{projectData?.critical_issues}</div>
            <p className="metric-label">Requiring attention</p>
          </div>
        </motion.div>
      </motion.div>

      <motion.div 
        className="health-card glass-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="health-header">
          <FiTrendingUp className="health-icon" />
          <h3>Schedule Health Status</h3>
        </div>
        <div className="health-indicator">
          <div 
            className="health-badge"
            style={{
              background: `linear-gradient(135deg, ${getHealthColor(projectData?.schedule_health)}dd, ${getHealthColor(projectData?.schedule_health)}aa)`,
              boxShadow: `0 8px 24px ${getHealthColor(projectData?.schedule_health)}40`
            }}
          >
            {projectData?.schedule_health}
          </div>
          <p className="health-description">
            {projectData?.schedule_health === 'Excellent' && 'Project is on track with no major concerns'}
            {projectData?.schedule_health === 'Good' && 'Project is progressing well with minor issues'}
            {projectData?.schedule_health === 'At Risk' && 'Some delays and conflicts detected - attention needed'}
            {projectData?.schedule_health === 'Critical' && 'Significant issues require immediate intervention'}
          </p>
        </div>
      </motion.div>

      <motion.div 
        className="actions-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <h3>Quick Actions</h3>
        <div className="actions-grid">
          <motion.button
            className="action-card glass-card"
            onClick={() => onNavigate('analyzer')}
            whileHover={{ scale: 1.03, y: -4 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="action-icon" style={{background: 'linear-gradient(135deg, #6366f1, #818cf8)'}}>
              <FiZap />
            </div>
            <h4>Analyze Meeting</h4>
            <p>Upload transcript and extract AI-powered insights</p>
          </motion.button>

          <motion.button
            className="action-card glass-card"
            onClick={() => onNavigate('actions')}
            whileHover={{ scale: 1.03, y: -4 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="action-icon" style={{background: 'linear-gradient(135deg, #10b981, #059669)'}}>
              <FiCheckCircle />
            </div>
            <h4>View Action Items</h4>
            <p>See prioritized tasks and assignments</p>
          </motion.button>

          <motion.button
            className="action-card glass-card"
            onClick={() => onNavigate('conflicts')}
            whileHover={{ scale: 1.03, y: -4 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="action-icon" style={{background: 'linear-gradient(135deg, #f59e0b, #d97706)'}}>
              <FiAlertCircle />
            </div>
            <h4>Detect Conflicts</h4>
            <p>Identify contradictions and resolve issues</p>
          </motion.button>
        </div>
      </motion.div>

      <motion.div 
        className="features-showcase glass-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
      >
        <h3>💡 AI-Powered Features</h3>
        <div className="features-list">
          <div className="feature-highlight">
            <span className="feature-emoji">🎯</span>
            <div>
              <h4>Smart Action Item Extraction</h4>
              <p>Automatically identifies tasks, assignees, and deadlines from natural conversation</p>
            </div>
          </div>
          <div className="feature-highlight">
            <span className="feature-emoji">⚡</span>
            <div>
              <h4>Priority Scoring (1-10)</h4>
              <p>AI analyzes urgency and impact to intelligently prioritize tasks</p>
            </div>
          </div>
          <div className="feature-highlight">
            <span className="feature-emoji">🔍</span>
            <div>
              <h4>Conflict Detection</h4>
              <p>Flags contradicting information between speakers or inconsistent data</p>
            </div>
          </div>
          <div className="feature-highlight">
            <span className="feature-emoji">📊</span>
            <div>
              <h4>Real-time Dashboard</h4>
              <p>Glassmorphism design with fluid animations for premium user experience</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default ProjectOverview
