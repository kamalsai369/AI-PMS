import { motion } from 'framer-motion'
import { FiHome, FiFileText, FiCheckCircle, FiAlertTriangle } from 'react-icons/fi'
import './Header.css'

const Header = ({ activeView, onViewChange }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: FiHome },
    { id: 'analyzer', label: 'Analyze Meeting', icon: FiFileText },
    { id: 'actions', label: 'Action Items', icon: FiCheckCircle },
    { id: 'conflicts', label: 'Conflicts', icon: FiAlertTriangle }
  ]

  return (
    <motion.header 
      className="header glass-card"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="header-content">
        <div className="logo">
          <div className="logo-icon">
            <span className="text-gradient">AI</span>
          </div>
          <h1 className="logo-text">
            <span className="text-gradient">AI-PMS</span>
            <span className="logo-subtitle">Intelligent Dashboard</span>
          </h1>
        </div>

        <nav className="nav">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <motion.button
                key={item.id}
                className={`nav-item ${activeView === item.id ? 'active' : ''}`}
                onClick={() => onViewChange(item.id)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Icon className="nav-icon" />
                <span>{item.label}</span>
                {activeView === item.id && (
                  <motion.div
                    className="nav-indicator"
                    layoutId="activeNav"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
              </motion.button>
            )
          })}
        </nav>
      </div>
    </motion.header>
  )
}

export default Header
