import { ReceiptCard } from "./ReceiptCard"
import { History, Inbox } from "lucide-react"

export default function ReceiptList({ receipts, onViewReceipt }) {
  return (
    <div className="bg-background rounded-lg shadow-lg p-8 border border-border">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-primary-light p-3 rounded-lg">
          <History size={24} className="text-primary" />
        </div>
        <h2 className="text-2xl font-bold text-foreground">Receipt History</h2>
      </div>

      {receipts.length === 0 ? (
        <div className="text-center py-12">
          <Inbox size={48} className="text-muted-foreground mx-auto mb-4 opacity-50" />
          <p className="text-muted-foreground text-sm">No receipts generated yet</p>
          <p className="text-muted-foreground text-xs mt-1">Create your first e-receipt to see it here</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {receipts.map((receipt, index) => (
            <ReceiptCard 
              key={receipt.id || receipt._id || receipt.receiptNumber || `receipt-${index}`} 
              receipt={receipt} 
              onView={() => onViewReceipt(receipt)} 
            />
          ))}
        </div>
      )}
    </div>
  )
}
