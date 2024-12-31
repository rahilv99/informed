import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ExternalLink } from 'lucide-react'

const citations = [
  {
    title: "Meet Willow, Google's Latest Breakthrough in Quantum Chip",
    source: "Spinquanta",
    url: "https://www.spinquanta.com/newsDetail/92ad47a1-99c1-4e01-a8ee-0074c42d9384"
  },
  {
    title: "Meet Willow, our state-of-the-art quantum chip",
    source: "Google",
    url: "https://blog.google/technology/research/google-willow-quantum-chip/"
  },
  {
    title: "Google claims quantum leap with new Willow chip",
    source: "CIO",
    url: "https://www.cio.com/article/3622570/google-claims-quantum-leap-with-new-willow-chip.html"
  },
  {
    title: "China Property Watch: Charting A Path To Stabilization",
    source: "S&P Global",
    url: "https://www.spglobal.com/ratings/en/research/articles/241018-china-property-watch-charting-a-path-to-stabilization-13280334"
  },
  {
    title: "China Residential Real Estate Market Size & Share Analysis - Growth Trends & Forecasts (2024 - 2029)",
    source: "Modor Intelligence",
    url: "https://www.mordorintelligence.com/industry-reports/residential-real-estate-market-in-china"
  },
  {
    title: "China Real Estate Market Pulse: Q4 2024",
    source: "Morningstar",
    url: "https://www.morningstar.com/en-hk/lp/china-real-estate-market-analysis"
  },
  {
    title: "Ozempic for weight loss: Does it work, and what do experts recommend?",
    source: "UC Davis Health",
    url: "https://health.ucdavis.edu/blog/cultivating-health/ozempic-for-weight-loss-does-it-work-and-what-do-experts-recommend/2023/07"
  },
  {
    title: "How does Ozempic® work? Here is how it makes you feel full",
    source: "Tuli Health",
    url: "https://www.tuli.health/post/how-does-ozempic-work"
  },
  {
    title: "Ozempic for Weight Loss: Who Should Try It and Will It Work?",
    source: "Cleveland Clinic",
    url: "https://health.clevelandclinic.org/ozempic-for-weight-loss"
  }
]

export function Citations() {
  return (
    <Card className="w-full bg-black bg-opacity-10 text-black mt-4 sm:mt-6 border-none">
      <CardHeader className="p-4 sm:p-6">
        <CardTitle className="text-xl sm:text-2xl">Learn More: Citations and Sources</CardTitle>
        <CardDescription className="text-gray-800 text-sm sm:text-base">
          Explore these resources to dive deeper into today's topics.
        </CardDescription>
      </CardHeader>
      <CardContent className="p-4 sm:p-6">
        <ul className="space-y-3 sm:space-y-4">
          {citations.map((citation, index) => (
            <li key={index} className="flex items-start space-x-2">
              <ExternalLink className="w-4 h-4 sm:w-5 sm:h-5 mt-1 flex-shrink-0" />
              <div>
                <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-sm sm:text-base text-gray-700 hover:underline">
                  {citation.title}
                </a>
                <p className="text-xs sm:text-sm text-gray-700">{citation.source}</p>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

