import React, { useEffect, useRef, useState } from 'react'
import './AudioPlayer.css'

function AudioPlayer({
  messageId,
  src,
  autoPlay = false,
  onPlayRequest,
  onPauseRequest,
  registerAudio,
  variant = 'full'
}) {
  const audioRef = useRef(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [shouldAutoPlay, setShouldAutoPlay] = useState(autoPlay)

  useEffect(() => {
    setShouldAutoPlay(autoPlay)
  }, [autoPlay, src])

  useEffect(() => {
    if (registerAudio) {
      registerAudio(audioRef.current)
      return () => registerAudio(null)
    }
  }, [registerAudio])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    // Ensure audio doesn't loop
    audio.loop = false
    
    const handleTimeUpdate = () => setCurrentTime(audio.currentTime)
    const handleLoaded = () => {
      setDuration(audio.duration || 0)
      // Auto-play when loaded if shouldAutoPlay is true
      if (shouldAutoPlay && audio.readyState >= 2) {
        playAudio()
      }
    }
    const handlePause = () => {
      setIsPlaying(false)
      onPauseRequest && onPauseRequest(messageId, audio)
    }
    const handleEnded = () => {
      setIsPlaying(false)
      onPauseRequest && onPauseRequest(messageId, audio)
      audio.currentTime = 0
      setShouldAutoPlay(false) // Prevent re-playing
    }
    const handlePlay = () => setIsPlaying(true)

    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('loadedmetadata', handleLoaded)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('play', handlePlay)

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('loadedmetadata', handleLoaded)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('play', handlePlay)
    }
  }, [messageId, onPauseRequest])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return
    
    // Auto-play when audio is ready and shouldAutoPlay is true
    if (shouldAutoPlay) {
      const tryPlay = () => {
        if (audio.readyState >= 2) { // HAVE_CURRENT_DATA or higher
          playAudio().then(() => {
            setShouldAutoPlay(false)
          }).catch(err => {
            console.error('Auto-play failed:', err)
            setShouldAutoPlay(false)
          })
        } else {
          // Wait for audio to load
          audio.addEventListener('canplay', tryPlay, { once: true })
        }
      }
      
      tryPlay()
      
      return () => {
        audio.removeEventListener('canplay', tryPlay)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [shouldAutoPlay, src])

  const formatTime = (seconds) => {
    if (typeof seconds !== 'number' || Number.isNaN(seconds)) return '0:00'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const playAudio = async () => {
    if (!audioRef.current) return
    try {
      if (onPlayRequest) {
        await Promise.resolve(onPlayRequest(messageId, audioRef.current))
      }
      await audioRef.current.play()
      setIsPlaying(true)
    } catch (error) {
      console.error('Error playing audio', error)
    }
  }

  const stopPlayback = () => {
    if (!audioRef.current) return
    audioRef.current.pause()
    audioRef.current.currentTime = 0
    setIsPlaying(false)
    onPauseRequest && onPauseRequest(messageId, audioRef.current)
  }

  const togglePlayback = () => {
    if (!audioRef.current) return
    if (audioRef.current.paused) {
      playAudio()
    } else {
      audioRef.current.pause()
    }
  }

  return (
    <div className={`audio-player ${variant === 'compact' ? 'audio-player-compact' : ''}`}>
      <button
        type="button"
        className="audio-player-btn"
        onClick={togglePlayback}
      >
        {isPlaying ? '⏸ Pause' : '▶️ Play'}
      </button>
      <button
        type="button"
        className="audio-player-stop-btn"
        onClick={stopPlayback}
        disabled={!audioRef.current}
      >
        ■ Stop
      </button>
      {variant !== 'compact' && (
        <div className="audio-player-time">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
      )}
      {variant === 'compact' && (
        <div className="audio-player-time compact">
          {formatTime(currentTime)}
        </div>
      )}
      <audio ref={audioRef} src={src} preload="auto" />
    </div>
  )
}

export default AudioPlayer