import { checkoutAction } from '@/lib/payments/actions';
import { Check } from 'lucide-react';
import { getStripePrices, getStripeProducts } from '@/lib/payments/stripe';
import { SubmitButton } from './submit-button';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

// Prices are fresh for one hour max
export const revalidate = 3600;

export default async function PricingPage() {
  const [prices, products] = await Promise.all([
    getStripePrices(),
    getStripeProducts(),
  ]);

  const plusPlan = products.find((product) => product.name === 'Plus');
  const proPlan = products.find((product) => product.name === 'Pro');

  const plusPrice = prices.find((price) => price.productId === plusPlan?.id);
  const proPrice = prices.find((price) => price.productId === proPlan?.id);

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="grid md:grid-cols-3 gap-8 w-full mx-auto">
        <PricingCard
          name={'Base'}
          price={0}
          interval={'month'}
          features={[
            'Weekly short podcast',
            'Multi host conversation',
            'Direct email delivery',
          ]}
          isFreePlan = {true}
        />
        <PricingCard
          name={plusPlan?.name || 'Plus'}
          price={plusPrice?.unitAmount || 400}
          interval={plusPrice?.interval || 'month'}
          trialDays={plusPrice?.trialPeriodDays || 7}
          features={[
            'Everything in base',
            '2 long podcasts per week',
            'Unlimited journal club access',
          ]}
          priceId={plusPrice?.id}
        />
        <PricingCard
          name={proPlan?.name || 'Pro'}
          price={proPrice?.unitAmount || 900}
          interval={proPrice?.interval || 'month'}
          trialDays={proPrice?.trialPeriodDays || 7}
          features={[
            'Everything in Plus',
            'Includes proprietary data sources',
            'Early access to AstraNote and AstraNews',
          ]}
          priceId={proPrice?.id}
        />
      </div>
    </main>
  );
}

function PricingCard({
    name,
    price,
    interval,
    trialDays,
    features,
    priceId,
    isFreePlan,
  }: {
    name: string;
    price: number;
    interval: string;
    trialDays?: number;
    features: string[];
    priceId?: string;
    isFreePlan?: boolean;
  }) {
    return (
      <div className="pt-6">
        <h2 className="text-2xl font-medium text-white mb-2">{name}</h2>
        {trialDays ? (
          <p className="text-sm text-gray-300 mb-4">
            with {trialDays} day free trial
          </p>
        ) : (
          <p className="text-sm text-gray-300 mb-4">&nbsp;</p>
        )}
        <p className="text-4xl font-medium text-white mb-6">
          ${price / 100}{' '}
          <span className="text-xl font-normal text-gray-300">
            per / {interval}
          </span>
        </p>
        <ul className="space-y-4 mb-8">
          {features.map((feature, index) => (
            <li key={index} className="flex items-start">
              <Check className="h-5 w-5 text-cyan-300 mr-2 mt-0.5 flex-shrink-0" />
              <span className="text-gray-300">{feature}</span>
            </li>
          ))}
        </ul>
        {isFreePlan ? (
          <SubmitButton freePlan = {isFreePlan}/>
        ) : (
          <form action={checkoutAction}>
            <input type="hidden" name="priceId" value={priceId} />
            <SubmitButton />
          </form>
        )}
      </div>
  );
}