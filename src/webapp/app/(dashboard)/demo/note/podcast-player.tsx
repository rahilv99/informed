import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AudioLines } from 'lucide-react'

export function PodcastPlayer() {
  return (
    <Card className="w-full bg-black bg-opacity-10 text-black mt-6 border-none">
      <CardHeader>
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
            <AudioLines className="w-6 h-6 text-primary-foreground" />
          </div>
          <CardTitle className="text-2xl">Your Daily Insights: AI, Climate, and Space</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <CardDescription className="mb-6 text-lg text-gray-800">
          In this episode, we explore the latest developments in Artificial Intelligence, 
          the ongoing efforts to combat Climate Change, and recent breakthroughs in Space Exploration. 
          We've curated insights based on your notes and interests.
        </CardDescription>
        <div className="p-4 flex items-center space-x-4">
          <audio controls className="w-full">
            <source src="/placeholder.svg?height=50&width=300" type="audio/mp3" />
            Your browser does not support the audio element.
          </audio>
        </div>
      </CardContent>
    </Card>
  )
}

