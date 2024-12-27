'use client'

import React, { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { motion, AnimatePresence } from "framer-motion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Pagination } from "@/components/ui/pagination"
import { AudioLines } from 'lucide-react'
import Image from "next/image"


interface Step {
  icon: React.ReactNode;
  title: string;
  content: string;
  prompt: string;
}

interface AIPodcastWalkthroughProps {
  steps: Step[];
  product: string;
}

export default function AIPodcastWalkthrough({ steps, product }: AIPodcastWalkthroughProps) {
  const [currentStep, setCurrentStep] = useState<number>(0);

  let PodcastPlayer = () => <></>;

  if (product === 'insight') {
    PodcastPlayer = () => (
      <Card className="w-full bg-black bg-opacity-10 text-black mt-6 border-none">
        <CardHeader>
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
              <AudioLines className="w-6 h-6 text-primary-foreground" />
            </div>
            <CardTitle className="text-2xl">Recent Advances in Quantum Computing</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <CardDescription className="mb-6 text-lg text-gray-800">
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
  } else {
    PodcastPlayer = () => (
      <Card className="w-full bg-black bg-opacity-10 text-black mt-6 border-none">
        <CardHeader>
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
              <AudioLines className="w-6 h-6 text-primary-foreground" />
            </div>
            <CardTitle className="text-2xl">Recent Advances in Quantum Computing</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <CardDescription className="mb-6 text-lg text-gray-800">
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
    );
  }

  return (
    <div className="container mx-auto py-12">
      <Tabs defaultValue="setup" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mx-auto h-14 rounded-lg bg-black bg-opacity-10 p-1 text-gray-800">
          <TabsTrigger
            value="setup"
            className="flex items-center justify-center whitespace-nowrap rounded-md px-4 py-2 text-xs sm:px-6 sm:py-3 sm:text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-20 data-[state=active]:bg-gray-800 data-[state=active]:text-black data-[state=active]:shadow-sm data-[state=active]:bg-gray-800 relative"
          >
            Walkthrough
          </TabsTrigger>
          <TabsTrigger
            value="result"
            className="flex items-center justify-center whitespace-nowrap rounded-md px-4 py-2 text-xs sm:px-6 sm:py-3 sm:text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-20 data-[state=active]:bg-gray-800 data-[state=active]:text-black data-[state=active]:shadow-sm data-[state=active]:bg-gray-800 relative"
          >
            Podcast
          </TabsTrigger>
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
              <Card className="bg-black bg-opacity-10 text-black border-none mt-6">
                <CardHeader>
                  <CardTitle>Updates Podcast Setup</CardTitle>
                  <CardDescription className="text-gray-800">
                    Follow the steps to set up your personalized podcast.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-8">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0 w-12 h-12 bg-primary rounded-full flex items-center justify-center text-gray-200">
                        {steps[currentStep].icon}
                      </div>
                      <div>
                        <h3 className="text-xl font-semibold">
                          {steps[currentStep].title}
                        </h3>
                        <p className="text-gray-800 font-semibold">
                          {steps[currentStep].content}
                        </p>
                      </div>
                    </div>
                    <Card className="bg-gray-500 bg-opacity-10 text-black border-none">
                      <CardContent className="pt-6 flex items-center space-x-4">
                        <Image 
                          src="/logo.svg" 
                          alt="Company Logo" 
                          width={40}
                          height={40}
                        />
                        <p>{steps[currentStep].prompt}</p>
                      </CardContent>
                    </Card>
                    <Pagination className="flex justify-between">
                      <Button
                        className="bg-gray-800 text-white hover:bg-gray-600"
                        onClick={() =>
                          setCurrentStep((prev) => Math.max(0, prev - 1))
                        }
                        disabled={currentStep === 0}
                      >
                        Previous
                      </Button>
                      <Button
                        className="bg-gray-800 text-white hover:bg-gray-600"
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
  );
}

