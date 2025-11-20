import React from 'react'
import Message from './Message'
import './MessageList.css'

function MessageList({ messages, onPlayAudio, onPauseAudio, registerAudio, activeAudioId }) {
  return (
    <div className="message-list">
      {messages.length === 0 ? (
        <div className="empty-state">
          <p>👋 Start a conversation with your AI tutor!</p>
          <p>Ask questions about the uploaded textbook.</p>
        </div>
      ) : (
        messages.map((message) => (
          <Message
            key={message.id}
            message={message}
            onPlayAudio={onPlayAudio}
            onPauseAudio={onPauseAudio}
            registerAudio={registerAudio}
            isActive={activeAudioId === message.id}
          />
        ))
      )}
    </div>
  )
}

export default MessageList
