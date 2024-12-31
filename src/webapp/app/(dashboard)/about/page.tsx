'use client'
import { Card, CardContent } from "@/components/ui/card"
import { HandHeart, Earth, Users } from 'lucide-react'
import { motion } from "framer-motion"
import Link from 'next/link'

export default function AboutPage() {
  return (
    <div className="min-h-screen w-full text-gray-800">
      {/* Hero Section */}
      <div className="relative h-[50vh] flex items-center justify-center">
        <div className="absolute inset-0 bg-black bg-opacity-10" />
        <motion.h1
          className="relative z-10 text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-center max-w-4xl mx-auto leading-tight"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          Empowering Minds Through Accessible Knowledge
        </motion.h1>
      </div>

      {/* Mission Statement */}
      <div className="max-w-4xl mx-auto my-16 px-4">
        <motion.p
          className="text-2xl sm:text-3xl md:text-4xl text-center font-semibold leading-relaxed"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          Our mission is to foster a world where knowledge is a shared and universal resource.
        </motion.p>
      </div>

      {/* Cards Section */}
      <div className="max-w-7xl mx-auto my-16 px-4 flex justify-center">
        <motion.div
          className="w-full md:w-1/2"
          initial={{ opacity: 0, y: 0 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <Card className="border-none bg-opacity-10 bg-black text-gray-700 h-full">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4 mb-4">
            <Earth className="h-10 w-10" />
            <h2 className="text-3xl font-bold">Our Motivation</h2>
          </div>
          <p className="text-xl">
            We believe that education is a fundamental human right. Auxiom aims to be accessible to all by
            transforming complex academic content into engaging audio experiences.
          </p>
        </CardContent>
          </Card>
        </motion.div>
      </div>


      {/* Call to Action */}
      <div className="text-center my-16">
        <motion.h2
          className="text-3xl font-bold mb-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 1.2 }}
        >
          Join Us in Our Mission
        </motion.h2>
        <motion.button
          className="bg-gray-800 hover:bg-gray-600 text-white font-bold py-3 px-8 rounded-full text-lg transition-all duration-300"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.5 }}
        >
          <Link href='/sign-up' className="h-6 w-6 mr-2">
          Get Started with Auxiom
          </Link>
        </motion.button>
      </div>
    </div>
  )
}

