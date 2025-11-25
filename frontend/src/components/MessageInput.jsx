import React from 'react'
import './MessageInput.css'

function MessageInput({ value, onChange, onSend, loading, placeholder }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSend()
    }
  }

  return (
    <div className="message-input">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={1}
        className="message-textarea"
      />
      <button
        onClick={onSend}
        disabled={!value.trim() || loading}
        className="send-button"
      >
        {loading ? 'Sending...' : 'Send'}
      </button>
    </div>
  )
}

export default MessageInput


