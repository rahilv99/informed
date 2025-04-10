'use client'

import { motion } from 'framer-motion'
import { Button } from "@/components/ui/button"
import Link from 'next/link'

const product = {
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
}

export default function ProductsPage() {
  return (
    <div className="min-h-screen text-black flex flex-col">
      <div className="max-w-6xl w-full mx-auto px-4 py-12 flex flex-col items-center">
        <h1 className="text-5xl font-bold text-center mb-12">Our Products</h1>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mt-12 px-4 text-center"
        >
          <div>
            <h2 className="text-4xl font-bold mb-4 text-gray-700">
              {product.tagline}
            </h2>
            <p className="text-xl mb-8 max-w-2xl mx-auto">
              {product.description}
            </p>
            
            <div className="w-full sm:w-1/2 mx-auto">
              {product.subProducts.map((subProduct) => (
                <div key={subProduct.id} className="bg-black bg-opacity-10 p-6 rounded-lg">
                  <h3 className="text-2xl font-bold mb-4 text-gray-700">{subProduct.name}</h3>
                  <p className="text-lg mb-4">{subProduct.description}</p>
                  <Link href={subProduct.demo || '/product'} passHref>
                    <Button className="bg-gray-800 font-semibold hover:bg-gray-600 text-white rounded-full text-lg px-8 py-8 inline-flex items-center justify-center">
                      Demo
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

