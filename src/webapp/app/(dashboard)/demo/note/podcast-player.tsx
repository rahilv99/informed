import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AudioLines } from 'lucide-react'

export function PodcastPlayer() {
  return (
    <Card className="w-full bg-black bg-opacity-10 text-black mt-4 sm:mt-6 border-none">
      <CardHeader className="p-4 sm:p-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 sm:w-12 sm:h-12 bg-primary rounded-full flex items-center justify-center">
            <AudioLines className="w-5 h-5 sm:w-6 sm:h-6 text-primary-foreground" />
          </div>
          <CardTitle className="text-xl sm:text-2xl">Your Daily Insights: Quantum Chips, Chinese Real Estate, and Ozempic</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="p-4 sm:p-6">
        <CardDescription className="mb-4 sm:mb-6 text-base sm:text-lg text-gray-800">
          Get expert insight and up to date information on the latest news and trends in any industry. 
          See how Auxiom Note can turn your notes into a daily briefing that keeps you ahead of the curve. 
        </CardDescription>
        <div className="p-2 sm:p-4 flex items-center">
          <audio controls className="w-full">
            <source src="/note-demo.mp3" type="audio/mp3" />
            Your browser does not support the audio element.
          </audio>
        </div>
      </CardContent>
    </Card>
  )
}

