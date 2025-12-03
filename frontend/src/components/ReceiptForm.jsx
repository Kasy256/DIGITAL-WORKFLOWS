"use client"

import { useState } from "react"
import { Plus, Trash2, FileText } from "lucide-react"

export default function ReceiptForm({ onSubmit }) {
  const [customerName, setCustomerName] = useState("")
  const [customerEmail, setCustomerEmail] = useState("")
  const [transactionDate, setTransactionDate] = useState("")
  const [items, setItems] = useState([{ id: 1, name: "", quantity: 1, price: 0 }])
  const [taxRate, setTaxRate] = useState(10)
  const [nextId, setNextId] = useState(2)

  // Calculate totals
  const subtotal = items.reduce((sum, item) => sum + item.quantity * item.price, 0)
  const tax = (subtotal * taxRate) / 100
  const total = subtotal + tax

  // Add item
  const handleAddItem = () => {
    setItems([...items, { id: nextId, name: "", quantity: 1, price: 0 }])
    setNextId(nextId + 1)
  }

  // Remove item
  const handleRemoveItem = (id) => {
    if (items.length > 1) {
      setItems(items.filter((item) => item.id !== id))
    }
  }

  // Update item
  const handleUpdateItem = (id, field, value) => {
    setItems(items.map((item) => (item.id === id ? { ...item, [field]: value } : item)))
  }

  // Handle submit
  const handleSubmit = (e) => {
    e.preventDefault()

    if (!customerName || !customerEmail || !transactionDate) {
      alert("Please fill in all customer details")
      return
    }

    if (items.some((item) => !item.name || item.price <= 0)) {
      alert("Please fill in all item details")
      return
    }

    onSubmit({
      customerName,
      customerEmail,
      transactionDate,
      items,
      subtotal,
      tax,
      total,
      taxRate,
    })

    // Reset form
    setCustomerName("")
    setCustomerEmail("")
    setTransactionDate("")
    setItems([{ id: 1, name: "", quantity: 1, price: 0 }])
    setNextId(2)
  }

  return (
    <form onSubmit={handleSubmit} className="bg-background rounded-lg shadow-lg p-8 border border-border">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-primary-light p-3 rounded-lg">
          <FileText size={24} className="text-primary" />
        </div>
        <h2 className="text-3xl font-bold text-foreground">Create E-Receipt</h2>
      </div>

      {/* Customer Details */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-foreground mb-4">Customer Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Customer Name *</label>
            <input
              type="text"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="John Doe"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Customer Email *</label>
            <input
              type="email"
              value={customerEmail}
              onChange={(e) => setCustomerEmail(e.target.value)}
              className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="john@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Transaction Date *</label>
            <input
              type="date"
              value={transactionDate}
              onChange={(e) => setTransactionDate(e.target.value)}
              className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Tax Rate (%) *</label>
            <input
              type="number"
              value={taxRate}
              onChange={(e) => setTaxRate(Number(e.target.value))}
              className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              step="0.1"
              min="0"
              max="100"
            />
          </div>
        </div>
      </div>

      {/* Items Section */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-foreground mb-4">Receipt Items</h3>
        <div className="space-y-3">
          {items.map((item, index) => (
            <div key={item.id} className="flex gap-3 items-end">
              <div className="flex-1">
                <label className="block text-xs font-medium text-muted-foreground mb-1">Item Name</label>
                <input
                  type="text"
                  value={item.name}
                  onChange={(e) => handleUpdateItem(item.id, "name", e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Product or Service"
                  required
                />
              </div>

              <div className="w-20">
                <label className="block text-xs font-medium text-muted-foreground mb-1">Qty</label>
                <input
                  type="number"
                  value={item.quantity}
                  onChange={(e) => handleUpdateItem(item.id, "quantity", Number(e.target.value))}
                  className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  min="1"
                  required
                />
              </div>

              <div className="w-24">
                <label className="block text-xs font-medium text-muted-foreground mb-1">Price</label>
                <input
                  type="number"
                  value={item.price}
                  onChange={(e) => handleUpdateItem(item.id, "price", Number(e.target.value))}
                  className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  required
                />
              </div>

              <div className="w-20 text-right">
                <label className="block text-xs font-medium text-muted-foreground mb-1">Total</label>
                <p className="font-semibold text-foreground">${(item.quantity * item.price).toFixed(2)}</p>
              </div>

              <button
                type="button"
                onClick={() => handleRemoveItem(item.id)}
                disabled={items.length === 1}
                className="p-2 text-error hover:bg-error/10 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Trash2 size={20} />
              </button>
            </div>
          ))}
        </div>

        <button
          type="button"
          onClick={handleAddItem}
          className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 border-2 border-dashed border-primary text-primary rounded-lg hover:bg-primary-light transition-colors"
        >
          <Plus size={20} />
          Add Item
        </button>
      </div>

      {/* Summary */}
      <div className="bg-muted p-6 rounded-lg mb-8">
        <div className="space-y-2 mb-4 border-b border-border pb-4">
          <div className="flex justify-between text-foreground">
            <span>Subtotal:</span>
            <span className="font-semibold">${subtotal.toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-foreground">
            <span>Tax ({taxRate}%):</span>
            <span className="font-semibold">${tax.toFixed(2)}</span>
          </div>
        </div>
        <div className="flex justify-between text-lg font-bold text-primary">
          <span>Total:</span>
          <span>${total.toFixed(2)}</span>
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        className="w-full bg-primary hover:bg-primary-dark text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <FileText size={20} />
        Generate Receipt
      </button>
    </form>
  )
}
