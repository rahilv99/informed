import { Metadata } from "next"
import { DeleteAccountForm } from "./delete-account-form"
import { getUser } from "@/lib/db/queries"
import { redirect } from "next/navigation"


export const metadata: Metadata = {
    title: "Delete Account",
    description: "Permanently delete your account.",
}

export default function DeleteAccountPage() {
    const user = getUser();
    if (!user) {
        redirect("/sign-in?redirect=/deactivate-account");
    }
    return (
        <div className="flex flex-col items-center justify-center min-h-screen text-white p-4">
            <div className="w-full max-w-md space-y-8 bg-black bg-opacity-10 p-6 rounded-lg">
                <div className="text-center">
                    <h2 className="mt-6 text-3xl font-extrabold text-black">Delete Your Account</h2>
                    <p className="mt-2 text-sm text-gray-800">
                        We're sorry to see you go. Please confirm your account deletion below.
                    </p>
                </div>
                <DeleteAccountForm />
            </div>
        </div>
    )
}
