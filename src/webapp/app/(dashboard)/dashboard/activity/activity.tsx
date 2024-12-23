import { AudioLines } from 'lucide-react'
import  Link  from 'next/link'

// BACKEND - Retrieve from database
const podcastHistory = [
  {
    id: 1,
    title: "The Future of AI",
    date: "2023-05-15",
    summary: "Exploring the latest advancements in artificial intelligence and their potential impact on society.",
    link: "https://www.example.com/podcast-1"
  },
  {
    id: 2,
    title: "Sustainable Energy Solutions",
    date: "2023-05-22",
    summary: "Discussing innovative approaches to renewable energy and their role in combating climate change.",
    link: "https://www.example.com/podcast-1"
  },
  {
    id: 3,
    title: "The Art of Mindfulness",
    date: "2023-05-29",
    summary: "Delving into mindfulness practices and their benefits for mental health and overall well-being.",
    link: "https://www.example.com/podcast-1"
  },
]

export function Activity() {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-semibold text-white mb-8">Your Podcast History</h1>
      <div className="space-y-6 pb-20">
        {podcastHistory.map((podcast) => (
          <div 
            key={podcast.id} 
            className="bg-white bg-opacity-10 backdrop-blur-sm rounded-lg overflow-hidden transition-all duration-300 ease-in-out hover:bg-opacity-20 hover:shadow-lg"
          >
            <div className="p-6">
              <div className='flex justify-between items-center'>
                <h2 className="text-xl font-semibold text-white mb-2">{podcast.title}</h2>
                <Link href={podcast.link}>
                  <AudioLines className="h-10 w-10 text-cyan-200 hover:text-cyan-800" />
                </Link>
              </div>
              <p className="text-sm text-cyan-200 mb-3">{podcast.date}</p>
              <p className="text-gray-300">{podcast.summary}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

