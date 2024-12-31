'use client'

import React, { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { motion, AnimatePresence } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
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

let PodcastPlayer = () => {
  const sources = product === 'pulse' 
    ? [
        { title: "Attention Is All You Need", 
          summary: " Revolutionizing machine translation, this paper introduces the Transformer, a neural network architecture ditching RNNs and CNNs for a purely attention-based approach. Achieving state-of-the-art results on English-to-German and English-to-French translation with significantly faster training, the Transformer boasts superior parallelization and long-range dependency capture. A must-read for anyone working with sequence transduction or deep learning.", 
          url: "https://arxiv.org/abs/1706.03762" },
        { title: "Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets", 
          summary: "Neural networks trained on tiny, artificial datasets surprisingly achieve perfect generalization after overfitting—a phenomenon called 'grokking.' This study reveals grokking isn't random, but strongly linked to dataset size; smaller datasets need far more training. While limited by artificial data, it offers crucial insights into deep learning's data efficiency and generalization mysteries.", 
          url: "https://arxiv.org/abs/2201.02177" },
        { title: "Neural Networks are Decision Trees", 
          summary: "Neural networks, regardless of architecture, are mathematically equivalent to decision trees! This paper proves it, offering a potentially game-changing perspective on neural network interpretability and computation. While the resulting decision trees might be large, this finding could revolutionize our understanding and efficiency of deep learning.", 
          url: "https://arxiv.org/abs/2210.05189" },
        { title: "On the cross-validation bias due to unsupervised pre-processing", 
          summary: "Unsupervised data preprocessing (like feature selection & scaling) *can significantly bias cross-validation results, leading to inaccurate model performance estimates and potentially suboptimal model choices. This effect, explored via simulation, depends on dataset characteristics and is particularly problematic with small samples & high dimensionality. Read if you use unsupervised preprocessing and care about reliable model evaluation.", 
          url: "https://arxiv.org/abs/1901.08974" },
        { title: "LoRA: Low-Rank Adaptation of Large Language Models", 
          summary: "LoRA: Fine-tune massive language models without retraining the entire model! Achieve comparable or better performance with up to 10,000x fewer parameters, drastically reduced memory usage (3x less for GPT-3 175B), and faster training—all with zero inference latency increase.", 
          url: "https://arxiv.org/abs/2106.09685" }
      ]
    : [
        { title: "Attention Is All You Need", 
          summary: "Revolutionizing neural machine translation, the Transformer architecture ditches recurrence and convolutions for pure attention. This allows massive parallelization, resulting in faster training and superior translation quality (higher BLEU scores) than previous state-of-the-art models. Key to its success is multi-head self-attention, enabling the model to weigh different parts of the input sequence simultaneously. While computationally expensive for extremely long sequences, its speed and accuracy make it a game-changer.", 
          url: "https://arxiv.org/abs/1706.03762" },
        { title: "A Review of Multimodal Explainable Artificial Intelligence: Past, Present and Future", 
          summary: "Unraveling the Black Box: This review comprehensively explores the evolution of explainable AI (XAI), focusing on multimodal systems (text, images, audio, etc.). It categorizes XAI methods across four AI eras, highlighting challenges in interpreting increasingly complex models like LLMs. Key takeaways include a structured taxonomy of MXAI methods, identified challenges, and future research directions. A GitHub repo with supporting resources is available. Essential reading for anyone working with or researching complex AI systems needing transparency and trust.", 
          url: "https://www.semanticscholar.org/paper/6c6ee9986b06cad886ef8e534336a19a21fc6b2c" },
        { title: "A Review of Human Emotion Synthesis Based on Generative Technology", 
          summary: "Generative AI is revolutionizing emotion synthesis! This review explores how Autoencoders, GANs, Diffusion Models, LLMs, & Sequence-to-Sequence models create realistic emotional expressions (facial, speech, text). It highlights impressive progress but also crucial limitations: inconsistent datasets & metrics hinder comparisons, and ethical concerns (deepfakes, bias) demand attention.", 
          url: "https://www.semanticscholar.org/paper/bd7e210994b7ba821c29a4d60325493646283b20" }
      ];

  return (
    <Card className="w-full bg-black bg-opacity-10 text-black mt-6 border-none">
      <CardHeader>
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 sm:w-12 sm:h-12 bg-primary rounded-full flex items-center justify-center">
            <AudioLines className="w-5 h-5 sm:w-6 sm:h-6 text-primary-foreground" />
          </div>
          {product === 'pulse' ? (
            <CardTitle className="text-lg sm:text-2xl">Weekly Update in AI: From Attention to Adaptation</CardTitle>
          ) : (
            <CardTitle className="text-lg sm:text-2xl">Attention is All You Need</CardTitle>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {product === 'pulse' ? (
          <CardDescription className="mb-4 sm:mb-6 text-sm sm:text-lg text-gray-800">
            In this special edition of pulse, we discuss the most influential papers of the last decade related to Generative AI.
          </CardDescription>
        ) : (
          <CardDescription className="mb-4 sm:mb-6 text-sm sm:text-lg text-gray-800">
            Use auxiom to help you understand complex papers, such as this foundational paper for modern generative AI models. Simply provide your documents and we will generate expert analyses and related articles.
          </CardDescription>
        )}
        <div className="p-2 sm:p-4 flex items-center space-x-4">
          <audio controls className="w-full">
            <source src={product === 'pulse' ? "/pulse-demo.mp3" : "/insight-demo.mp3"} type="audio/mp3" />
            Your browser does not support the audio element.
          </audio>
        </div>
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">Sources Discussed:</h3>
          <div className="space-y-4">
            {sources.map((source, index) => (
              <div key={index} className="bg-white bg-opacity-20 p-3 rounded-md">
                <h4 className="font-medium">{source.title}</h4>
                <p className="text-sm text-gray-700 mt-1">{source.summary}</p>
                <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline mt-1 inline-block">
                  Read more
                </a>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

  return (
    <div className="container mx-auto py-12">
      <Tabs defaultValue="setup" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mx-auto h-auto rounded-lg bg-black bg-opacity-10 p-1 text-gray-800">
          <TabsTrigger
            value="setup"
            className="flex items-center justify-center whitespace-nowrap rounded-md px-2 py-2 text-xs sm:px-4 sm:py-3 sm:text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-20 data-[state=active]:bg-gray-800 data-[state=active]:text-black data-[state=active]:shadow-sm data-[state=active]:bg-gray-800 relative"
          >
            Walkthrough
          </TabsTrigger>
          <TabsTrigger
            value="result"
            className="flex items-center justify-center whitespace-nowrap rounded-md px-2 py-2 text-xs sm:px-4 sm:py-3 sm:text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-20 data-[state=active]:bg-gray-800 data-[state=active]:text-black data-[state=active]:shadow-sm data-[state=active]:bg-gray-800 relative"
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
                  <CardTitle className="text-lg sm:text-xl">Updates Podcast Setup</CardTitle>
                  <CardDescription className="text-sm sm:text-base text-gray-800">
                    Follow the steps to set up your personalized podcast.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4 sm:space-y-8">
                    <div className="flex items-start sm:items-center space-x-4">
                      <div className="flex-shrink-0 w-10 h-10 sm:w-12 sm:h-12 bg-primary rounded-full flex items-center justify-center text-gray-200">
                        {steps[currentStep].icon}
                      </div>
                      <div>
                        <h3 className="text-lg sm:text-xl font-semibold">
                          {steps[currentStep].title}
                        </h3>
                        <p className="text-sm sm:text-base text-gray-800 font-semibold">
                          {steps[currentStep].content}
                        </p>
                      </div>
                    </div>
                    <Card className="bg-gray-500 bg-opacity-10 text-black border-none">
                      <CardContent className="pt-4 sm:pt-6 flex items-center space-x-2 sm:space-x-4">
                        <Image 
                          src="/logo.svg" 
                          alt="Company Logo" 
                          width={30}
                          height={30}
                          className="w-8 h-8 sm:w-10 sm:h-10"
                        />
                        <p className="text-sm sm:text-base">{steps[currentStep].prompt}</p>
                      </CardContent>
                    </Card>
                    <Pagination className="flex justify-between">
                      <Button
                        className="bg-gray-800 text-white hover:bg-gray-600 text-xs sm:text-sm px-2 py-1 sm:px-4 sm:py-2"
                        onClick={() =>
                          setCurrentStep((prev) => Math.max(0, prev - 1))
                        }
                        disabled={currentStep === 0}
                      >
                        Previous
                      </Button>
                      <Button
                        className="bg-gray-800 text-white hover:bg-gray-600 text-xs sm:text-sm px-2 py-1 sm:px-4 sm:py-2"
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

