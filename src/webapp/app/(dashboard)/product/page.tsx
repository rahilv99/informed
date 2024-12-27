'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import Link from 'next/link'

const products = [
  {
    id: 'Pulse',
    name: 'Pulse',
    tagline: 'A Modern Weekly Newsletter',
    description: 'Our cutting-edge models powered by reliable sources help professionals stay up-to-date with the latest research in their field.',
    subProducts: [
      {
        id: 'pulse',
        name: 'Pulse',
        description: 'A personalized podcast summarizing the latest updates in your field. All content includes citations to academic sources.',
        demo: '/demo/pulse'
      }
    ]
  },
  {
    id: 'Insight',
    name: 'Insight',
    tagline: 'The Best Morning Routine Since Coffee',
    description: 'Apply Auxiom models to your documents to gain deeper insights in less time.',
    subProducts: [
      {
        id: 'insight',
        name: 'Insight',
        description: 'Want your podcast to be about something in particular? Queue up scientific papers or topics, and get expert summaries and analysis.',
        demo: '/demo/insight'
      }
    ]
    },
  {
    id: 'Notes',
    name: 'Notes',
    tagline: 'Fuel your Curiosity',
    description: "Turn your notes app into a personalized mini podcast, complete with research and citations.",
    subProducts: [
      {
        id: 'Note',
        name: 'Note',
        description: 'Get the answers to your questions, and learn something new every day.',
        demo: '/demo/note'
      }
    ]
  }
]

export default function ProductsPage() {
  const [activeTab, setActiveTab] = useState('Pulse')

  return (
    <div className="min-h-screen text-black flex flex-col">
      <div className="max-w-6xl w-full mx-auto px-4 py-12 flex flex-col items-center">
        <h1 className="text-5xl font-bold text-center mb-12">Our Products</h1>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 mx-auto h-14 rounded-lg bg-black bg-opacity-10 p-1 text-gray-800">
            {products.map((product) => (
              <TabsTrigger
                key={product.id}
                value={product.id}
                className="flex items-center justify-center whitespace-nowrap rounded-md px-4 py-2 text-xs sm:px-6 sm:py-3 sm:text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-opacity-20 data-[state=active]:bg-gray-800 data-[state=active]:text-black data-[state=active]:shadow-sm data-[state=active]:bg-gray-800 relative"
              >
                {product.name}
              </TabsTrigger>
            ))}
          </TabsList>

          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="mt-12 px-4 text-center"
            >
              {products.map(
                (product) =>
                  product.id === activeTab && (
                    <div key={product.id}>
                      <h2 className="text-4xl font-bold mb-4 text-gray-700">
                        {product.tagline}
                      </h2>
                      <p className="text-xl mb-8 max-w-2xl mx-auto">
                        {product.description}
                      </p>
                      
                      {product.subProducts ? (
                        
                        <div className={`grid gap-8 mb-8 ${product.subProducts.length === 1 ? 'w-1/2 mx-auto' : 'grid-cols-1 md:grid-cols-2'}`}>
                          {product.subProducts.map((subProduct) => (
                          <div key={subProduct.id} className="bg-black bg-opacity-10 p-6 rounded-lg">
                            <h3 className="text-2xl font-bold mb-4 text-gray-700">{subProduct.name}</h3>
                            <p className="text-lg mb-4">{subProduct.description}</p>
                            {
                            <Link href={subProduct.demo || '/product'} passHref>
                              <Button className="bg-gray-800 font-semibold hover:bg-gray-600 text-white rounded-full text-lg px-8 py-8 inline-flex items-center justify-center">
                              Demo
                              </Button>
                            </Link>
                            }
                          </div>
                          ))}
                        </div>
                      ) : (
                        <div>
                      </div>
                      )}
                      
                    </div>
                  )
              )}
            </motion.div>
          </AnimatePresence>
        </Tabs>
      </div>
    </div>
  );
}

