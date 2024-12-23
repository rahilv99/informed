import { CalendarDays, Brain, PenIcon as UserPen, Calendar, BarChart2, Settings2 } from 'lucide-react'
import { ActionLink } from '@/components/ui/action-link'
import { Button } from "@/components/ui/button"
import Link from 'next/link'

export function Home() {
  // BACKEND - fetch this data from backend
  const userName = "Rahil"
  const daysUntilNextPodcast = 3
  const upcomingPodcastType = "Journal Club" // This should be fetched from the backend

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-lg w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-5xl">
            Welcome back to Astra
          </h1>
          <p className="mt-3 text-xl text-cyan-200">
            Hello, {userName}!
          </p>
        </div>

        <div className="bg-white bg-opacity-10 rounded-xl p-8 backdrop-filter backdrop-blur-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-cyan-200 rounded-full p-3">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-cyan-200">Next Podcast</p>
                <p className="text-2xl font-bold text-white">{daysUntilNextPodcast} days</p>
              </div>
            </div>
            <CalendarDays className="h-10 w-10 text-cyan-200" />
          </div>
          <div className="mt-6 border-t border-cyan-200 pt-4">
              <p className="text-gray-300 mb-4">You have a <span className="text-white font-bold">{upcomingPodcastType}</span> episode coming up! 
              {upcomingPodcastType === "Updates" && (<p className="text-gray-300"> We're curating the best content tailored to your interests...</p>)}  
              {upcomingPodcastType !== "Updates" && (
                <p className="text-gray-300">We're curating expert opinions on your documents...</p>
              )}
              </p>
              
            <Link href="/dashboard/podcast-settings">
              <Button className="w-full bg-cyan-200 text-gray-900 hover:bg-cyan-300">
                <Settings2 className="mr-2 h-4 w-4" /> Podcast Preferences
              </Button>
            </Link>
          </div>
        </div>

        <div className="flex flex-wrap justify-center gap-4">
          <ActionLink href="/dashboard/edit-day" icon={Calendar}>
            Change Podcast Day
          </ActionLink>
          <ActionLink href="/dashboard/activity" icon={BarChart2}>
            Activity
          </ActionLink>
        </div>
      </div>
    </div>
  )
}

