import { Button } from '@/components/ui/button';
import { ArrowRight , Database, Podcast, Fingerprint } from 'lucide-react';
import Link from 'next/link';
import Title from '../../components/title';
import Features from '../../components/features';

export default function HomePage() {
  return (
    <main>
      <Title />

      <Features />

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
