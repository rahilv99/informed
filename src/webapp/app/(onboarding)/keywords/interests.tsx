"use client"
import { Button } from "@/components/ui/button"
import type React from "react"

import { useState, useRef, useEffect } from "react"
import { submitInterests } from "@/lib/actions"
import { toast } from "@/hooks/use-toast"
import { useRouter } from "next/navigation"
import { useOnboarding } from "../context/OnboardingContext" // Keeping the original import path
import { X, Plus } from "lucide-react"

// Define the props interface for the component
interface InterestsProps {
  // Add any props that might be passed to this component
  onComplete?: (interests: string[]) => void
}

// Suggested interests that might be relevant for academic/research contexts
const SUGGESTED_INTERESTS = [
  "Orbital Dynamics",
  "Drug-Resistant Epilepsy",
  "Game Theory",
  "Combinatorics",
  "Generative Image Models",
  "Machine Learning",
  "Quantum Computing",
  "Neuroscience",
  "Climate Science",
  "Bioinformatics",
  "Cryptography",
  "Artificial Intelligence",
  "Data Science",
  "Robotics",
  "Molecular Biology",
]

export function Interests({ onComplete }: InterestsProps) {
  // Initialize with initialInterests if provided
  const [keywords, setKeywords] = useState<string[]>([])
  const router = useRouter()
  const { setCurrentPage } = useOnboarding()

  const [inputValue, setInputValue] = useState("")
  const [suggestions, setSuggestions] = useState<string[]>([])
  const inputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)

  // Handle outside clicks to close suggestions
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setSuggestions([])
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  const handleTextareaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setInputValue(value)
    if (value.trim()) {
      const filtered = SUGGESTED_INTERESTS.filter(
        (interest) => interest.toLowerCase().includes(value.toLowerCase()) && !keywords.includes(interest),
      )
      setSuggestions(filtered)
    } else {
      setSuggestions([])
    }
  }

  const addInterest = (interest: string) => {
    if (interest.trim() && !keywords.includes(interest)) {
      setKeywords([...keywords, interest])
      setInputValue("")
      setSuggestions([])

      // Focus back on input after adding
      if (inputRef.current) {
        inputRef.current.focus()
      }
    }
  }

  const removeInterest = (interest: string) => {
    setKeywords(keywords.filter((i) => i !== interest))
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && inputValue.trim()) {
      e.preventDefault()
      addInterest(inputValue)
    } else if (e.key === "Backspace" && inputValue === "" && keywords.length > 0) {
      // Remove the last tag when backspace is pressed and input is empty
      const newInterests = [...keywords]
      newInterests.pop()
      setKeywords(newInterests)
    }
  }

  const handleSubmit = async () => {
    try {
      const ret = await submitInterests(keywords.join(", "))

      if (ret.error) {
        toast({
          title: "Error",
          description: ret.error,
          variant: "destructive",
        })
      } else {
        toast({
          title: "Success",
          description: "Your interests have been saved.",
        })

        // Call the onComplete prop if provided
        if (onComplete) {
          onComplete(keywords)
        }

        setCurrentPage(4)
        router.push("/day")
      }
    } catch (error) {
      console.error("Error submitting interests:", error)
      toast({
        title: "Error",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      })
    }
  }

  return (
    <main>
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
            <div>
              <h1 className="text-3xl font-bold text-black sm:text-4xl">Tell us about your interests</h1>
              <p className="mt-4 text-base text-gray-700">
                Add 5-10 interests that describe your research, projects, or work.
              </p>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-2">
        {/* Tag display area - reduced top margin by using mt-2 */}
        <div
          className="w-full min-h-24 text-black bg-black bg-opacity-10 rounded-xl p-6 backdrop-filter backdrop-blur-lg border-none flex flex-wrap gap-2 items-start content-start"
          onClick={() => inputRef.current?.focus()}
        >
          {keywords.map((interest) => (
            <div
              key={interest}
              className="px-3 py-2 text-sm bg-white bg-opacity-30 hover:bg-opacity-40 text-black rounded-full flex items-center"
            >
              {interest}
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  removeInterest(interest)
                }}
                className="ml-2 text-black hover:text-gray-700"
                aria-label={`Remove ${interest}`}
              >
                <X size={14} />
              </button>
            </div>
          ))}

          <div className="relative flex-grow min-w-[200px]">
            <input
              ref={inputRef}
              type="text"
              placeholder={
                keywords.length === 0
                  ? "Examples: Orbital Dynamics, Drug-Resistant Epilepsy, Game Theory..."
                  : "Add another interest..."
              }
              value={inputValue}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              className="w-full border-none bg-transparent text-black placeholder:text-gray-500 focus:outline-none p-0"
            />

            {suggestions.length > 0 && (
              <div
                ref={suggestionsRef}
                className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-md max-h-60 overflow-auto"
              >
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-black"
                    onClick={() => addInterest(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Popular suggestions */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
        <h3 className="text-sm font-medium mb-2 text-gray-700">Suggested interests</h3>
        <div className="flex flex-wrap gap-2">
          {SUGGESTED_INTERESTS.slice(0, 8).map(
            (interest) =>
              !keywords.includes(interest) && (
                <button
                  key={interest}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-full cursor-pointer hover:bg-black hover:bg-opacity-5 text-black flex items-center"
                  onClick={() => addInterest(interest)}
                >
                  <Plus size={12} className="mr-1" />
                  {interest}
                </button>
              ),
          )}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-end py-5">
          <Button
            onClick={handleSubmit}
            className="mt-4 bg-gray-800 text-white px-4 py-2 rounded-full font-semibold hover:bg-gray-600 transition duration-300"
          >
            Submit
          </Button>
        </div>
      </div>
    </main>
  )
}

