import { Button } from '@/components/ui/button';
import { ArrowRight , Database, Podcast, Fingerprint } from 'lucide-react';
import Link from 'next/link';

export default function HomePage() {
  return (
    <main>
      <section className="py-20 text-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols lg:gap-8">
            <div className="text-center md:max-w-2xl md:mx-auto lg:col-span-6 ">
              <h1 className="text-4xl font-bold text-black tracking-tight sm:text-5xl md:text-6xl">
                Auxiom.
                <span className="block text-gray-700">Smarter Content</span>
              </h1>
              <p className="mt-3 text-base text-gray-700 sm:mt-5 sm:text-xl lg:text-lg xl:text-xl">
                Spend less time searching and more time learning. Auxiom brings all the newest
                advancements in your field to you.  
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

      <section className="py-16 w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-3 lg:gap-8">
            <div className="bg-black bg-opacity-10 p-8 rounded-lg">
                <div className="flex items-center justify-center h-12 w-12 rounded-md border-2 border-gray-800 text-gray-700">
                <Database className="h-6 w-6" />
                </div>
              <div className="mt-5">
                <h2 className="text-lg font-medium text-black">
                  Premium Data
                </h2>
                <p className="mt-2 text-base text-gray-700">
                  Auxiom tracks the latest breakthroughs, publications, and major events in your field,
                  keeping you informed.
                </p>
              </div>
            </div>

            <div className="bg-black bg-opacity-10 p-8 rounded-lg mt-10 lg:mt-0">
              <div className="flex items-center justify-center h-12 w-12 rounded-md border-2 border-gray-800 text-gray-700">
                <Fingerprint className="h-6 w-6" />
              </div>
              <div className="mt-5">
                <h2 className="text-lg font-medium text-black">
                  Personalized Content
                </h2>
                <p className="mt-2 text-base text-gray-700">
                  Your personalized content is curated with developments that are most relevant to you,
                  reducing informational overload.
                </p>
              </div>
            </div>

            <div className="bg-black bg-opacity-10 p-8 rounded-lg mt-10 lg:mt-0">
              <div className="flex items-center justify-center h-12 w-12 rounded-md border-2 border-gray-800 text-gray-700">
                <Podcast className="h-6 w-6" />
              </div>
              <div className="mt-5">
                <h2 className="text-lg font-medium text-black">
                  Podcast Generation
                </h2>
                <p className="mt-2 text-base text-gray-700">
                  Auxiom extracts only the most important information, generating engaging podcast 
                  episodes with our personable hosts.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
            <div>
              <h2 className="text-3xl font-bold text-black sm:text-4xl">
                Curious? Sign up for our free plan.
              </h2>
              <p className="mt-3 max-w-3xl text-lg text-gray-700">
                Our free plan offers a taste of what Auxiom can do for you. Sign up today to 
                receive weekly updates on the latest advancements in your field, straight to your inbox. 
              </p>
            </div>
            <div className="mt-8 lg:mt-0 flex justify-center lg:justify-end">
              <Link
                href='/pricing'
                target="_blank"
              >
                <Button className="bg-gray-800 hover:bg-gray-600 text-white transition duration-300 rounded-full text-xl px-12 py-6 inline-flex items-center justify-center">
                  View Plans
                  <ArrowRight className="ml-3 h-6 w-6" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
