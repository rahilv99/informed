'use client'

import React, { createContext, useContext, useState } from 'react'

type OnboardingContextType = {
  currentPage: number
  setCurrentPage: (page: number) => void
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined)

export const OnboardingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentPage, setCurrentPage] = useState(1)

  return (
    <OnboardingContext.Provider value={{ currentPage, setCurrentPage }}>
      {children}
    </OnboardingContext.Provider>
  )
}

export const useOnboarding = () => {
  const context = useContext(OnboardingContext)
  if (context === undefined) {
    throw new Error('useOnboarding must be used within an OnboardingProvider')
  }
  return context
}

