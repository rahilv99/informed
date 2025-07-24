"use client"

import { Input } from "@/components/ui/input"

export function AccountForm({ email }: { email: string }) {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          Email
        </label>
        <Input value={email} disabled className="mt-1" />
        <p className="text-sm text-muted-foreground mt-1">
          This is the email your Auxiom podcasts are sent to.
        </p>
      </div>
    </div>
  )
}
