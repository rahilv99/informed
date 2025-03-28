import type React from "react"
import "./globals.css"
import type { Metadata, Viewport } from "next"
import { Manrope } from "next/font/google"
import { UserProvider } from "@/lib/auth"
import { getUser } from "@/lib/db/queries"
import ClientLayout from "./ClientLayout"

export const metadata: Metadata = {
  title: "Auxiom",
  description: "Your Personalized AI Journalist.",
}

export const viewport: Viewport = {
  maximumScale: 1,
  themeColor: "#000000", // Added for media controls theming
}

const manrope = Manrope({ subsets: ["latin"] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const userPromise = getUser()

  return (
    <html lang="en" className={`bg-black dark:bg-gray-950 text-black dark:text-black ${manrope.className}`}>
      <body className="min-h-[100dvh] bg-gray-50">
        <UserProvider userPromise={userPromise}>
          <ClientLayout>{children}</ClientLayout>
        </UserProvider>
      </body>
    </html>
  )
}

