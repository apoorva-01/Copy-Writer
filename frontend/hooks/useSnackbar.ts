import { useState, useCallback } from 'react'

interface SnackbarState {
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  isVisible: boolean
}

interface UseSnackbarReturn {
  snackbar: SnackbarState
  showSuccess: (message: string) => void
  showError: (message: string) => void
  showWarning: (message: string) => void
  showInfo: (message: string) => void
  hideSnackbar: () => void
}

export const useSnackbar = (): UseSnackbarReturn => {
  const [snackbar, setSnackbar] = useState<SnackbarState>({
    message: '',
    type: 'info',
    isVisible: false
  })

  const showSnackbar = useCallback((message: string, type: 'success' | 'error' | 'warning' | 'info') => {
    setSnackbar({
      message,
      type,
      isVisible: true
    })
  }, [])

  const hideSnackbar = useCallback(() => {
    setSnackbar(prev => ({
      ...prev,
      isVisible: false
    }))
  }, [])

  const showSuccess = useCallback((message: string) => {
    showSnackbar(message, 'success')
  }, [showSnackbar])

  const showError = useCallback((message: string) => {
    showSnackbar(message, 'error')
  }, [showSnackbar])

  const showWarning = useCallback((message: string) => {
    showSnackbar(message, 'warning')
  }, [showSnackbar])

  const showInfo = useCallback((message: string) => {
    showSnackbar(message, 'info')
  }, [showSnackbar])

  return {
    snackbar,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    hideSnackbar
  }
} 