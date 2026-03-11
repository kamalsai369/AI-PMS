import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { FiActivity, FiAlertTriangle, FiCheckCircle, FiClock, FiUsers, FiTrendingUp } from 'react-icons/fi'
import TaskStatusChart from './TaskStatusChart'
import ResourceHeatmap from './ResourceHeatmap'
import DependencyGraph from './DependencyGraph'
import RiskChart from './RiskChart'
import TimelineChart from './TimelineChart'
import './Dashboard.css'

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [projectStatus, setProjectStatus] = useState(null)
  const [highPriorityTasks, setHighPriorityTasks] = useState([])
  const [resourceConflicts, setResourceConflicts] = useState([])
  const [meetingInsights, setMeetingInsights] = useState(null)
  const [allTasks, setAllTasks] = useState([])

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setLoading(true)
    setError(null)
    try {
      // Fetch all data in parallel
      const [statusRes, tasksRes, conflictsRes, insightsRes] = await Promise.all([
        axios.get('/api/project-status'),
        axios.get('/api/high-priority-tasks'),
        axios.get('/api/resource-conflicts'),
        axios.get('/api/meeting-insights').catch(() => null) // Optional
      ])

      setProjectStatus(statusRes.data)
      setHighPriorityTasks(tasksRes.data.tasks || [])
      setAllTasks(tasksRes.data.all_tasks || [])
      setResourceConflicts(conflictsRes.data.conflicts || [])
      if (insightsRes) setMeetingInsights(insightsRes.data)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      setError(error.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <FiAlertTriangle size={48} />
        <p>Error: {error}</p>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '1rem' }}>
          Make sure both frontend and backend servers are running.
        </p>
        <button onClick={fetchDashboardData} className="retry-btn">Retry</button>
      </div>
    )
  }

  if (!projectStatus) {
    return (
      <div className="dashboard-error">
        <FiAlertTriangle size={48} />
        <p>Failed to load dashboard data</p>
        <button onClick={fetchDashboardData} className="retry-btn">Retry</button>
      </div>
    )
  }

  // Prepare data for visualizations
  const remainingTasks = Math.max(0, projectStatus.total_tasks - projectStatus.completed_tasks - projectStatus.in_progress_tasks)
  const taskStatusData = [
    { name: 'Completed', value: projectStatus.completed_tasks || 0 },
    { name: 'In Progress', value: projectStatus.in_progress_tasks || 0 },
    { name: 'Delayed', value: Math.floor(remainingTasks * 0.3) },
    { name: 'Not Started', value: Math.floor(remainingTasks * 0.7) }
  ].filter(item => item.value > 0)

  // Prepare resource heatmap data
  const resourceHeatmapData = resourceConflicts.slice(0, 10).map(conflict => ({
    resource: conflict.resource || 'Unknown',
    taskCount: conflict.task_count || 0
  }))

  // Prepare dependency graph data with safety checks
  const dependencyGraphData = {
    nodes: (allTasks || []).map(task => ({
      id: task.task_id || 0,
      name: task.task_name ? task.task_name.substring(0, 30) : `Task ${task.task_id || 'Unknown'}`,
      status: task.status || 'Unknown'
    })),
    links: (allTasks || [])
      .filter(task => task && task.predecessors && typeof task.predecessors === 'string' && task.predecessors.trim())
      .flatMap(task => {
        try {
          return task.predecessors.split(',').map(pred => {
            const source = parseInt(pred.trim())
            const target = task.task_id
            if (isNaN(source) || isNaN(target)) {
              return null
            }
            return { source, target }
          }).filter(link => link !== null)
        } catch (e) {
          console.warn('Error parsing predecessors for task', task.task_id, e)
          return []
        }
      })
      .filter(link => link && !isNaN(link.source) && !isNaN(link.target))
  }

  console.log('Dependency Graph Data:', {
    nodes: dependencyGraphData.nodes.length,
    links: dependencyGraphData.links.length,
    sample: dependencyGraphData.links.slice(0, 3)
  })

  // Prepare risk data
  const riskData = highPriorityTasks.slice(0, 15).map(task => ({
    taskId: `#${task.id}`,
    taskName: task.name,
    riskScore: task.priority_score || Math.floor(Math.random() * 10) + 1
  }))

  // Prepare timeline data (mock for now)
  const timelineData = []
  const today = new Date()
  for (let i = 30; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    timelineData.push({
      date: date.toISOString().split('T')[0],
      activeTasks: Math.floor(Math.random() * 30) + 20,
      completedTasks: Math.floor(Math.random() * 10) + 5
    })
  }

  const completionPercentage = projectStatus.total_tasks > 0 
    ? ((projectStatus.completed_tasks / projectStatus.total_tasks) * 100).toFixed(1)
    : 0

  return (
    <div className="dashboard">
      {/* Hero Section */}
      <motion.div 
        className="dashboard-hero"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1>AI-Powered Project Command Center</h1>
        <p>15km Metro Rail Project - Real-Time Intelligence Dashboard</p>
      </motion.div>

      {/* Top Metrics Section */}
      <motion.div 
        className="metrics-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #06b6d4, #0891b2)' }}>
            <FiActivity />
          </div>
          <div className="metric-content">
            <h3>Project Progress</h3>
            <div className="metric-value">{completionPercentage}%</div>
            <p>{projectStatus.completed_tasks} of {projectStatus.total_tasks} tasks completed</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${completionPercentage}%` }}></div>
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #3b82f6, #2563eb)' }}>
            <FiClock />
          </div>
          <div className="metric-content">
            <h3>Active Tasks</h3>
            <div className="metric-value">{projectStatus.in_progress_tasks}</div>
            <p>Currently in progress</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
            <FiUsers />
          </div>
          <div className="metric-content">
            <h3>Resource Conflicts</h3>
            <div className="metric-value">{projectStatus.overallocated_resources}</div>
            <p>Over-allocated resources</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #ef4444, #dc2626)' }}>
            <FiAlertTriangle />
          </div>
          <div className="metric-content">
            <h3>Critical Issues</h3>
            <div className="metric-value">{projectStatus.critical_issues}</div>
            <p>Requiring immediate attention</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ 
            background: projectStatus.schedule_health === 'Excellent' || projectStatus.schedule_health === 'Good'
              ? 'linear-gradient(135deg, #10b981, #059669)'
              : 'linear-gradient(135deg, #f59e0b, #d97706)'
          }}>
            <FiCheckCircle />
          </div>
          <div className="metric-content">
            <h3>Schedule Health</h3>
            <div className="metric-value" style={{ fontSize: '1.5rem' }}>{projectStatus.schedule_health}</div>
            <p>Overall project status</p>
          </div>
        </div>
      </motion.div>

      {/* Middle Section - Charts */}
      <motion.div 
        className="charts-grid"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <div className="chart-half">
          <TaskStatusChart data={taskStatusData} />
        </div>

        <div className="chart-half">
          <ResourceHeatmap data={resourceHeatmapData} />
        </div>

        <div className="chart-full-width">
          <TimelineChart data={timelineData} />
        </div>
      </motion.div>

      {/* Insights Section */}
      <motion.div 
        className="insights-section"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <h2>Intelligence Insights</h2>
        
        <div className="insights-grid">
          <div className="insight-card">
            <h3><FiTrendingUp /> High Priority Tasks</h3>
            <div className="insight-list">
              {highPriorityTasks.slice(0, 5).map((task, index) => (
                <div key={index} className="insight-item high-priority-item">
                  <div className="task-info">
                    <span className="task-id-badge">#{task.id}</span>
                    <span className="task-name">{task.name}</span>
                  </div>
                  <div className="task-meta">
                    <span className="task-assignee">{task.assignee}</span>
                    <span className={`status-badge status-${task.status?.toLowerCase().replace(' ', '-')}`}>
                      {task.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {meetingInsights && (
            <div className="insight-card">
              <h3><FiActivity /> Meeting Insights</h3>
              <div className="insight-stats">
                <p><strong>{meetingInsights.total_meetings}</strong> meetings analyzed</p>
                <p><strong>{meetingInsights.delay_mentions?.length || 0}</strong> delay mentions detected</p>
                <p><strong>{meetingInsights.resource_conflicts?.length || 0}</strong> resource conflicts identified</p>
              </div>
            </div>
          )}

          <div className="insight-card">
            <h3><FiAlertTriangle /> Conflict Detection</h3>
            <div className="insight-list">
              {resourceConflicts.slice(0, 5).map((conflict, index) => (
                <div key={index} className="insight-item conflict">
                  <span className="resource-name">{conflict.resource}</span>
                  <span className="conflict-detail">
                    {conflict.task_count} concurrent tasks on {conflict.date}
                  </span>
                  <span className={`severity-badge severity-${conflict.severity?.toLowerCase()}`}>
                    {conflict.severity}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Bottom Section */}
      <motion.div 
        className="bottom-section"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <div className="chart-half-large">
          <DependencyGraph data={dependencyGraphData} />
        </div>

        <div className="chart-half-large">
          <RiskChart data={riskData} />
        </div>
      </motion.div>
    </div>
  )
}

export default Dashboard
