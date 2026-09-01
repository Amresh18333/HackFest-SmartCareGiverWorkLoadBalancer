import { useState, useEffect } from 'react'

export function ToastContainer() {
  const [toasts, setToasts] = useState([])
  
  const addToast = (message, type = 'info', duration = 4000) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, duration)
  }
  
  // Expose globally for easy access
  useEffect(() => {
    window.showToast = addToast
    return () => { delete window.showToast }
  }, [])
  
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => (
        <div 
          key={toast.id}
          className={`toast pointer-events-auto ${
            toast.type === 'success' ? 'toast-success' :
            toast.type === 'error' ? 'toast-error' : 'toast-info'
          }`}
        >
          {toast.message}
        </div>
      ))}
    </div>
  )
}

// Helper to show toast from anywhere
export function showToast(message, type = 'info') {
  if (window.showToast) {
    window.showToast(message, type)
  }
}