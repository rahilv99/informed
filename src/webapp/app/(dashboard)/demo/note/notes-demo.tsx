"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PenLine, AudioLines, BrainCog, CircleIcon } from 'lucide-react';
import { Pagination } from "@/components/ui/pagination";
import { PodcastPlayer } from "./podcast-player";
import { Citations } from "./citations";
import { AnimatedTopics } from "./animated-topics";

const steps = [
  {
    icon: <PenLine className="w-6 h-6" />,
    title: "Jot Down Topics",
    content: "Write down topics of interest throughout your day.",
    prompt: "Auxiom Note Editor",
  },
  {
    icon: <BrainCog className="w-6 h-6" />,
    title: "Auxiom Analysis",
    content: "Auxiom processes your notes and generates insights.",
    prompt: "Auxiom is analyzing your topics and preparing content...",
  },
  {
    icon: <AudioLines className="w-6 h-6" />,
    title: "Mini Podcast Generation",
    content: "A personalized mini podcast is created by the end of the day.",
    prompt:
      "Your podcast is being generated with the latest information and insights.",
  },
];

export default function NotesDemo() {
  const [currentStep, setCurrentStep] = useState(0);

  return (
    <div className="container mx-auto py-4 sm:py-6">
      <Tabs defaultValue="setup" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mx-auto h-12 sm:h-14 rounded-lg bg-black bg-opacity-10 p-1 text-gray-800">
          <TabsTrigger
            value="setup"
            className="flex items-center justify-center whitespace-nowrap rounded-md px-2 py-1 text-xs sm:px-6 sm:py-3 sm:text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-20 data-[state=active]:bg-gray-800 data-[state=active]:text-black data-[state=active]:shadow-sm data-[state=active]:bg-gray-800 relative"
          >
            Walkthrough
          </TabsTrigger>
          <TabsTrigger
            value="result"
            className="flex items-center justify-center whitespace-nowrap rounded-md px-2 py-1 text-xs sm:px-6 sm:py-3 sm:text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-20 data-[state=active]:bg-gray-800 data-[state=active]:text-black data-[state=active]:shadow-sm data-[state=active]:bg-gray-800 relative"
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
              <Card className="bg-black bg-opacity-10 text-black mt-4 sm:mt-6 border-none">
                <CardHeader className="p-4 sm:p-6">
                  <CardTitle className="text-xl sm:text-2xl">
                    Auxiom Notes: Your Personal Knowledge Assistant
                  </CardTitle>
                  <CardDescription className="text-gray-800 text-sm sm:text-base">
                    Discover how Auxiom Notes transforms your ideas into
                    personalized audio content.
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-4 sm:p-6">
                  <div className="space-y-6 sm:space-y-8">
                    <div className="flex items-center space-x-3 sm:space-x-4">
                      <div className="flex-shrink-0 w-10 h-10 sm:w-12 sm:h-12 bg-primary rounded-full flex items-center justify-center text-gray-200">
                        {steps[currentStep].icon}
                      </div>
                      <div>
                        <h3 className="text-lg sm:text-xl font-semibold">
                          {steps[currentStep].title}
                        </h3>
                        <p className="text-gray-800 font-semibold text-sm sm:text-base">
                          {steps[currentStep].content}
                        </p>
                      </div>
                    </div>
                    <Card className="bg-black bg-opacity-10 text-black border-none">
                      <CardContent className="p-4 sm:pt-6">
                        <p className="mb-4 text-sm sm:text-base">{steps[currentStep].prompt}</p>
                        {currentStep === 0 && <AnimatedTopics />}
                      </CardContent>
                    </Card>
                    <Pagination className="flex justify-between">
                      <Button
                        className="bg-gray-800 text-white hover:bg-gray-600 text-sm sm:text-base"
                        onClick={() =>
                          setCurrentStep((prev) => Math.max(0, prev - 1))
                        }
                        disabled={currentStep === 0}
                      >
                        Previous
                      </Button>
                      <Button
                        className="bg-gray-800 text-white hover:bg-gray-600 text-sm sm:text-base"
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
          <Citations />
        </TabsContent>
      </Tabs>
    </div>
  );
}

