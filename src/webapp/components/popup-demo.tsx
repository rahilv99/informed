"use client"

import { useState, useEffect, useRef } from "react"
import { X, Play, Pause, Volume2, VolumeX, MessageCircle, ChevronLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { cn } from "@/lib/utils"

export default function PopupWidget() {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isMuted, setIsMuted] = useState(false)
  const [audioProgress, setAudioProgress] = useState(0)
  const audioUrl = "https://905418457861-astra-bucket.s3.us-east-1.amazonaws.com/user/27/13/podcast.mp3"
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Initialize audio element
  useEffect(() => {
    if (!audioUrl) return

    const audio = new Audio(audioUrl)
    audioRef.current = audio

    // Set up event listeners
    audio.addEventListener("loadedmetadata", () => {
      setDuration(audio.duration)
    })

    audio.addEventListener("timeupdate", () => {
      setCurrentTime(audio.currentTime)
      setAudioProgress((audio.currentTime / audio.duration) * 100)
    })

    audio.addEventListener("ended", () => {
      setIsPlaying(false)
      setCurrentTime(0)
      setAudioProgress(0)
    })

    return () => {
      audio.pause()
      audio.src = ""

      // Clean up event listeners
      audio.removeEventListener("loadedmetadata", () => {})
      audio.removeEventListener("timeupdate", () => {})
      audio.removeEventListener("ended", () => {})
    }
  }, [audioUrl])

  // Handle play/pause state changes
  useEffect(() => {
    if (!audioRef.current) return

    if (isPlaying) {
      audioRef.current.play().catch((error) => {
        console.error("Error playing audio:", error)
        setIsPlaying(false)
      })
    } else {
      audioRef.current.pause()
    }
  }, [isPlaying])

  // Handle mute state changes
  useEffect(() => {
    if (!audioRef.current) return
    audioRef.current.muted = isMuted
  }, [isMuted])

  // Format time for audio player
  const formatTime = (seconds: number) => {
    if (isNaN(seconds)) return "0:00"
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`
  }

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
  }

  const handleVolumeToggle = () => {
    setIsMuted(!isMuted)
  }

  const handleProgressChange = (value: number[]) => {
    setAudioProgress(value[0])
    setCurrentTime((value[0] / 100) * duration)
    if (!audioRef.current) return

    const newProgress = value[0]
    setAudioProgress(newProgress)

    const newTime = (newProgress / 100) * (audioRef.current.duration || 0)
    audioRef.current.currentTime = newTime
    setCurrentTime(newTime)
  }

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded)

    // Pause audio when collapsing
    if (isExpanded && isPlaying) {
      setIsPlaying(false)
    }
  }

  return (
    <>
      {/* Corner Icon */}
      {!isExpanded && (
        <Button
          onClick={toggleExpanded}
          className="fixed bottom-4 right-4 h-12 w-12 rounded-full shadow-lg"
          size="icon"
        >
          <MessageCircle className="h-6 w-6" />
        </Button>
      )}

      {/* Expanded Widget */}
      {isExpanded && (
    <Card className="fixed bottom-4 right-4 w-80 shadow-lg rounded-lg overflow-hidden z-50 border border-gray-700 bg-black/50 text-gray-200">
      <div className="bg-gray-800 text-gray-100 p-3 flex justify-between items-center">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleExpanded}
              className="h-8 w-8 mr-2 text-primary-foreground"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <h3 className="font-medium flex-1">Your AI Journalist</h3>
            <Button variant="ghost" size="icon" onClick={toggleExpanded} className="h-8 w-8 text-primary-foreground">
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="p-4 bg-gray-900">
          <div className="animate-fadeIn">
            <div className="flex items-start gap-2 mb-4">
              <div className="bg-gray-700 w-8 h-8 rounded-full flex items-center justify-center">
                <span className="text-xs text-gray-300">AI</span>
              </div>
              <div className="bg-gray-800 p-3 rounded-lg text-sm text-gray-300">
                Hello! I'm your personal AI Journalist.
              </div>
            </div>
          </div>

            <div className="flex items-start gap-2 mb-4">
              <div className="bg-gray-700 w-8 h-8 rounded-full flex items-center justify-center">
                <span className="text-xs text-gray-300">AI</span>
              </div>
              <div className="bg-gray-800 p-3 rounded-lg text-sm text-gray-300">
                What current events are you interested in tracking?
              </div>
            </div>

            <div className="flex items-start gap-2 mb-4">
              <div className="bg-gray-800 p-3 rounded-lg text-sm text-gray-300">
                I'm interested in the Ukraine war, foreign affairs, and immigration, and tariffs.
              </div>
              <div className="bg-gray-700 w-8 h-8 rounded-full flex items-center justify-center">
                <span className="text-xs text-gray-300">User</span>
              </div>
            </div>

            <div className="flex items-start gap-2 mb-4">
              <div className="bg-gray-700 w-8 h-8 rounded-full flex items-center justify-center">
                <span className="text-xs text-gray-300">AI</span>
              </div>
              <div className="bg-gray-800 p-3 rounded-lg text-sm text-gray-300">
                Great! Here's the big news from the last week. Sign up for your own personalized journalist!
              </div>
            </div>

          <div className="animate-fadeIn">
            <div className="bg-gray-800/60 p-3 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handlePlayPause}
                  className="h-8 w-8 text-gray-200 hover:text-gray-100"
                >
                  {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                </Button>
                <div className="text-xs text-gray-400">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleVolumeToggle}
                  className="h-8 w-8 ml-auto text-gray-200 hover:text-gray-100"
                >
                  {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                </Button>
              </div>

              <Slider
                value={[audioProgress]}
                min={0}
                max={100}
                step={1}
                onValueChange={handleProgressChange}
                className="w-full bg-gray-700"
              />

              <div className="text-xs text-center mt-2 text-gray-400">Weekly Briefing</div>
            </div>
          </div>
      </div>
    </Card>
      )}
    </>
  )
}
