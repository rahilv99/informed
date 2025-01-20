import { Check } from 'lucide-react';
import Link from 'next/link';

export default function B2BPricingPage() {
  return (
    <main className="max-w-5xl mx-auto px-4 sm:px-4 lg:px-6 py-8">
      <div className="grid md:grid-cols-2 gap-8 w-full mx-auto">
        <PricingCard
          name="Enterprise"
          tagline = "Tailored for your business needs"
          features={[
            'Receive expertly curated content crucial to your business',
            'Make a company newsletter people will actually listen to',
            'Improve efficiency by distributing necessary information',
            'Enterprise dashboard to review curated feeds and insights',
          ]}
        />
        <PricingCard
          name="Academic Institutions"
          tagline = "Tailored for your academic pursuits"
          features={[
            'Auxiom Pro for everyone in your organization',
            'Enable progression at the frontiers of fields',
            'Boost productivity and generate inspiration',
            'Organizational dashboard to distribute information',
          ]}
        />
      </div>
    </main>
  );
}

function PricingCard({
  name,
  tagline,
  features,
}: {
  name: string;
  tagline: string;
  features: string[];
}) {
  return (
    <div className="pt-6">
      <h2 className="text-2xl font-medium text-black mb-2">{name}</h2>
      <p className="text-sm text-gray-700 mb-4">{tagline}</p>
      <ul className="space-y-4 mb-8">
        {features.map((feature, index) => (
          <li key={index} className="flex items-start">
            <Check className="h-5 w-5 text-gray-600 mr-2 mt-0.5 flex-shrink-0" />
            <span className="text-gray-700">{feature}</span>
          </li>
        ))}
      </ul>
      <Link
        href={`/pricing/contact-sales`}
        className="block w-full bg-gray-800 text-white text-center py-2 px-4 rounded-full hover:bg-gray-600 transition-colors"
      >
        Contact Sales
      </Link>
    </div>
  );
}

