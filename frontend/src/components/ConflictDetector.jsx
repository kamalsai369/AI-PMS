import { motion } from 'framer-motion'
import { FiAlertTriangle, FiUsers, FiInfo } from 'react-icons/fi'
import './ConflictDetector.css'

const ConflictDetector = ({ data }) => {
  if (!data || !data.conflicts) {
    return (
      <div className="conflict-empty">
        <p>No conflict data available. Please analyze a meeting transcript first.</p>
      </div>
    )
  }

  const getSeverityColor = (severity) => {
    const colors = {
      critical: '#ef4444',
      high: '#f59e0b',
      medium: '#3b82f6',
      low: '#10b981'
    }
    return colors[severity.toLowerCase()] || colors.medium
  }

  const getConflictIcon = (type) => {
    if (type.includes('Date')) return '📅'
    if (type.includes('Resource')) return '👥'
    if (type.includes('Scope')) return '📋'
    return '⚠️'
  }

  return (
    <div className="conflict-detector">
      <div className="conflict-header">
        <h2 className="text-gradient">Conflict Detection</h2>
        <p className="conflict-subtitle">
          Identified {data.conflicts.length} potential conflicts or contradictions
        </p>
      </div>

      {data.summary && (
        <motion.div 
          className="summary-card glass-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="summary-header">
            <FiInfo className="summary-icon" />
            <h3>Meeting Summary</h3>
          </div>
          <p>{data.summary}</p>
        </motion.div>
      )}

      {data.key_decisions && data.key_decisions.length > 0 && (
        <motion.div 
          className="decisions-card glass-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="section-header">
            <span className="section-icon">✓</span>
            <h3>Key Decisions</h3>
          </div>
          <ul className="decisions-list">
            {data.key_decisions.map((decision, index) => (
              <li key={index}>{decision}</li>
            ))}
          </ul>
        </motion.div>
      )}

      {data.risks_identified && data.risks_identified.length > 0 && (
        <motion.div 
          className="risks-card glass-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="section-header">
            <span className="section-icon">🚨</span>
            <h3>Risks Identified</h3>
          </div>
          <ul className="risks-list">
            {data.risks_identified.map((risk, index) => (
              <li key={index}>{risk}</li>
            ))}
          </ul>
        </motion.div>
      )}

      <div className="conflicts-section">
        <h3 className="section-title">
          <FiAlertTriangle /> Detected Conflicts
        </h3>

        {data.conflicts.length === 0 ? (
          <div className="no-conflicts glass-card">
            <div className="success-icon">✓</div>
            <h4>No Conflicts Detected</h4>
            <p>Great! The meeting transcript shows consistent information with no contradictions.</p>
          </div>
        ) : (
          <div className="conflicts-grid">
            {data.conflicts.map((conflict, index) => (
              <motion.div
                key={index}
                className="conflict-card glass-card"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                style={{
                  borderLeft: `4px solid ${getSeverityColor(conflict.severity)}`
                }}
              >
                <div className="conflict-card-header">
                  <div className="conflict-type">
                    <span className="type-icon">{getConflictIcon(conflict.type)}</span>
                    <span className="type-text">{conflict.type}</span>
                  </div>
                  <div 
                    className="severity-badge"
                    style={{
                      background: `linear-gradient(135deg, ${getSeverityColor(conflict.severity)}dd, ${getSeverityColor(conflict.severity)}aa)`
                    }}
                  >
                    {conflict.severity}
                  </div>
                </div>

                <p className="conflict-description">{conflict.description}</p>

                {conflict.parties && conflict.parties.length > 0 && (
                  <div className="parties-involved">
                    <FiUsers className="parties-icon" />
                    <span>Parties: {conflict.parties.join(', ')}</span>
                  </div>
                )}

                {conflict.conflicting_info && Object.keys(conflict.conflicting_info).length > 0 && (
                  <div className="conflicting-info">
                    <h5>Conflicting Information:</h5>
                    <div className="info-comparison">
                      {Object.entries(conflict.conflicting_info).map(([key, value], i) => (
                        <div key={i} className="info-item">
                          <span className="info-key">{key}:</span>
                          <span className="info-value">{JSON.stringify(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ConflictDetector
