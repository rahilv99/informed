"use client"

import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { toast } from "@/hooks/use-toast"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

const cancelSubscriptionFormSchema = z.object({
  confirmCancel: z.literal("CANCEL", {
    errorMap: () => ({ message: "Please type CANCEL to confirm" }),
  }),
})

type CancelSubscriptionFormValues = z.infer<typeof cancelSubscriptionFormSchema>

// Mock function to simulate Stripe API call
const cancelStripeSubscription = async (customerId: string) => {
  // In a real implementation, you would use the Stripe SDK here
  console.log(`Cancelling subscription for customer: ${customerId}`)
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  // Simulate successful cancellation
  return { success: true, message: "Subscription successfully cancelled" }
}

export function SubscriptionForm() {
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const form = useForm<CancelSubscriptionFormValues>({
    resolver: zodResolver(cancelSubscriptionFormSchema),
    defaultValues: {
      confirmCancel: "" as "CANCEL",
    },
  })

  async function onSubmit(data: CancelSubscriptionFormValues) {
    try {
      // In a real application, you would get the customer ID from your auth system
      const customerId = "cus_example123"
      const result = await cancelStripeSubscription(customerId)
      
      if (result.success) {
        toast({
          title: "Subscription Cancelled",
          description: "Your subscription has been successfully cancelled.",
        })
        setIsDialogOpen(false)
      } else {
        throw new Error(result.message)
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "There was a problem cancelling your subscription. Please try again later.",
        variant: "destructive",
      })
    }
  }

  return (
    <AlertDialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">Cancel Subscription</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure you want to cancel your subscription?</AlertDialogTitle>
          <AlertDialogDescription>
            This action will immediately cancel your current subscription. You will lose access to premium features at the end of your current billing cycle.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="confirmCancel"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirm Cancellation</FormLabel>
                  <FormControl>
                    <Input placeholder="Type CANCEL to confirm" {...field} />
                  </FormControl>
                  <FormDescription>
                    This action is irreversible. Please type CANCEL to confirm.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <AlertDialogFooter>
              <AlertDialogCancel>Keep Subscription</AlertDialogCancel>
              <AlertDialogAction asChild>
                <Button type="submit" variant="destructive">
                  Cancel Subscription
                </Button>
              </AlertDialogAction>
            </AlertDialogFooter>
          </form>
        </Form>
      </AlertDialogContent>
    </AlertDialog>
  )
}

