import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ActionLink } from './ui/action-link'

interface ComingSoonWrapperProps {
  demo: string
  children: React.ReactNode
}

export function ComingSoonWrapper({ demo, children }: ComingSoonWrapperProps) {
  return (
    <div className="relative">
      <div className="filter blur-sm pointer-events-none">
        {children}
      </div>
      <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-xl">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-center">Coming Soon!</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-center mb-4">
              We're excited to bring you this feature. Stay tuned for updates!
            </p>
            <div className="flex justify-center">
              <ActionLink href = {demo}>Demo</ActionLink>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

