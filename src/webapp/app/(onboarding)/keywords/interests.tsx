"use client"
import { Button } from "@/components/ui/button"
import type React from "react"
import { useState, useRef, useEffect, useMemo } from "react"
import { submitInterests } from "@/lib/actions"
import { toast } from "@/hooks/use-toast"
import { useRouter } from "next/navigation"
import { useOnboarding } from "../context/OnboardingContext"
import { X, Plus } from "lucide-react"
import Fuse from "fuse.js"

// Define the props interface for the component
interface InterestsProps {
  // Add any props that might be passed to this component
  onComplete?: (interests: string[]) => void
}

// Suggested interests that might be relevant for academic/research contexts
const SUGGESTED_INTERESTS = [
  "Climate Policy",
  "Global Trade",
  "Energy Policy",
  "Cybersecurity",
  "Tech Regulation",
  "Economic Policy",
  "Voting Rights",
  "International Relations",
  "Public Health",
  "Immigration Reform",
  "Media Freedom",
  "Income Inequality",
  "Healthcare Policy",
  "Financial Regulation",
  "Space Policy",
  "Arms Control",
  "Education Policy",
  "Civil Rights",
  "Gender Equality",
  "Trade Policy",
  "Misinformation",
  "Urban Development",
  "Human Rights",
  "Political Polarization",
  "Corporate Influence",
  "Infrastructure",
  "Food Security",
  "Water Policy",
  "Economic Agreements",
  "Gun Control",
  "Housing Policy",
  "Labor Rights",
  "Public Transit",
  "Indigenous Rights",
  "Tax Policy",
  "Electoral Reform",
  "Law Enforcement",
  "Drug Policy",
  "Justice Reform",
  "Religious Freedom",
  "Science Policy",
  "Diversity Policies",
  "Conservation Laws",
  "Digital Rights",
  "Corporate Regulation",
  "Election Security",
  "Transparency Laws",
  "National Security",
  "Media Protections",
  "Biodiversity Laws",
  "Wages Policy",
  "Rural Development",
  "Child Welfare",
  "Universal Healthcare",
  "Education Standards",
  "Civic Engagement",
  "Trade Globalization",
  "Energy Subsidies",
  "Workforce Automation",
  "Campaign Finance",
  "Veterans' Affairs",
  "Corporate Taxation",
  "Statehood Policies",
  "Climate Change",
  "Free Speech",
  "Election Integrity",
  "Government Debt",
  "Food Safety",
  "Mental Health",
  "Diplomacy Policy",
  "AI Ethics",
  "Consumer Safety",
  "Animal Welfare",
  "Foreign Aid",
  "Legal System",
  "Fair Housing",
  "Nuclear Policy",
  "Education Reform",
  "Workplace Rights",
  "Family Policy",
  "Criminal Sentencing",
  "Healthcare Costs",
  "Substance Abuse",
  "Land Management",
  "Government Ethics",
  "Tech Governance",
  "Death Penalty",
  "Consumer Protection",
  "Wildlife Laws",
  "Research Investment",
  "Economic Justice",
  "Self-Governance",
  "Judicial Reform",
  "Social Welfare",
  "Waste Management",
  "Political Expression",
  "Digital Economy",
  "Rural Policy",
  "United States",
  "China Politics",
  "European Union",
  "Middle East",
  "Russia Policy",
  "Latin America",
  "India Politics",
  "African Union",
  "Japan Politics",
  "South Korea",
  "Australia Policy",
  "Canada Governance",
  "Brazil Politics",
  "Germany Policy",
  "United Kingdom",
  "France Politics",
  "Italy Governance",
  "Scandinavian Policy"
]

// Function to calculate similarity between two strings
function calculateSimilarity(str1: string, str2: string): number {
  const s1 = str1.toLowerCase()
  const s2 = str2.toLowerCase()

  // Check for exact word matches
  const words1 = s1.split(/\s+/)
  const words2 = s2.split(/\s+/)

  let wordMatchCount = 0
  for (const word1 of words1) {
    if (word1.length < 3) continue // Skip short words
    for (const word2 of words2) {
      if (word2.length < 3) continue // Skip short words
      if (word1 === word2 || word1.includes(word2) || word2.includes(word1)) {
        wordMatchCount++
      }
    }
  }

  // Check for character-level similarity
  let charMatchCount = 0
  for (let i = 0; i < s1.length - 2; i++) {
    const trigram = s1.substring(i, i + 3)
    if (s2.includes(trigram)) {
      charMatchCount++
    }
  }

  return wordMatchCount * 3 + charMatchCount
}

// Keyword component from keywords.tsx with original styling
function Keyword({ keyword, onRemove }: { keyword: string; onRemove: (keyword: string) => void }) {
  return (
    <div className="bg-black text-gray-300 px-3 py-1 rounded-full flex items-center">
      <span className="mr-1">{keyword}</span>
      <button
        onClick={(e) => {
          e.stopPropagation()
          onRemove(keyword)
        }}
        className="text-gray-500 hover:text-white"
      >
        <X size={14} />
      </button>
    </div>
  )
}

// AddKeyword component adapted from keywords.tsx with original styling
function AddKeyword({
  value,
  onChange,
  onKeyDown,
  placeholder,
  inputRef,
  onAdd,
}: {
  value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  onKeyDown: (e: React.KeyboardEvent) => void
  placeholder: string
  inputRef: React.RefObject<HTMLInputElement>
  onAdd: (value: string) => void
}) {
  return (
    <div className="relative">
      <input
        ref={inputRef}
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        onKeyDown={onKeyDown}
        onKeyPress={(e) => e.key === "Enter" && onAdd(value)}
        className="bg-black text-gray-300 px-3 py-1 rounded-full pr-8 focus:outline-none focus:ring-2 focus:ring-gray-300"
      />
      <button
        onClick={() => onAdd(value)}
        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-white"
      >
        <Plus size={14} />
      </button>
    </div>
  )
}

export function Interests({ onComplete }: InterestsProps) {
  const [keywords, setKeywords] = useState<string[]>([])
  const router = useRouter()
  const { setCurrentPage } = useOnboarding()

  const [inputValue, setInputValue] = useState("")
  const [suggestions, setSuggestions] = useState<string[]>([])
  const inputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)

  // Initialize Fuse.js with stronger fuzziness
  const fuse = useMemo(() => new Fuse(SUGGESTED_INTERESTS, { threshold: 0.4, distance: 100 }), [])

  // Get dynamic suggestions based on current interests
  const dynamicSuggestions = useMemo(() => {
    if (keywords.length === 0) {
      // If no interests selected yet, return original suggestions
      return SUGGESTED_INTERESTS
    }

    // Calculate similarity scores for each suggestion based on current interests
    const scoredSuggestions = SUGGESTED_INTERESTS.filter((suggestion) => !keywords.includes(suggestion)).map(
      (suggestion) => {
        let totalScore = 0
        for (const keyword of keywords) {
          totalScore += calculateSimilarity(keyword, suggestion)
        }
        return { suggestion, score: totalScore }
      },
    )

    // Sort by score (highest first) and return the top 5 suggestions
    return scoredSuggestions
      .sort((a, b) => b.score - a.score)
      .slice(0, 5)
      .map((item) => item.suggestion)
  }, [keywords])

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
      const filtered = fuse.search(value).map(result => result.item).filter(
        (interest) => !keywords.includes(interest)
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
      <section className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
            <div>
              <h1 className="text-3xl font-bold text-black sm:text-4xl">Tell us about your interests</h1>
              <p className="mt-4 text-base text-gray-700">
                Enter 5-10 topics to stay informed about.
              </p>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-2">
        {/* Container with keywords.tsx styling */}
        <div className="w-full max-w-7xl rounded-lg shadow-md p-6 bg-black bg-opacity-10 rounded-xl backdrop-filter backdrop-blur-lg ml-0 h-64">
          <h1 className="text-2xl font-semibold text-black mb-4">I want my podcasts to be about...</h1>
          <div className="flex flex-wrap gap-2 mb-4">
            {keywords.map((interest) => (
              <Keyword key={interest} keyword={interest} onRemove={removeInterest} />
            ))}
          </div>

          <div className="flex items-center">
            <AddKeyword
              value={inputValue}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              placeholder={keywords.length === 0 ? "Add interest..." : "Add another interest..."}
              inputRef={inputRef}
              onAdd={addInterest}
            />
          </div>

          {/* Suggestions dropdown */}
          {suggestions.length > 0 && (
            <div ref={suggestionsRef} className="mt-2 bg-white border rounded-md shadow-md max-h-60 overflow-auto">
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

      {/* Popular suggestions - now dynamically based on current interests */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
        <h3 className="text-sm font-medium mb-2 text-gray-700">
          {keywords.length > 0 ? "Related interests" : "Suggested interests"}
        </h3>
        <div className="flex flex-wrap gap-2">
          {dynamicSuggestions.slice(0, 10).map(
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

