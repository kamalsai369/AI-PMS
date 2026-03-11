import { useEffect, useRef } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import './DependencyGraph.css'

const DependencyGraph = ({ data }) => {
  const graphRef = useRef()

  if (!data || !data.nodes || data.nodes.length === 0) {
    return (
      <div className="chart-container">
        <h3>Task Dependency Network</h3>
        <div className="no-data">No dependency data available</div>
      </div>
    )
  }

  // Prepare graph data
  const graphData = {
    nodes: data.nodes.map(node => ({
      id: node.id,
      name: node.name,
      status: node.status,
      wbs: node.wbs || '',
      val: 10 // Node size
    })),
    links: data.links.map(link => ({
      source: link.source,
      target: link.target,
      type: link.type || 'dependency',
      value: 1
    }))
  }

  const getNodeColor = (status) => {
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
    <div className="chart-container dependency-graph-container">
      <h3>Task Dependency Network</h3>
      <div className="graph-info">
        {data.nodes.length} tasks, {data.links.length} connections 
        ({data.links.filter(l => l.type === 'dependency').length} dependencies, 
        {data.links.filter(l => l.type === 'hierarchy').length} WBS hierarchy)
      </div>
      
      <div className="dependency-graph">
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          nodeLabel={(node) => `${node.name} (${node.wbs || node.id})`}
          nodeColor={node => getNodeColor(node.status)}
          nodeRelSize={6}
          linkColor={(link) => link.type === 'hierarchy' ? 'rgba(139, 92, 246, 0.3)' : 'rgba(59, 130, 246, 0.3)'}
          linkWidth={(link) => link.type === 'hierarchy' ? 1 : 2}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={1}
          linkDirectionalParticles={(link) => link.type === 'dependency' ? 2 : 0}
          linkDirectionalParticleWidth={2}
          backgroundColor="transparent"
          width={Math.min(window.innerWidth - 100, 1200)}
          height={500}
          cooldownTicks={100}
          onNodeClick={(node) => {
            console.log('Clicked node:', node)
          }}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.name
            const fontSize = 12/globalScale
            ctx.font = `${fontSize}px Sans-Serif`
            const textWidth = ctx.measureText(label).width
            const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.4)

            // Draw node circle
            ctx.beginPath()
            ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false)
            ctx.fillStyle = getNodeColor(node.status)
            ctx.fill()
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)'
            ctx.lineWidth = 1.5 / globalScale
            ctx.stroke()

            // Draw label background
            ctx.fillStyle = 'rgba(26, 26, 46, 0.9)'
            ctx.fillRect(
              node.x - bckgDimensions[0] / 2, 
              node.y - bckgDimensions[1] / 2 + 10, 
              bckgDimensions[0], 
              bckgDimensions[1]
            )

            // Draw label text
            ctx.textAlign = 'center'
            ctx.textBaseline = 'middle'
            ctx.fillStyle = '#f8fafc'
            ctx.fillText(label, node.x, node.y + 10)
          }}
        />
      </div>

      <div className="dependency-legend">
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
        <div className="legend-item">
          <div className="legend-line" style={{ background: 'rgba(59, 130, 246, 0.6)', width: '30px', height: '2px' }}></div>
          <span>Task Dependency</span>
        </div>
        <div className="legend-item">
          <div className="legend-line" style={{ background: 'rgba(139, 92, 246, 0.6)', width: '30px', height: '1px' }}></div>
          <span>WBS Hierarchy</span>
        </div>
      </div>
    </div>
  )
}

export default DependencyGraph
