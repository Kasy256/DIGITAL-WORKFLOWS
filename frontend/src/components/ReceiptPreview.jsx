"use client"

import { Send, X, Printer, Leaf } from "lucide-react"

export default function ReceiptPreview({ receipt, onSend, onClose, isSending = false }) {
  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold text-foreground">Receipt Preview</h2>
        <button
          onClick={onClose}
          className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
        >
          <X size={24} />
        </button>
      </div>

      {/* Receipt Card */}
      <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8 border border-border print:shadow-none">
        {/* Receipt Header */}
        <div className="flex items-start justify-between mb-8 border-b-2 border-primary pb-6">
          <div className="flex items-center gap-3">
            <div className="bg-primary-light p-4 rounded-xl">
              <Leaf size={32} className="text-primary" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-foreground">EReceipt</h3>
              <p className="text-xs text-muted-foreground">Digital Receipt</p>
            </div>
          </div>

          <div className="text-right">
            <p className="text-3xl font-bold text-primary">{receipt.receiptNumber || receipt.receipt_number}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {(() => {
                let date;
                if (receipt.timestamp) {
                  date = receipt.timestamp instanceof Date ? receipt.timestamp : new Date(receipt.timestamp);
                } else if (receipt.created_at) {
                  date = receipt.created_at instanceof Date ? receipt.created_at : new Date(receipt.created_at);
                } else {
                  date = new Date();
                }
                return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
              })()}
            </p>
          </div>
        </div>

        {/* Customer Info */}
        <div className="grid grid-cols-2 gap-6 mb-8 pb-6 border-b border-border">
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Customer</p>
            <p className="text-lg font-semibold text-foreground mt-1">{receipt.customerName || receipt.customer_name}</p>
            <p className="text-sm text-muted-foreground">{receipt.customerEmail || receipt.customer_email}</p>
          </div>

          <div className="text-right">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Date</p>
            <p className="text-lg font-semibold text-foreground mt-1">{receipt.transactionDate || receipt.transaction_date}</p>
          </div>
        </div>

        {/* Items Table */}
        <div className="mb-8">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-primary">
                <th className="text-left py-3 text-xs font-semibold text-muted-foreground uppercase">Description</th>
                <th className="text-center py-3 text-xs font-semibold text-muted-foreground uppercase">Qty</th>
                <th className="text-right py-3 text-xs font-semibold text-muted-foreground uppercase">Price</th>
                <th className="text-right py-3 text-xs font-semibold text-muted-foreground uppercase">Amount</th>
              </tr>
            </thead>
            <tbody>
              {(receipt.items || []).map((item, index) => (
                <tr key={index} className="border-b border-border">
                  <td className="py-4 text-foreground font-medium">{item.name || ''}</td>
                  <td className="py-4 text-center text-foreground">{item.quantity || 0}</td>
                  <td className="py-4 text-right text-foreground">${(item.price || 0).toFixed(2)}</td>
                  <td className="py-4 text-right font-semibold text-foreground">
                    ${((item.quantity || 0) * (item.price || 0)).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Summary Section */}
        <div className="flex justify-end mb-8">
          <div className="w-64">
            <div className="flex justify-between py-2 text-foreground">
              <span>Subtotal:</span>
              <span>${(receipt.subtotal || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between py-2 text-foreground border-b border-border mb-2 pb-3">
              <span>Tax ({receipt.taxRate || receipt.tax_rate || 0}%):</span>
              <span>${(receipt.tax || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between py-3 text-lg font-bold text-primary bg-primary-light px-4 rounded-lg">
              <span>Total:</span>
              <span>${(receipt.total || 0).toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Footer Message */}
        <div className="text-center pt-6 border-t border-border">
          <p className="text-xs text-muted-foreground">
            Thank you for your purchase! This is a digital receipt. No physical copy will be provided.
          </p>
          <p className="text-xs text-success font-semibold mt-2">♻ Paperless Transaction</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 print:hidden">
        <button
          onClick={handlePrint}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 border-2 border-border text-foreground rounded-lg hover:bg-muted transition-colors"
        >
          <Printer size={20} />
          Print
        </button>

        <button
          onClick={onClose}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 border-2 border-border text-foreground rounded-lg hover:bg-muted transition-colors"
        >
          <X size={20} />
          Close
        </button>

        <button
          onClick={onSend}
          disabled={isSending}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSending ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              Sending...
            </>
          ) : (
            <>
              <Send size={20} />
              Send Receipt
            </>
          )}
        </button>
      </div>

      {/* Status Badge */}
      <div className="mt-6 text-center">
        <span
          className={`inline-block px-4 py-2 rounded-lg font-semibold text-sm ${
            receipt.status === "Sent" || receipt.status === "both_sent" || receipt.status === "email_sent" || receipt.status === "sms_sent" 
              ? "bg-success/10 text-success" 
              : "bg-warning/10 text-warning"
          }`}
        >
          Status: {receipt.status || "Not Sent"}
        </span>
      </div>
    </div>
  )
}
