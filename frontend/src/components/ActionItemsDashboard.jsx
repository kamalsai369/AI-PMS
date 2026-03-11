import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { FiUser, FiCalendar, FiTarget, FiFilter } from 'react-icons/fi'
import './ActionItemsDashboard.css'

const ActionItemsDashboard = ({ data }) => {
  const [filterPriority, setFilterPriority] = useState('all')
  const [sortBy, setSortBy] = useState('priority')
  const [viewMode, setViewMode] = useState('grid') // grid or kanban

  const filteredItems = useMemo(() => {
    if (!data?.action_items) return []
    
    let items = [...data.action_items]

    // Filter
    if (filterPriority !== 'all') {
      items = items.filter(item => item.urgency.toLowerCase() === filterPriority)
    }

    // Sort
    if (sortBy === 'priority') {
      items.sort((a, b) => b.priority_score - a.priority_score)
    } else if (sortBy === 'assignee') {
      items.sort((a, b) => a.assignee.localeCompare(b.assignee))
    }

    return items
  }, [data, filterPriority, sortBy])

  const getPriorityClass = (score) => {
    if (score >= 9) return 'priority-critical'
    if (score >= 7) return 'priority-high'
    if (score >= 5) return 'priority-medium'
    return 'priority-low'
  }

  const getUrgencyColor = (urgency) => {
    const colors = {
      critical: '#ef4444',
      high: '#f59e0b',
      medium: '#3b82f6',
      low: '#10b981'
    }
    return colors[urgency.toLowerCase()] || colors.low
  }

  if (!data) {
    return (
      <div className="action-items-empty">
        <p>No analysis data available. Please analyze a meeting transcript first.</p>
      </div>
    )
  }

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
    <div className="action-items-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h2 className="text-gradient">Action Items Dashboard</h2>
          <p className="dashboard-subtitle">{data.meeting_title} - {data.meeting_date}</p>
        </div>
        
        <div className="dashboard-stats glass-card">
          <div className="stat-item">
            <span className="stat-label">Total Tasks</span>
            <span className="stat-value">{data.total_action_items}</span>
          </div>
          <div className="stat-divider" />
          <div className="stat-item">
            <span className="stat-label">High Priority</span>
            <span className="stat-value" style={{color: '#f59e0b'}}>{data.high_priority_count}</span>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="dashboard-controls glass-card">
        <div className="control-group">
          <FiFilter />
          <label>Filter:</label>
          <select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)}>
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="control-group">
          <FiTarget />
          <label>Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="priority">Priority</option>
            <option value="assignee">Assignee</option>
          </select>
        </div>

        <div className="view-toggle">
          <motion.button
            className={viewMode === 'grid' ? 'active' : ''}
            onClick={() => setViewMode('grid')}
            whileTap={{ scale: 0.95 }}
          >
            Grid
          </motion.button>
          <motion.button
            className={viewMode === 'kanban' ? 'active' : ''}
            onClick={() => setViewMode('kanban')}
            whileTap={{ scale: 0.95 }}
          >
            Kanban
          </motion.button>
        </div>
      </div>

      {/* Action Items */}
      {viewMode === 'grid' ? (
        <motion.div 
          className="action-items-grid"
          variants={container}
          initial="hidden"
          animate="show"
        >
          {filteredItems.map((actionItem, index) => (
            <motion.div
              key={index}
              className="action-item-card glass-card"
              variants={item}
              whileHover={{ scale: 1.02, y: -4 }}
              style={{
                borderLeft: `4px solid ${getUrgencyColor(actionItem.urgency)}`
              }}
            >
              <div className="card-header">
                <div className={`priority-badge ${getPriorityClass(actionItem.priority_score)}`}>
                  {actionItem.priority_score}/10
                </div>
                <div className="urgency-badge" style={{
                  background: `linear-gradient(135deg, ${getUrgencyColor(actionItem.urgency)}dd, ${getUrgencyColor(actionItem.urgency)}aa)`
                }}>
                  {actionItem.urgency}
                </div>
              </div>

              <h3 className="task-title">{actionItem.task}</h3>

              <div className="task-meta">
                <div className="meta-item">
                  <FiUser className="meta-icon" />
                  <span>{actionItem.assignee}</span>
                </div>
                <div className="meta-item">
                  <FiCalendar className="meta-icon" />
                  <span>{actionItem.deadline}</span>
                </div>
              </div>

              <div className="task-impact">
                <span className="impact-label">Impact:</span>
                <span className="impact-value">{actionItem.impact}</span>
              </div>

              <div className="task-context">
                <p>{actionItem.context}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      ) : (
        <div className="kanban-view">
          {['Critical', 'High', 'Medium', 'Low'].map(urgency => (
            <div key={urgency} className="kanban-column glass-card">
              <div className="kanban-header" style={{
                borderBottom: `3px solid ${getUrgencyColor(urgency)}`
              }}>
                <h3>{urgency}</h3>
                <span className="count-badge">
                  {filteredItems.filter(item => item.urgency.toLowerCase() === urgency.toLowerCase()).length}
                </span>
              </div>
              <div className="kanban-items">
                {filteredItems
                  .filter(item => item.urgency.toLowerCase() === urgency.toLowerCase())
                  .map((actionItem, index) => (
                    <motion.div
                      key={index}
                      className="kanban-card glass-card"
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                      whileHover={{ scale: 1.03 }}
                    >
                      <div className={`priority-score ${getPriorityClass(actionItem.priority_score)}`}>
                        {actionItem.priority_score}
                      </div>
                      <h4>{actionItem.task}</h4>
                      <div className="kanban-meta">
                        <span><FiUser /> {actionItem.assignee}</span>
                        <span><FiCalendar /> {actionItem.deadline}</span>
                      </div>
                    </motion.div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {filteredItems.length === 0 && (
        <div className="empty-state glass-card">
          <p>No action items match the current filters</p>
        </div>
      )}
    </div>
  )
}

export default ActionItemsDashboard
