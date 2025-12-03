"use client"

import { Leaf, LogOut, User } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { useNavigate } from "react-router-dom"

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  return (
    <nav className="bg-foreground text-white shadow-md">
      <div className="container mx-auto px-4 py-4 max-w-7xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-primary p-2 rounded-lg">
              <Leaf size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold">EReceipt</h1>
              <p className="text-xs text-gray-400">Paperless • Green Computing • Digital Workflow</p>
            </div>
          </div>

          {isAuthenticated ? (
            <div className="flex items-center gap-4">
              {/* User Info */}
              <div className="flex items-center gap-3 bg-white/10 px-4 py-2 rounded-lg">
                <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                  <User size={16} />
                </div>
                <div className="hidden sm:block">
                  <p className="text-sm font-medium">{user?.business_name || "My Business"}</p>
                  <p className="text-xs text-gray-400">{user?.email}</p>
                </div>
              </div>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 hover:text-red-200 px-4 py-2 rounded-lg transition-colors"
              >
                <LogOut size={18} />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          ) : (
            <div className="text-right">
              <p className="text-sm text-gray-300">Digital Receipt Management System</p>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
