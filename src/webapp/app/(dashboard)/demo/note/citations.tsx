import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ExternalLink } from 'lucide-react'

const citations = [
  {
    title: "The Future of AI: Trends and Innovations",
    source: "MIT Technology Review",
    url: "https://www.technologyreview.com/ai"
  },
  {
    title: "Climate Change: Global Temperature",
    source: "NASA",
    url: "https://climate.nasa.gov/vital-signs/global-temperature/"
  },
  {
    title: "SpaceX Starship: The Revolutionary Spacecraft",
    source: "Space.com",
    url: "https://www.space.com/spacex-starship.html"
  }
]

export function Citations() {
  return (
    <Card className="w-full bg-black bg-opacity-10 text-black mt-6 border-none">
      <CardHeader>
        <CardTitle className="text-2xl">Learn More: Citations and Sources</CardTitle>
        <CardDescription className="text-gray-800">
          Explore these resources to dive deeper into today's topics.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="space-y-4">
          {citations.map((citation, index) => (
            <li key={index} className="flex items-start space-x-2">
              <ExternalLink className="w-5 h-5 mt-1 flex-shrink-0" />
              <div>
                <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-gray-700 hover:underline">
                  {citation.title}
                </a>
                <p className="text-sm text-gray-700">{citation.source}</p>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

