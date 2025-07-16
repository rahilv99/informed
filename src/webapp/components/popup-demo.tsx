"use client"

import { useState, useEffect, useRef } from "react"
import { X, Play, Pause, Volume2, VolumeX, ChevronUp, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { cn } from "@/lib/utils"
import { Select, SelectTrigger, SelectContent, SelectItem } from "@/components/ui/select"

interface PopupWidgetProps {
  isExpanded?: boolean
  onToggle?: () => void
}

export default function PopupWidget({ isExpanded = false, onToggle }: PopupWidgetProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isMuted, setIsMuted] = useState(false)
  const [audioProgress, setAudioProgress] = useState(0)
  const [playbackSpeed, setPlaybackSpeed] = useState(1)
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

  // Handle playback speed changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = playbackSpeed
    }
  }, [playbackSpeed])

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
    if (onToggle) {
      onToggle()
    }

    // Pause audio when collapsing
    if (isExpanded && isPlaying) {
      setIsPlaying(false)
    }
  }

  return (
    <div
      className={cn(
        "fixed right-0 flex flex-col items-end z-50 transition-all duration-300 ease-in-out overflow-hidden",
        isExpanded ? "bottom-0" : "bottom-[-550px]", // Ensure it's completely hidden
      )}
    >
      {/* Stylized Tab */}
      <div
        onClick={toggleExpanded}
        className={cn(
          "flex items-center justify-center px-6 py-3 cursor-pointer",
          "bg-gray-800 ",
          "rounded-t-xl shadow-lg border border-primary/20 border-b-0",
          "transition-all duration-300",
          "w-36 text-center relative z-10",
          isExpanded ? "mb-0" : "mb-0 hover:mb-1",
        )}
      >
        <div className="flex items-center justify-center gap-2 font-medium text-primary-foreground">
          {isExpanded ? <ChevronDown className="h-5 w-5" /> : <ChevronUp className="h-5 w-5" />}
          <span>Demo</span>
        </div>
      </div>

      {/* Widget Content */}
      <Card className="w-80 shadow-lg rounded-tl-lg overflow-hidden border border-gray-700 bg-black/50 text-gray-200 rounded-tr-none">

        <div className="p-4 bg-gray-900">
          <div className="animate-fadeIn">
            <div className="flex items-start gap-2 mb-4">
              <div className="bg-gray-700 w-8 aspect-square rounded-full flex items-center justify-center">
                <span className="text-xs text-gray-300">AI</span>
              </div>
              <div className="bg-gray-800 p-3 rounded-lg text-sm text-gray-300">
                Hello! I'm your personal AI Journalist.
              </div>
            </div>
          </div>

          <div className="flex items-start gap-2 mb-4">
            <div className="bg-gray-700 w-8 h-8 aspect-square rounded-full flex items-center justify-center">
              <span className="text-xs text-gray-300">AI</span>
            </div>
            <div className="bg-gray-800 p-3 rounded-lg text-sm text-gray-300">
              What political news do you care about?
            </div>
          </div>

          <div className="flex items-start gap-2 mb-4">
            <div className="bg-gray-800 p-3 rounded-lg text-sm text-gray-300">
              I'm interested in the Ukraine war, foreign affairs, and immigration, and tariffs.
            </div>
            <div className="bg-gray-700 w-8 h-8 aspect-square rounded-full flex items-center justify-center">
              <span className="text-xs text-gray-300">User</span>
            </div>
          </div>

          <div className="flex items-start gap-2 mb-4">
            <div className="bg-gray-700 w-8 h-8 aspect-square rounded-full flex items-center justify-center">
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
                  className="h-8 w-8 text-gray-200 hover:text-gray-500"
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
                  className="h-8 w-8 ml-auto text-gray-200 hover:text-gray-500"
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

              {/* Playback Speed Selector */}
              <div className="mt-4 flex items-center gap-2">
                <span className="text-xs text-gray-400">Speed:</span>
                <Select
                  value={playbackSpeed.toString()}
                  onValueChange={(value) => setPlaybackSpeed(Number.parseFloat(value))}
                >
                  <SelectTrigger className="w-20 text-xs bg-gray-700 text-gray-300">{playbackSpeed}x</SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0.5">0.5x</SelectItem>
                    <SelectItem value="1">1x</SelectItem>
                    <SelectItem value="1.2">1.2x</SelectItem>
                    <SelectItem value="1.5">1.5x</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="text-xs text-center mt-2 text-gray-400">Weekly Briefing</div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}
