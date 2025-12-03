"use client"

import { useState, useEffect } from "react"
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider, useAuth } from "./context/AuthContext"
import Navbar from "./components/Navbar"
import Footer from "./components/Footer"
import ReceiptForm from "./components/ReceiptForm"
import ReceiptPreview from "./components/ReceiptPreview"
import ReceiptList from "./components/ReceiptList"
import Login from "./pages/Login"
import Signup from "./pages/Signup"
import { receiptsAPI, notificationsAPI } from "./services/api"

// Protected Route Component
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500" />
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

// Dashboard Component (main app content)
function Dashboard() {
  const [receipts, setReceipts] = useState([])
  const [formData, setFormData] = useState(null)
  const [showPreview, setShowPreview] = useState(false)
  const [toastMessage, setToastMessage] = useState("")
  const [isSending, setIsSending] = useState(false)

  // Load receipts on mount
  useEffect(() => {
    loadReceipts()
  }, [])

  const loadReceipts = async () => {
    try {
      const response = await receiptsAPI.getAll(1, 20)
      if (response.ok && response.data.receipts) {
        setReceipts(response.data.receipts)
      }
    } catch (error) {
      console.error("Failed to load receipts:", error)
    }
  }

  const checkNotificationConfig = async () => {
    try {
      const response = await notificationsAPI.getConfig()
      if (response.ok) {
        const config = response.data
        if (!config.email?.configured && !config.sms?.configured) {
          return {
            error: true,
            message: "Email and SMS services are not configured. Please configure at least one service in your backend environment variables."
          }
        }
        if (!config.email?.configured) {
          return {
            warning: true,
            message: "Email service is not configured. Only SMS will be sent if phone number is available."
          }
        }
      }
    } catch (error) {
      console.error("Failed to check notification config:", error)
    }
    return null
  }

  // Handle form submission
  const handleCreateReceipt = (data) => {
    // Generate receipt number
    const receiptNumber = `REC-${Date.now()}`

    setFormData({
      ...data,
      receiptNumber,
      timestamp: new Date(),
      status: "Not Sent",
    })
    setShowPreview(true)
  }

  // Handle sending receipt
  const handleSendReceipt = async () => {
    if (!formData) return

    setIsSending(true)
    setToastMessage("")

    try {
      // Check notification configuration
      const configCheck = await checkNotificationConfig()
      if (configCheck?.error) {
        throw new Error(configCheck.message)
      }
      if (configCheck?.warning) {
        console.warn(configCheck.message)
      }
      // Prepare receipt data for backend
      const receiptData = {
        customer_name: formData.customerName,
        customer_email: formData.customerEmail,
        customer_phone: formData.customerPhone || null,
        transaction_date: formData.transactionDate,
        items: formData.items.map(item => ({
          name: item.name,
          quantity: item.quantity,
          price: item.price
        })),
        subtotal: formData.subtotal,
        tax_rate: formData.taxRate,
        tax: formData.tax,
        total: formData.total,
        receipt_number: formData.receiptNumber
      }

      // Step 1: Create receipt in database
      const createResponse = await receiptsAPI.create(receiptData)
      
      if (!createResponse.ok) {
        throw new Error(createResponse.data.error || "Failed to create receipt")
      }

      const receiptId = createResponse.data.receipt?.id || createResponse.data.receipt?._id
      if (!receiptId) {
        throw new Error("Failed to get receipt ID from response")
      }

      // Step 2: Send receipt via email and/or SMS
      let emailSent = false
      let smsSent = false
      let sendMessage = ""

      // Try to send both email and SMS if phone is available, otherwise just email
      if (receiptData.customer_phone) {
        const sendBothResponse = await notificationsAPI.sendBoth(
          receiptId,
          receiptData.customer_email,
          receiptData.customer_phone
        )
        
        if (sendBothResponse.ok) {
          emailSent = sendBothResponse.data.results?.email?.sent || false
          smsSent = sendBothResponse.data.results?.sms?.sent || false
          
          if (emailSent && smsSent) {
            sendMessage = `✓ Receipt sent via email and SMS to ${receiptData.customer_email}`
          } else if (emailSent) {
            sendMessage = `✓ Receipt sent via email to ${receiptData.customer_email} (SMS failed: ${sendBothResponse.data.results?.sms?.message || "Unknown error"})`
          } else if (smsSent) {
            sendMessage = `✓ Receipt sent via SMS (Email failed: ${sendBothResponse.data.results?.email?.message || "Unknown error"})`
          } else {
            throw new Error(`Failed to send: ${sendBothResponse.data.results?.email?.message || "Unknown error"}`)
          }
        } else {
          // If send-both fails, try email only
          const emailResponse = await notificationsAPI.sendEmail(receiptId, receiptData.customer_email)
          if (emailResponse.ok && emailResponse.data.success) {
            emailSent = true
            sendMessage = `✓ Receipt sent via email to ${receiptData.customer_email}`
          } else {
            throw new Error(emailResponse.data.error || "Failed to send receipt")
          }
        }
      } else {
        // Only email available
        const emailResponse = await notificationsAPI.sendEmail(receiptId, receiptData.customer_email)
        if (emailResponse.ok && emailResponse.data.success) {
          emailSent = true
          sendMessage = `✓ Receipt sent via email to ${receiptData.customer_email}`
        } else {
          throw new Error(emailResponse.data.error || "Failed to send email")
        }
      }

      // Show success message
      setToastMessage(sendMessage)
      setTimeout(() => setToastMessage(""), 5000)

      // Reload receipts to get updated list
      await loadReceipts()

      // Reset
      setShowPreview(false)
      setFormData(null)
    } catch (error) {
      console.error("Error sending receipt:", error)
      setToastMessage(`✗ Error: ${error.message || "Failed to send receipt"}`)
      setTimeout(() => setToastMessage(""), 5000)
    } finally {
      setIsSending(false)
    }
  }

  // Handle view receipt
  const handleViewReceipt = (receipt) => {
    setFormData(receipt)
    setShowPreview(true)
  }

  // Handle close preview
  const handleClosePreview = () => {
    setShowPreview(false)
    setFormData(null)
  }

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Navbar />

      <main className="flex-1 container mx-auto px-4 py-8 max-w-7xl">
        {!showPreview ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Form Section */}
            <div className="lg:col-span-2">
              <ReceiptForm onSubmit={handleCreateReceipt} />
            </div>

            {/* Receipts List Section */}
            <div className="lg:col-span-1">
              <ReceiptList receipts={receipts} onViewReceipt={handleViewReceipt} />
            </div>
          </div>
        ) : (
          /* Preview Section */
          <ReceiptPreview 
            receipt={formData} 
            onSend={handleSendReceipt} 
            onClose={handleClosePreview}
            isSending={isSending}
          />
        )}
      </main>

      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 bg-success text-white px-6 py-3 rounded-lg shadow-lg animate-pulse">
          {toastMessage}
        </div>
      )}

      <Footer />
    </div>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App
