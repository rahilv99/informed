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
import { deleteAccount } from '@/lib/actions'
import { useRouter } from 'next/navigation'

const deleteAccountFormSchema = z.object({
  confirmDelete: z.literal("DELETE", {
    errorMap: () => ({ message: "Please type DELETE to confirm" }),
  }),
})

type DeleteAccountFormValues = z.infer<typeof deleteAccountFormSchema>

export function DeleteAccountForm() {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const router = useRouter()

  const form = useForm<DeleteAccountFormValues>({
    resolver: zodResolver(deleteAccountFormSchema),
    defaultValues: {
      confirmDelete: "" as "DELETE",
    },
  })

  async function onSubmit(data: DeleteAccountFormValues) {
    try {
      await deleteAccount()
      toast({
        title: "Account Deleted",
        description: "Your account has been permanently deleted.",
      })
      setIsDialogOpen(false)
      router.push('/')
    } catch (error) {
      toast({
        title: "Error",
        description: "There was a problem deleting your account.",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="space-y-6">
      <AlertDialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <AlertDialogTrigger asChild>
          <Button variant="destructive" className="w-full">Delete Account</Button>
        </AlertDialogTrigger>
        <AlertDialogContent className="bg-gray-800 text-white">
          <AlertDialogHeader>
            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
            <AlertDialogDescription className="text-gray-200">
              This action cannot be undone. This will permanently delete your account and remove your data from our servers.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="confirmDelete"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Confirm Deletion</FormLabel>
                    <FormControl>
                      <Input placeholder="Type DELETE to confirm" {...field} className="bg-gray-800 text-white" />
                    </FormControl>
                    <FormDescription className="text-gray-200">
                      This action is irreversible. Please type DELETE to confirm.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <AlertDialogFooter>
                <AlertDialogCancel className="bg-gray-800 text-white">Cancel</AlertDialogCancel>
                <AlertDialogAction asChild>
                  <Button type="submit" variant="destructive">
                    Delete Account
                  </Button>
                </AlertDialogAction>
              </AlertDialogFooter>
            </form>
          </Form>
        </AlertDialogContent>
      </AlertDialog>
      <Button variant="outline" className="w-full bg-gray-800" onClick={() => router.push('/')}>Cancel</Button>
    </div>
  )
}
