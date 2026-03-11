import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Header from './components/Header'
import TranscriptAnalyzer from './components/TranscriptAnalyzer'
import ActionItemsDashboard from './components/ActionItemsDashboard'
import ConflictDetector from './components/ConflictDetector'
import Dashboard from './components/Dashboard'
import './App.css'

function App() {
  const [activeView, setActiveView] = useState('dashboard')
  const [analysisData, setAnalysisData] = useState(null)

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data)
    setActiveView('actions')
  }

  const renderView = () => {
    switch (activeView) {
      case 'dashboard':
        return <Dashboard />
      case 'analyzer':
        return <TranscriptAnalyzer onAnalysisComplete={handleAnalysisComplete} />
      case 'actions':
        return <ActionItemsDashboard data={analysisData} />
      case 'conflicts':
        return <ConflictDetector data={analysisData} />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="app">
      <Header activeView={activeView} onViewChange={setActiveView} />
      
      <main className="main-content">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeView}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderView()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App
