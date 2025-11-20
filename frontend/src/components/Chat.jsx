import React, { useCallback, useEffect, useRef, useState } from 'react'
import axios from 'axios'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import './ChatInterface.css'

const API_BASE =
  (import.meta.env.VITE_API_BASE_URL && import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '')) ||
  ''

const generateId = () => {
  if (window?.crypto?.randomUUID) {
    return window.crypto.randomUUID()
  }
  return `msg_${Date.now()}_${Math.random().toString(16).slice(2)}`
}

function Chat({ documentId, documentName, sessionId, language, onSessionReady = () => {} }) {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [suggestedQuestions, setSuggestedQuestions] = useState([])
  const [fetchingSuggestions, setFetchingSuggestions] = useState(false)
  const [activeAudioId, setActiveAudioId] = useState(null)
  const [suggestionsExpanded, setSuggestionsExpanded] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)

  const audioRegistry = useRef(new Map())
  const messagesEndRef = useRef(null)
  const messagesSnapshotRef = useRef(messages)
  const historySessionRef = useRef(null)

  useEffect(() => {
    messagesSnapshotRef.current = messages
  }, [messages])

  useEffect(() => {
    if (sessionId) {
      onSessionReady(sessionId)
    }
  }, [sessionId, onSessionReady])

  const resetConversation = useCallback(() => {
    setMessages([])
    setActiveAudioId(null)
    setSuggestionsExpanded(false)
    audioRegistry.current.forEach((audio) => {
      if (audio) {
        audio.pause()
      }
    })
    audioRegistry.current.clear()
  }, [])

  useEffect(() => {
    historySessionRef.current = null
  }, [documentId])

  useEffect(() => {
    if (!documentId) return
    resetConversation()
    const fetchSuggestions = async () => {
      setFetchingSuggestions(true)
      try {
        const response = await axios.post(`${API_BASE}/api/chat/suggestions`, {
          document_id: documentId,
          language
        })
        if (response.data?.success) {
          setSuggestedQuestions(response.data.suggestions || [])
          setSuggestionsExpanded(false)
        } else {
          setSuggestedQuestions([])
        }
      } catch (error) {
        console.error('Failed to load suggestions', error)
        setSuggestedQuestions([])
      } finally {
        setFetchingSuggestions(false)
      }
    }
    fetchSuggestions()
  }, [documentId, language, resetConversation])

  const scrollToBottom = useCallback(() => {
    // Use setTimeout to ensure DOM is updated
    setTimeout(() => {
      const messagesContainer = messagesEndRef.current?.parentElement
      if (messagesContainer) {
        // Scroll to bottom with a small offset to ensure last message is fully visible
        messagesContainer.scrollTop = messagesContainer.scrollHeight + 50
      } else {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
      }
    }, 150)
  }, [])
  
  useEffect(() => {
    // Always scroll to bottom when new messages arrive
    const messagesContainer = messagesEndRef.current?.parentElement
    if (messagesContainer) {
      const isNearBottom = messagesContainer.scrollHeight - messagesContainer.scrollTop - messagesContainer.clientHeight < 300
      // Always scroll if user is near bottom or if it's a new message
      if (isNearBottom || messages.length <= 2) {
        scrollToBottom()
      }
    } else {
      scrollToBottom()
    }
  }, [messages, scrollToBottom])
  
  // Ensure first message is visible when scrolling to top
  useEffect(() => {
    const messagesContainer = messagesEndRef.current?.parentElement
    if (messagesContainer) {
      const handleScroll = () => {
        // If scrolled to top, ensure first message is visible
        if (messagesContainer.scrollTop < 50 && messages.length > 0) {
          // Small adjustment to ensure first message header is visible
          if (messagesContainer.scrollTop === 0) {
            messagesContainer.scrollTop = 5
          }
        }
      }
      messagesContainer.addEventListener('scroll', handleScroll)
      return () => messagesContainer.removeEventListener('scroll', handleScroll)
    }
  }, [messages.length])
  
  // Force scroll on new message - ensure all content is visible
  useEffect(() => {
    if (messages.length > 0) {
      const timer = setTimeout(() => {
        scrollToBottom()
        // Also ensure scroll container has proper height
        const messagesContainer = messagesEndRef.current?.parentElement
        if (messagesContainer) {
          messagesContainer.style.minHeight = '400px'
        }
      }, 200)
      return () => clearTimeout(timer)
    }
  }, [messages.length, scrollToBottom])

  const normalizeHistoryMessages = useCallback((historyData) => {
    if (!Array.isArray(historyData) || historyData.length === 0) {
      return []
    }
    // Case 1: history already in role/content format
    if (historyData[0]?.role && historyData[0]?.content) {
      return historyData.map((entry) => ({
        id: generateId(),
        role: entry.role,
        content: entry.content,
        createdAt: entry.created_at || new Date().toISOString()
      }))
    }
    // Case 2: Supabase rows with user/assistant pairs
    const timeline = []
    historyData.forEach((entry) => {
      if (entry.user_message) {
        timeline.push({
          id: generateId(),
          role: 'user',
          content: entry.user_message,
          createdAt: entry.created_at || new Date().toISOString()
        })
      }
      if (entry.ai_response) {
        timeline.push({
          id: generateId(),
          role: 'assistant',
          content: entry.ai_response,
          audioUrl: entry.audio_path ? `${API_BASE}/api/audio/${entry.audio_path}` : null,
          createdAt: entry.created_at || new Date().toISOString()
        })
      }
    })
    return timeline
  }, [])

  useEffect(() => {
    if (!sessionId || !documentId) return
    if (historySessionRef.current === sessionId) return
    let isMounted = true
    const loadHistory = async () => {
      setLoadingHistory(true)
      try {
        const response = await axios.get(`${API_BASE}/api/chat/history/${sessionId}`)
        if (!isMounted) return
        if (response.data?.success) {
          const historyMessages = normalizeHistoryMessages(response.data.history || [])
          if (historyMessages.length > 0) {
            setMessages(historyMessages)
          }
        }
        historySessionRef.current = sessionId
      } catch (error) {
        console.error('Failed to load chat history', error)
      } finally {
        if (isMounted) {
          setLoadingHistory(false)
        }
      }
    }
    loadHistory()
    return () => {
      isMounted = false
    }
  }, [sessionId, documentId, normalizeHistoryMessages])

  const buildHistoryPayload = useCallback((items) => {
    return items
      .filter((msg) => ['user', 'assistant'].includes(msg.role) && msg.content)
      .map((msg) => ({
        role: msg.role,
        content: msg.content
      }))
  }, [])

  const registerAudio = useCallback((messageId, element) => {
    if (element) {
      audioRegistry.current.set(messageId, element)
    } else {
      audioRegistry.current.delete(messageId)
    }
  }, [])

  const handleAudioPlay = useCallback((messageId, audioElement) => {
    audioRegistry.current.forEach((ref, id) => {
      if (id !== messageId && ref && !ref.paused) {
        ref.pause()
        ref.currentTime = 0
      }
    })
    setActiveAudioId(messageId)
    setMessages((prev) =>
      prev.map((msg) => (msg.id === messageId ? { ...msg, autoPlay: false } : msg))
    )
  }, [])

  const handleAudioPause = useCallback((messageId) => {
    if (activeAudioId === messageId) {
      setActiveAudioId(null)
    }
  }, [activeAudioId])

  const sendChatRequest = useCallback(
    async (text) => {
      if (!text.trim() || loading) return
      if (!documentId) {
        console.warn('Document not loaded yet')
        return
      }

      const trimmed = text.trim()
      const userMessage = {
        id: generateId(),
        role: 'user',
        content: trimmed,
        createdAt: new Date().toISOString()
      }

      setMessages((prev) => [...prev, userMessage])
      setInputValue('')
      setLoading(true)
      
      // Prevent auto-scroll on input
      setTimeout(() => {
        scrollToBottom()
      }, 50)
      
      // Add "Generating..." message
      const generatingMessage = {
        id: generateId(),
        role: 'assistant',
        content: 'Generating...',
        isGenerating: true,
        createdAt: new Date().toISOString()
      }
      setMessages((prev) => [...prev, generatingMessage])

      const historyPayload = buildHistoryPayload([...messagesSnapshotRef.current, userMessage])

      try {
        const response = await axios.post(`${API_BASE}/api/chat/message`, {
          message: trimmed,
          document_id: documentId,
          session_id: sessionId,
          language,
          history: historyPayload
        })

        if (!response.data?.success) {
          throw new Error(response.data?.error || 'Failed to get response')
        }

        // Remove generating message and add actual response
        setMessages((prev) => {
          const filtered = prev.filter(msg => !msg.isGenerating)
          const aiMessage = {
            id: generateId(),
            role: 'assistant',
            content: response.data.response,
            audioUrl: `${API_BASE}${response.data.audio_url}`,
            autoPlay: true,
            createdAt: new Date().toISOString(),
            sources: response.data.sources || []
          }
          return [...filtered, aiMessage]
        })
      } catch (error) {
        console.error('Chat error', error)
        // Remove generating message and add error
        setMessages((prev) => {
          const filtered = prev.filter(msg => !msg.isGenerating)
          return [
            ...filtered,
            {
              id: generateId(),
              role: 'error',
              content: error.response?.data?.error || 'Failed to get response. Please try again.',
              createdAt: new Date().toISOString()
            }
          ]
        })
      } finally {
        setLoading(false)
      }
    },
    [buildHistoryPayload, documentId, language, loading, sessionId]
  )

  const handleSubmit = useCallback(() => {
    sendChatRequest(inputValue)
  }, [inputValue, sendChatRequest])

  const handleSuggestionClick = (question) => {
    sendChatRequest(question)
  }

  return (
    <div className="chat-interface">
      <div className="chat-context-bar">
        <div>
          <p className="chat-context-label">Current textbook</p>
          <h3 className="chat-context-title">{documentName || 'Uploaded Textbook'}</h3>
        </div>
        <div className="chat-context-meta">
          Session ID:&nbsp;
          <span>{sessionId || 'active'}</span>
        </div>
      </div>
      <div className="chat-messages">
        {loadingHistory && messages.length === 0 && (
          <div className="history-loading">Loading your previous conversation…</div>
        )}
        <MessageList
          messages={messages}
          onPlayAudio={handleAudioPlay}
          onPauseAudio={handleAudioPause}
          registerAudio={registerAudio}
          activeAudioId={activeAudioId}
        />
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-section">
        {suggestedQuestions.length > 0 && (
          <div className="suggested-questions">
            <div className="suggestions-header">
              <p>{fetchingSuggestions ? 'Loading suggestions…' : 'Suggested questions'}</p>
              {suggestedQuestions.length > 3 && (
                <button
                  type="button"
                  className="suggestions-toggle"
                  onClick={() => setSuggestionsExpanded((prev) => !prev)}
                >
                  {suggestionsExpanded ? '▾ Hide' : '▴ More'}
                </button>
              )}
            </div>
            <div className="question-buttons">
              {suggestedQuestions
                .slice(0, suggestionsExpanded ? suggestedQuestions.length : 1)
                .map((question, index) => (
                  <button
                    key={`${question}-${index}`}
                    className="suggested-question-btn"
                    onClick={() => handleSuggestionClick(question)}
                    disabled={loading}
                  >
                    {question}
                  </button>
                ))}
            </div>
          </div>
        )}

        <MessageInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSubmit}
          loading={loading}
          placeholder="Ask a question about your textbook..."
        />
      </div>
    </div>
  )
}

export default Chat

