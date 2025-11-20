import { supabaseClient } from '../lib/supabaseClient'

const USER_STORAGE_KEY = 'user'

export const sanitizeName = (value = '') =>
  value
    .replace(/[^A-Za-z\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim()

export const readStoredUser = () => {
  const raw = localStorage.getItem(USER_STORAGE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export const writeStoredUser = (user) => {
  if (!user) return
  try {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
  } catch (err) {
    console.warn('Failed to persist user payload', err)
  }
}

export const getStoredUserName = () => {
  const stored = readStoredUser()
  if (!stored) return ''

  const fallbackFromEmail = stored.email ? sanitizeName(stored.email.split('@')[0]) : ''
  const fromMetadata = sanitizeName(
    stored.full_name ||
      stored.user_metadata?.full_name ||
      stored.user_metadata?.name ||
      stored.name ||
      ''
  )

  const resolved = fromMetadata || fallbackFromEmail
  if (!resolved || resolved.toLowerCase() === 'learner') {
    return ''
  }
  return resolved
}

export const ensureUserName = async () => {
  const cachedName = getStoredUserName()
  if (cachedName) {
    return cachedName
  }

  if (!supabaseClient) {
    return ''
  }

  try {
    const { data } = await supabaseClient.auth.getUser()
    const remoteUser = data?.user
    const remoteName = sanitizeName(remoteUser?.user_metadata?.full_name)
    const emailFallback = remoteUser?.email ? sanitizeName(remoteUser.email.split('@')[0]) : ''
    const resolved = remoteName || emailFallback
    if (resolved && resolved.toLowerCase() !== 'learner') {
      const existing = readStoredUser() || {}
      writeStoredUser({ ...existing, full_name: resolved, email: remoteUser?.email })
      return resolved
    }
  } catch (error) {
    console.warn('Unable to fetch Supabase profile', error)
  }
  return ''
}

