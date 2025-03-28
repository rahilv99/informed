"use client"

import type React from "react"

import { useEffect } from "react"
import { registerServiceWorker } from "./register-sw"

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode
}) {
  useEffect(() => {
    registerServiceWorker()
  }, [])

  return <>{children}</>
}

