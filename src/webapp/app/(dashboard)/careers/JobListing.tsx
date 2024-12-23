'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface JobListingProps {
  title: string
  qualifications: string[]
}

export function JobListing({ title, qualifications }: JobListingProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="bg-cyan-300 bg-opacity-10 rounded-lg p-6 space-y-4 cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-white">{title}</h2>
          {isExpanded ? (
            <ChevronUp className="h-6 w-6 text-white" />
          ) : (
            <ChevronDown className="h-6 w-6 text-white" />
          )}
          <span className="sr-only">{isExpanded ? 'Hide' : 'Show'} qualifications</span>
      </div>
      {isExpanded && (
        <div className="mt-4 space-y-2 bg-cyan-100 bg-opacity-5 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-white font-semibold">Qualifications:</h3>
          <ul className="list-disc list-inside text-white space-y-1">
            {qualifications.map((qual, index) => (
              <li key={index}>{qual}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

