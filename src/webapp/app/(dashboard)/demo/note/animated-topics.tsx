'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const topics = [
  'Latest updates on the Google Willow Chip',
  'What are the latest trends on the Chinese real estate market?',
  'What makes ozempic so effective?'
]

export function AnimatedTopics() {
  const [currentTopic, setCurrentTopic] = useState(0)
  const [displayedText, setDisplayedText] = useState("")

  useEffect(() => {
    let interval: NodeJS.Timeout
    let charIndex = 0

    const animateText = () => {
      if (charIndex <= topics[currentTopic].length) {
        setDisplayedText(topics[currentTopic].slice(0, charIndex))
        charIndex++
      } else {
        clearInterval(interval)
        setTimeout(() => {
          setCurrentTopic((prev) => (prev + 1) % topics.length)
        }, 1000)
      }
    }

    interval = setInterval(animateText, 100)

    return () => clearInterval(interval)
  }, [currentTopic])

  return (
    <div className="h-10 flex items-center justify-center">
      <AnimatePresence mode="wait">
        <motion.div
          key={currentTopic}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.5 }}
          className="text-lg text-black"
        >
          {displayedText}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

