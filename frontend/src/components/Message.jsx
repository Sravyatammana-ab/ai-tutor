import React, { useEffect, useState } from 'react'
import AudioPlayer from './AudioPlayer'
import './Message.css'

function Message({ message, onPlayAudio, onPauseAudio, registerAudio, isActive }) {
  const isUser = message.role === 'user'
  const isError = message.role === 'error'
  const isGenerating = message.isGenerating
  const [shouldAutoPlay, setShouldAutoPlay] = useState(Boolean(message.autoPlay))

  useEffect(() => {
    setShouldAutoPlay(Boolean(message.autoPlay))
  }, [message.autoPlay, message.id])

  const timestampLabel = message.createdAt
    ? new Date(message.createdAt).toLocaleTimeString()
    : ''

  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'} ${isError ? 'message-error' : ''} ${isGenerating ? 'message-generating' : ''}`}>
      <div className="message-content">
        <div className="message-header">
          <span className="message-role">
            {isUser ? '👤 You' : isError ? '❌ Error' : '🤖 AI Tutor'}
          </span>
          <div className="message-meta">
            <span className="message-time">{timestampLabel}</span>
          </div>
        </div>

        {(message.content || isGenerating) && (
          <div className="message-text">
            {isGenerating ? (
              <div className="generating-indicator">
                <span className="generating-dots">
                  <span>.</span><span>.</span><span>.</span>
                </span>
              </div>
            ) : (
              message.content
            )}
          </div>
        )}

        {!isUser && !isError && message.audioUrl && (
          <div className="message-audio">
            <AudioPlayer
              messageId={message.id}
              src={message.audioUrl}
              autoPlay={shouldAutoPlay}
              onPlayRequest={onPlayAudio}
              onPauseRequest={onPauseAudio}
              registerAudio={(audioElement) => registerAudio(message.id, audioElement)}
              isActive={isActive}
              variant="compact"
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default Message
