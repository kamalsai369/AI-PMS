import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts'
import './RiskChart.css'

const RiskChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="chart-container">
        <h3>Schedule Risk Analysis</h3>
        <div className="no-data">No risk data available</div>
      </div>
    )
  }

  // Color coding based on risk score (0-10 scale)
  const getColor = (riskScore) => {
    if (riskScore >= 5.5) return '#ef4444' // High risk
    if (riskScore >= 4.5) return '#f59e0b' // Medium risk
    return '#10b981' // Low risk
  }

  return (
    <div className="chart-container">
      <h3>Schedule Risk Analysis</h3>
      <div className="risk-summary">
        <div className="risk-stat high">
          <span className="risk-count">{data.filter(d => d.riskScore >= 5.5).length}</span>
          <span className="risk-label">High Risk</span>
        </div>
        <div className="risk-stat medium">
          <span className="risk-count">{data.filter(d => d.riskScore >= 4.5 && d.riskScore < 5.5).length}</span>
          <span className="risk-label">Medium Risk</span>
        </div>
        <div className="risk-stat low">
          <span className="risk-count">{data.filter(d => d.riskScore < 4.5).length}</span>
          <span className="risk-label">Low Risk</span>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={450}>
        <BarChart data={data.slice(0, 20)} margin={{ left: 20, right: 30, top: 10, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
          <XAxis 
            dataKey="taskId" 
            stroke="#cbd5e1"
            style={{ fontSize: '11px' }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            stroke="#cbd5e1"
            style={{ fontSize: '12px' }}
            domain={[0, 10]}
            label={{ value: 'Risk Score (0-10)', angle: -90, position: 'insideLeft', style: { fill: '#cbd5e1' } }}
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
            formatter={(value, name, props) => [
              `Risk Score: ${value}`,
              props.payload.taskName
            ]}
          />
          <Bar dataKey="riskScore" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.riskScore)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="risk-factors">
        <h4>Key Risk Factors:</h4>
        <ul>
          <li>Missing dependencies or circular references</li>
          <li>Resource over-allocation conflicts</li>
          <li>Unrealistic durations or tight schedules</li>
          <li>Tasks with multiple blockers</li>
        </ul>
      </div>
    </div>
  )
}

export default RiskChart
