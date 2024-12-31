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
    <div className="flex h-screen flex-col md:flex-row">
      {isMobile ? <MobileHeader /> : <Sidebar />}
      <main className="flex-1 overflow-y-auto p-4 md:p-8">{children}</main>
    </div>
  )
}
