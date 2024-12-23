'use client'

import React, { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { AudioLines, User, FileUp, BrainCog, CircleIcon } from 'lucide-react'
import { Pagination } from "@/components/ui/pagination"

const steps = [
  {
    icon: <User className="w-6 h-6" />,
    title: "Create User Profile",
    content: "Ex:  Generative AI, Text-to-Speech, Transformer Models, Linguistics",
    prompt:  "Enter keywords related to your research interests."
  },
  {
    icon: <FileUp className="w-6 h-6" />,
    title: "Upload Articles",
    prompt:  "Upload PDFs of scientific articles to your queue.",
    content: "Ex: Attention is All You Need"
  },
  {
    icon: <BrainCog className="w-6 h-6" />,
    title: "Astra Analysis",
    content: "Astra selects an article and generates an expert analysis.",
    prompt: "Astra is analyzing the uploaded articles and generating insights..."
  },
]

export default function JournalClubPodcastWalkthrough() {
  const [currentStep, setCurrentStep] = useState(0)

  const PodcastPlayer = () => (
    <Card className="w-full bg-white bg-opacity-10 text-white mt-6 border-none">
      <CardHeader>
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
            <AudioLines className="w-6 h-6 text-primary-foreground" />
          </div>
          <CardTitle className="text-2xl">Recent Advances in Quantum Computing</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <CardDescription className="mb-6 text-lg text-gray-200">
          In this episode, we discuss a recent paper on quantum computing and its potential applications in cryptography. 
          We explore how these advancements might impact your work in network security and data protection.
        </CardDescription>
        <div className="p-4 flex items-center space-x-4">
          <audio controls className="w-full">
            <source src="/demo-podcast.mp3" type="audio/mp3" />
            Your browser does not support the audio element.
          </audio>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="container mx-auto py-6">
      <Tabs defaultValue="setup" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mx-auto h-14 rounded-lg bg-cyan-900/20 p-1 text-cyan-100">
          <TabsTrigger value="setup" className="flex items-center justify-center whitespace-nowrap rounded-md px-4 py-2 text-xs sm:px-6 sm:py-3 sm:text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-10 data-[state=active]:bg-cyan-200 data-[state=active]:text-white data-[state=active]:shadow-sm">Walkthrough</TabsTrigger>
          <TabsTrigger value="result" className="flex items-center justify-center whitespace-nowrap rounded-md px-4 py-2 text-xs sm:px-6 sm:py-3 sm:text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-10 data-[state=active]:bg-cyan-200 data-[state=active]:text-white data-[state=active]:shadow-sm">Podcast</TabsTrigger>
        </TabsList>
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <TabsContent value="setup">
          <Card  className="bg-white bg-opacity-10 text-white mt-6 border-none">
            <CardHeader>
              <CardTitle>Journal Club Podcast Setup</CardTitle>
              <CardDescription className="text-gray-200">
                Follow the steps to set up your personalized AI podcast.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-8">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary rounded-full flex items-center justify-center text-cyan-200">
                    {steps[currentStep].icon}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold">
                      {steps[currentStep].title}
                    </h3>
                    <p className="text-gray-200 font-semibold">
                      {steps[currentStep].content}
                    </p>
                  </div>
                </div>
                <Card className="bg-cyan-100 bg-opacity-10 text-white border-none">
                    <CardContent className="pt-6 flex items-center space-x-4">
                    <CircleIcon className="w-8 h-8 text-cyan-200" />
                    <p>{steps[currentStep].prompt}</p>
                    </CardContent>
                </Card>
                <Pagination className="flex justify-between">
                  <Button
                    className="bg-cyan-200 text-black hover:bg-cyan-600"
                    onClick={() =>
                      setCurrentStep((prev) => Math.max(0, prev - 1))
                    }
                    disabled={currentStep === 0}
                  >
                    Previous
                  </Button>
                  <Button
                    className="bg-cyan-200 text-black hover:bg-cyan-600"
                    onClick={() =>
                      setCurrentStep((prev) =>
                        Math.min(steps.length - 1, prev + 1)
                      )
                    }
                    disabled={currentStep === steps.length - 1}
                  >
                    Next
                  </Button>
                </Pagination>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
            </motion.div>
          </AnimatePresence>
          <TabsContent value="result">
            <PodcastPlayer />
          </TabsContent>
      </Tabs>
    </div>
  )
}

