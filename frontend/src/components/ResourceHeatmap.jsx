import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import './ResourceHeatmap.css'

const ResourceHeatmap = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="chart-container">
        <h3>Resource Allocation Heatmap</h3>
        <div className="no-data">No resource data available</div>
      </div>
    )
  }

  // Determine color based on task count
  const getColor = (taskCount) => {
    if (taskCount >= 8) return '#ef4444' // Critical - Red
    if (taskCount >= 5) return '#f59e0b' // Warning - Orange
    if (taskCount >= 3) return '#3b82f6' // Normal - Blue
    return '#10b981' // Light - Green
  }

  return (
    <div className="chart-container">
      <h3>Resource Allocation Heatmap</h3>
      <div className="heatmap-legend">
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#10b981' }}></div>
          <span>1-2 tasks</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#3b82f6' }}></div>
          <span>3-4 tasks</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#f59e0b' }}></div>
          <span>5-7 tasks</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#ef4444' }}></div>
          <span>8+ tasks (Over-allocated)</span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 100, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
          <XAxis 
            type="number" 
            stroke="#cbd5e1"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            type="category" 
            dataKey="resource" 
            stroke="#cbd5e1"
            style={{ fontSize: '12px' }}
            width={90}
          />
          <Tooltip 
            contentStyle={{ 
              background: 'rgba(26, 26, 46, 0.95)', 
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              color: '#f8fafc'
            }}
            labelStyle={{ color: '#f8fafc' }}
            itemStyle={{ color: '#f8fafc' }}
            formatter={(value, name) => [value, 'Active Tasks']}
          />
          <Bar dataKey="taskCount" radius={[0, 8, 8, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.taskCount)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default ResourceHeatmap
