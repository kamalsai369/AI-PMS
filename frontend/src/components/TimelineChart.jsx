import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, AreaChart } from 'recharts'
import './TimelineChart.css'

const TimelineChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="chart-container">
        <h3>Project Activity Timeline</h3>
        <div className="no-data">No timeline data available</div>
      </div>
    )
  }

  return (
    <div className="chart-container">
      <h3>Project Activity Timeline</h3>
      <div className="timeline-info">
        Daily active tasks and completion trend
      </div>
      
      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={data} margin={{ left: 10, right: 20, top: 10, bottom: 10 }}>
          <defs>
            <linearGradient id="colorActive" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
            </linearGradient>
            <linearGradient id="colorComplete" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
          <XAxis 
            dataKey="date" 
            stroke="#cbd5e1"
            style={{ fontSize: '11px' }}
            tickFormatter={(value) => {
              const date = new Date(value)
              return `${date.getMonth() + 1}/${date.getDate()}`
            }}
          />
          <YAxis 
            stroke="#cbd5e1"
            style={{ fontSize: '12px' }}
            label={{ value: 'Tasks', angle: -90, position: 'insideLeft', style: { fill: '#cbd5e1' } }}
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
            labelFormatter={(value) => {
              const date = new Date(value)
              return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
            }}
          />
          <Legend 
            wrapperStyle={{ color: '#cbd5e1', paddingTop: '10px' }}
            iconType="circle"
          />
          <Area 
            type="monotone" 
            dataKey="activeTasks" 
            stroke="#3b82f6" 
            fillOpacity={1} 
            fill="url(#colorActive)" 
            name="Active Tasks"
          />
          <Area 
            type="monotone" 
            dataKey="completedTasks" 
            stroke="#10b981" 
            fillOpacity={1} 
            fill="url(#colorComplete)" 
            name="Completed Tasks"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export default TimelineChart
