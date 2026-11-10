import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { getToken, portal, setToken } from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [developer, setDeveloper] = useState(null)
  const [loading, setLoading] = useState(Boolean(getToken()))

  const refresh = useCallback(async () => {
    try {
      setDeveloper(await portal('/me'))
    } catch {
      setToken(null) // expired or invalid token
      setDeveloper(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (getToken()) refresh()
  }, [refresh])

  const login = async (email, password) => {
    const { access_token } = await portal('/auth/token', { method: 'POST', form: { username: email, password } })
    setToken(access_token)
    await refresh()
  }

  const signup = async (email, password) => {
    const { access_token } = await portal('/auth/signup', { method: 'POST', body: { email, password } })
    setToken(access_token)
    await refresh()
  }

  const logout = () => {
    setToken(null)
    setDeveloper(null)
  }

  return (
    <AuthContext.Provider value={{ developer, loading, login, signup, logout }}>{children}</AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
