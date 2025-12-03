export default function Footer() {
  return (
    <footer className="bg-muted border-t border-border mt-12">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <h4 className="font-semibold text-foreground mb-3">About EReceipt</h4>
            <p className="text-sm text-muted-foreground">
              Digital receipt generation system for eco-conscious businesses. Reduce paper waste, increase efficiency.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-foreground mb-3">Features</h4>
            <ul className="text-sm text-muted-foreground space-y-2">
              <li>• Digital Receipt Generation</li>
              <li>• Email Delivery (Mock)</li>
              <li>• Receipt History</li>
              <li>• Eco-Friendly Design</li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-foreground mb-3">Integration Notes</h4>
            <p className="text-xs text-muted-foreground">
              Future integrations: Firebase for backend storage, SendGrid/AWS SES for email delivery, Stripe for
              payments.
            </p>
          </div>
        </div>

        <div className="border-t border-border pt-4 text-center text-sm text-muted-foreground">
          <p>© 2025 EReceipt System. Demo version with mock data.</p>
        </div>
      </div>
    </footer>
  )
}
