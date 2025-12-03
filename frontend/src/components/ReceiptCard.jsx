"use client"

import { ChevronRight, CheckCircle, Mail, MessageSquare } from "lucide-react"

export function ReceiptCard({ receipt, onView }) {
  // Handle both camelCase (from form) and snake_case (from API)
  const receiptNumber = receipt.receiptNumber || receipt.receipt_number || 'N/A'
  const customerName = receipt.customerName || receipt.customer_name || 'Unknown Customer'
  const transactionDate = receipt.transactionDate || receipt.transaction_date || 'N/A'
  const total = receipt.total || 0
  const status = receipt.status || 'created'
  const emailSent = receipt.email_sent || false
  const smsSent = receipt.sms_sent || false
  
  // Determine if receipt was sent
  const isSent = status === "Sent" || 
                 status === "email_sent" || 
                 status === "sms_sent" || 
                 status === "both_sent" ||
                 emailSent ||
                 smsSent

  // Get status text and icon
  const getStatusInfo = () => {
    if (status === "both_sent" || (emailSent && smsSent)) {
      return { text: "✓ Sent (Email & SMS)", color: "text-success" }
    } else if (status === "email_sent" || emailSent) {
      return { text: "✓ Email Sent", color: "text-success" }
    } else if (status === "sms_sent" || smsSent) {
      return { text: "✓ SMS Sent", color: "text-success" }
    } else if (status === "Sent") {
      return { text: "✓ Sent", color: "text-success" }
    } else {
      return { text: "⏱ Pending", color: "text-warning" }
    }
  }

  const statusInfo = getStatusInfo()

  return (
    <button
      onClick={onView}
      className="w-full text-left p-4 border border-border rounded-lg hover:border-primary hover:bg-primary-light transition-colors group"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p className="font-semibold text-foreground truncate">{receiptNumber}</p>
            {isSent && <CheckCircle size={16} className="text-success flex-shrink-0" />}
          </div>
          <p className="text-sm text-muted-foreground truncate">{customerName}</p>
          <p className="text-xs text-muted-foreground mt-1">{transactionDate}</p>
          {/* Show email/SMS indicators */}
          <div className="flex items-center gap-2 mt-2">
            {emailSent && (
              <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                <Mail size={12} />
                Email
              </span>
            )}
            {smsSent && (
              <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                <MessageSquare size={12} />
                SMS
              </span>
            )}
          </div>
        </div>

        <div className="text-right flex-shrink-0">
          <p className="font-bold text-primary text-lg">${total.toFixed(2)}</p>
          <p className={`text-xs font-medium mt-1 ${statusInfo.color}`}>
            {statusInfo.text}
          </p>
          <ChevronRight
            size={18}
            className="text-muted-foreground mt-2 group-hover:text-primary transition-colors ml-auto"
          />
        </div>
      </div>
    </button>
  )
}

export default ReceiptCard
