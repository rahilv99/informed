"use client"

import * as z from "zod"

import { Button } from "@/components/ui/button"
import { customerPortalAction } from "@/lib/payments/actions"

const cancelSubscriptionFormSchema = z.object({
  confirmCancel: z.literal("CANCEL", {
    errorMap: () => ({ message: "Please type CANCEL to confirm" }),
  }),
})

export function SubscriptionForm() {
  return (
          <form action={customerPortalAction} className="space-y-4">
            <Button type="submit" variant="destructive">
              Cancel Subscription
            </Button>
          </form>
  )
}

