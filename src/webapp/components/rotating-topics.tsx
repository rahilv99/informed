"use client"

import { useState, useEffect } from "react"

const politicalTopics = [
  "The latest news on Ukraine",
  "How tariffs are affecting the U.S. economy",
  "Breaking down the latest election polls",
  "Climate policy updates from around the world",
  "Understanding the Supreme Court's recent decisions",
]

export default function RotatingTopics() {
  const [currentTopicIndex, setCurrentTopicIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTopicIndex((prevIndex) => (prevIndex + 1) % politicalTopics.length)
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <section className="py-8 bg-transparent">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-700 mb-6">
            Today's Podcast is about...
          </h2>

          <div className="relative h-16 overflow-hidden">
            {politicalTopics.map((topic, index) => (
              <div
                key={index}
                className={`absolute w-full transition-all duration-500 ease-in-out ${
                  index === currentTopicIndex ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
                }`}
              >
                <p className="text-xl md:text-2xl font-medium text-gray-700">"{topic}"</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
