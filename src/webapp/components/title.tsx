import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function Title() {
  return (
    <section className="py-20 text-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols lg:gap-8">
            <div className="text-center md:max-w-2xl md:mx-auto lg:col-span-6 ">
              <h1 className="text-4xl font-bold text-black tracking-tight sm:text-5xl md:text-6xl">
                Auxiom.
                <span className="block text-gray-700 text-2xl">Your Personalized AI Journalist</span>
              </h1>
              <p className="mt-3 text-base text-gray-700 sm:mt-5 sm:text-xl lg:text-lg xl:text-xl">
                A wealth of information creates a poverty of attention. Let Auxiom be your attention.
              </p>
              <div className="mt-8 sm:max-w-lg sm:mx-auto sm:text-center lg:text-center lg:mx-auto">
                <Link href="/product">
                  <Button className="bg-gray-800 hover:bg-gray-600 text-white transition duration-300 font-semibold rounded-full text-lg px-8 py-8 inline-flex items-center justify-center">
                    Products
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

  )
}