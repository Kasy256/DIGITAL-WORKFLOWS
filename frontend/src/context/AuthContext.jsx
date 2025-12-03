"use client"

import { createContext, useContext, useState, useEffect } from "react"
import { authAPI } from "../services/api"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = authAPI.getUser()
    if (storedUser && authAPI.isAuthenticated()) {
      setUser(storedUser)
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const result = await authAPI.login(email, password)
    if (result.ok) {
      setUser(result.data.user)
      return { success: true }
    }
    return { success: false, error: result.data.error }
  }

  const signup = async (userData) => {
    const result = await authAPI.register(userData)
    if (result.ok) {
      setUser(result.data.user)
      return { success: true }
    }
    return { success: false, error: result.data.error }
  }

  const logout = () => {
    authAPI.logout()
    setUser(null)
  }

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    isAuthenticated: !!user,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}


