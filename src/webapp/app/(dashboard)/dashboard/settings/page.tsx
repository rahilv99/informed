import { Metadata } from "next"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { AccountForm } from "./account-form"
import { SubscriptionForm } from "./subscription-form"
import { PasswordForm } from "./password-form"
import { DeleteAccountForm } from "./delete-account-form"
import { getUser } from "@/lib/db/queries"
import { getAccountStatus, getKeywords } from "@/lib/actions";
import { redirect } from "next/navigation";

export const metadata: Metadata = {
  title: "Settings",
  description: "Manage your account settings and preferences.",
}

export default async function SettingsPage() {

  const isActive: boolean = await getAccountStatus();
  const user = await getUser();
  const currentKeywords: string[] = await getKeywords();

  if (!isActive && currentKeywords.length === 0) {
        redirect('/identity');
      } 
  
      if (!isActive) {
        redirect('/day');
      }
  
  const email = user?.email || "email"

  return (
    <div className="space-y-6 p-10 pb-16">
      <div className="space-y-0.5">
        <h2 className="text-2xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground">
          Manage your account settings and preferences.
        </p>
      </div>
      <Separator className="my-6" />
      <div className="grid gap-6 md:grid-cols-2">
        <Card className="bg-black bg-opacity-10 border-none">
          <CardHeader>
            <CardTitle>Account</CardTitle>
            <CardDescription>Update your account information.</CardDescription>
          </CardHeader>
          <CardContent>
            <AccountForm email={email} />
          </CardContent>
        </Card>
        <Card className="bg-black bg-opacity-10 border-none">
          <CardHeader>
            <CardTitle>Subscription</CardTitle>
            <CardDescription>Manage your subscription plan.</CardDescription>
          </CardHeader> 
          <CardContent>
            <SubscriptionForm />
          </CardContent>
        </Card>
        <Card className="bg-black bg-opacity-10 border-none">
          <CardHeader>
            <CardTitle>Password</CardTitle>
            <CardDescription>Update your password.</CardDescription>
          </CardHeader>
          <CardContent>
            <PasswordForm />
          </CardContent>
        </Card>
        <Card className="bg-black bg-opacity-10 border-none">
          <CardHeader>
            <CardTitle>Delete Account</CardTitle>
            <CardDescription>Permanently delete your account.</CardDescription>
          </CardHeader>
          <CardContent>
            <DeleteAccountForm />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

