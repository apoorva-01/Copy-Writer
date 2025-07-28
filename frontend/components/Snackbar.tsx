'use client'

import React, { useEffect } from 'react'

interface SnackbarProps {
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  isVisible: boolean
  onClose: () => void
  duration?: number
}

const Snackbar: React.FC<SnackbarProps> = ({
  message,
  type,
  isVisible,
  onClose,
  duration = 5000
}) => {
  useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(() => {
        onClose()
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [isVisible, duration, onClose])

  if (!isVisible) return null

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <i className="fas fa-check-circle"></i>
      case 'error':
        return <i className="fas fa-exclamation-circle"></i>
      case 'warning':
        return <i className="fas fa-exclamation-triangle"></i>
      case 'info':
        return <i className="fas fa-info-circle"></i>
      default:
        return <i className="fas fa-info-circle"></i>
    }
  }

  return (
    <div className={`snackbar ${type} ${isVisible ? 'show' : ''}`}>
      <div className="snackbar-content">
        <span className="snackbar-icon">
          {getIcon()}
        </span>
        <span className="snackbar-message">{message}</span>
        <button 
          className="snackbar-close" 
          onClick={onClose}
          aria-label="Close notification"
        >
          <i className="fas fa-times"></i>
        </button>
        {duration > 0 && isVisible && (
          <div className="snackbar-progress"></div>
        )}
      </div>
    </div>
  )
}

export default Snackbar 