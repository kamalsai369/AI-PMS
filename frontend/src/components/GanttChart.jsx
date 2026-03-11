import { useState, useEffect, useRef } from 'react'
import './GanttChart.css'

const GanttChart = ({ tasks }) => {
  const [visibleTasks, setVisibleTasks] = useState([])
  const scrollRef = useRef(null)

  useEffect(() => {
    if (tasks && tasks.length > 0) {
      // Show first 20 tasks to avoid performance issues
      setVisibleTasks(tasks.slice(0, 20))
    }
  }, [tasks])

  if (!tasks || tasks.length === 0) {
    return (
      <div className="chart-container">
        <h3>Project Timeline - Gantt Chart</h3>
        <div className="no-data">No timeline data available</div>
      </div>
    )
  }

  // Find the earliest and latest dates
  const dates = tasks.flatMap(t => [new Date(t.start_date), new Date(t.end_date)])
  const minDate = new Date(Math.min(...dates))
  const maxDate = new Date(Math.max(...dates))
  
  // Calculate time span in days
  const totalDays = Math.ceil((maxDate - minDate) / (1000 * 60 * 60 * 24))
  const pixelsPerDay = 3 // Adjust for zoom level

  // Generate month markers
  const monthMarkers = []
  let currentDate = new Date(minDate)
  currentDate.setDate(1)
  
  while (currentDate <= maxDate) {
    const daysFromStart = Math.ceil((currentDate - minDate) / (1000 * 60 * 60 * 24))
    monthMarkers.push({
      date: new Date(currentDate),
      position: daysFromStart * pixelsPerDay,
      label: currentDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    })
    currentDate.setMonth(currentDate.getMonth() + 1)
  }

  // Calculate bar position and width for each task
  const calculateBar = (task) => {
    const start = new Date(task.start_date)
    const end = new Date(task.end_date)
    const startOffset = Math.ceil((start - minDate) / (1000 * 60 * 60 * 24))
    const duration = Math.ceil((end - start) / (1000 * 60 * 60 * 24))
    
    return {
      left: startOffset * pixelsPerDay,
      width: Math.max(duration * pixelsPerDay, 10) // Minimum 10px width
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      'Completed': '#10b981',
      'In Progress': '#3b82f6',
      'Delayed': '#ef4444',
      'On Hold': '#f59e0b',
      'Not Started': '#6b7280'
    }
    return colors[status] || '#6b7280'
  }

  return (
    <div className="chart-container gantt-container">
      <div className="gantt-header">
        <h3>Project Timeline - Gantt Chart</h3>
        <div className="gantt-info">
          Showing {visibleTasks.length} of {tasks.length} tasks
        </div>
      </div>

      <div className="gantt-chart" ref={scrollRef}>
        <div className="gantt-timeline">
          <div className="gantt-months" style={{ width: totalDays * pixelsPerDay }}>
            {monthMarkers.map((marker, index) => (
              <div
                key={index}
                className="month-marker"
                style={{ left: marker.position }}
              >
                {marker.label}
              </div>
            ))}
          </div>

          <div className="gantt-grid" style={{ width: totalDays * pixelsPerDay }}>
            {monthMarkers.map((marker, index) => (
              <div
                key={index}
                className="grid-line"
                style={{ left: marker.position }}
              />
            ))}
          </div>
        </div>

        <div className="gantt-tasks">
          {visibleTasks.map((task, index) => {
            const bar = calculateBar(task)
            return (
              <div key={index} className="gantt-row">
                <div className="task-label" title={task.task_name}>
                  <span className="task-id">{task.task_id}</span>
                  <span className="task-name">{task.task_name}</span>
                </div>
                <div className="task-timeline" style={{ width: totalDays * pixelsPerDay }}>
                  <div
                    className="task-bar"
                    style={{
                      left: bar.left,
                      width: bar.width,
                      background: getStatusColor(task.status)
                    }}
                    title={`${task.task_name}\n${task.start_date} - ${task.end_date}\nStatus: ${task.status}`}
                  >
                    <span className="task-bar-label">{task.task_name}</span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="gantt-legend">
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#10b981' }}></div>
          <span>Completed</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#3b82f6' }}></div>
          <span>In Progress</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#ef4444' }}></div>
          <span>Delayed</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#f59e0b' }}></div>
          <span>On Hold</span>
        </div>
      </div>
    </div>
  )
}

export default GanttChart
