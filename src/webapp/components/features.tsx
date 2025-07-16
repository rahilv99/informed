import { ArrowRight, BookOpen, Database, Fingerprint, Podcast } from 'lucide-react';
import RotatingTopics from './rotating-topics'; // Import the RotatingTopics component
import Link from 'next/link';
import { Button } from './ui/button';

export default function Features() {
  return (
    <>
      {/* RotatingTopics Component */}
      <RotatingTopics />

      {/* Features Section */}
      <section className="py-16 w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-6">
              <Podcast className="h-8 w-8 text-primary" />
            </div>
            <h2 className="text-3xl font-bold text-black sm:text-4xl mb-4">All in a Weekly 5 Minute Podcast</h2>
            <p className="max-w-3xl mx-auto text-lg text-gray-700 mb-8">
              Listen to our charismatic AI hosts cut through the legislative noise and deliver the most relevant updates on the issues you care about.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/articles">
                <Button className="bg-primary hover:bg-primary/90 text-white transition duration-300 rounded-full text-lg px-8 py-3 inline-flex items-center justify-center">
                  <BookOpen className="mr-2 h-5 w-5" />
                  Demo
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>
          </div>

          <div className="lg:grid lg:grid-cols-3 lg:gap-8">
            <div className="bg-black bg-opacity-10 p-8 rounded-lg">
              <div className="flex items-center justify-center h-12 w-12 rounded-md border-2 border-gray-800 text-gray-700">
                <Database className="h-6 w-6" />
              </div>
              <div className="mt-5">
                <h2 className="text-lg font-medium text-black">
                  Primary Data Sources
                </h2>
                <p className="mt-2 text-base text-gray-700">
                  Auxiom analyzes legislative documents, financial data, and research papers to find the root of the action.
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
                  Auxiom composes hundreds of pages of documents into a 5 minute weekly podcast
                  episode with our personable hosts.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}