"use client";

import { Sidebar } from "@/components/sidebar"
import { MobileHeader } from "@/components/mobile-header"
import { useMediaQuery } from "@/hooks/use-media-query"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const isMobile = useMediaQuery("(max-width: 768px)")

  return (
    <div className="flex flex-col md:flex-row min-h-screen">
      {isMobile ? <MobileHeader /> : <Sidebar />}
      <main className="flex-1 p-4 md:p-8">{children}</main>
    </div>
  )
}
