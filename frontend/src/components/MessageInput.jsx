import React from 'react'
import './MessageInput.css'

function MessageInput({ value, onChange, onSend, loading, placeholder }) {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSend()
      // Prevent scroll jump
      e.target.blur()
    }
  }

  return (
    <div className="message-input">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        disabled={loading}
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


