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
import {  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { deleteAccount, signOut } from '@/lib/actions';


const deleteAccountFormSchema = z.object({
  confirmDelete: z.literal("DELETE", {
    errorMap: () => ({ message: "Please type DELETE to confirm" }),
  }),
})

type DeleteAccountFormValues = z.infer<typeof deleteAccountFormSchema>

export function DeleteAccountForm() {

  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const form = useForm<DeleteAccountFormValues>({
    resolver: zodResolver(deleteAccountFormSchema),
    defaultValues: {
      confirmDelete: "DELETE",
    },
  })

  async function onSubmit(data: DeleteAccountFormValues) {
    try {
      await deleteAccount()
      setIsDialogOpen(false)
      await signOut()
    } catch (error) {
      console.error(error)
    }
  }

  async function handleSignOut() {
    try {
      await signOut()
    } catch (error) {
      console.error(error)
    }
  }

  return (
    <div className="space-y-6 flex flex-col">
    <AlertDialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">Delete Account</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
          <AlertDialogDescription>
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
                    <Input 
                      placeholder="Type DELETE to confirm" 
                      value={field.value} // Explicitly set value
                      onChange={field.onChange}
                    />
                  </FormControl>
                  <FormDescription>
                    This action is irreversible. Please type DELETE to confirm.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
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
    <Button onClick={handleSignOut}>Sign Out</Button>
    </div>
  )
}

