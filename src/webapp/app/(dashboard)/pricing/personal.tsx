import { checkoutAction, customerPortalAction } from '@/lib/payments/actions';
import { Check } from 'lucide-react';
import { getStripePrices, getStripeProducts } from '@/lib/payments/stripe';
import { SubmitButton } from './submit-button';
import { getCurrentPlan } from '@/lib/actions'; 

// Prices are fresh for one hour max
export const revalidate = 3600;

export default async function PricingPage() {
  const [prices, products] = await Promise.all([
    getStripePrices(),
    getStripeProducts(),
  ]);

  let plan = 'free';
  try {
    plan = await getCurrentPlan();
  } catch {
    plan = 'free';
  }

  
  const plusPlan = products.find((product) => product.name === 'Plus');
  const proPlan = products.find((product) => product.name === 'Pro');

  const plusPrice = prices.find((price) => price.productId === plusPlan?.id);
  const proPrice = prices.find((price) => price.productId === proPlan?.id);

  return (
    <main className="max-w-5xl mx-auto px-4 sm:px-4 lg:px-6 py-8">
      <div className="grid md:grid-cols-3 gap-8 w-full mx-auto">
        <PricingCard
          name={'Base'}
          price={0}
          interval={'month'}
          features={[
        'Great option to try out Auxiom',
        'Short pulse podcast',
        'Direct email delivery',
          ]}
          currentPlan={plan === 'free'}
          action_type = {plan == 'free' ? checkoutAction : customerPortalAction}
        />
        <PricingCard
          name={plusPlan?.name || 'Plus'}
          price={plusPrice?.unitAmount || 400}
          interval={plusPrice?.interval || 'month'}
          trialDays={7}
          features={[
        'Get the full Auxiom experience',
        '8-10 minute pulse podcast',
        'Access to proprietary sources',
          ]}
          priceId={plusPrice?.id}
          currentPlan={plan === 'plus' || plan === 'Plus'}
          action_type = {plan == 'free' ? checkoutAction : customerPortalAction}
        />
        { 
        <PricingCard
          name={proPlan?.name || 'Pro'}
          price={proPrice?.unitAmount || 900}
          interval={proPrice?.interval || 'month'}
          trialDays={7}
          features={[
        'Everything in Plus',
        'Access to your daily notes episode',
        'Early access to new features',
          ]}
          priceId={proPrice?.id}
          currentPlan={plan === 'pro' || plan === 'Pro'}
          action_type = {plan == 'free' ? checkoutAction : customerPortalAction}
        />
        }
      </div>
    </main>
  );
}

function PricingCard({
    name,
    price,
    interval,
    features,
    priceId,
    currentPlan,
    action_type,
    trialDays
  }: {
    name: string;
    price: number;
    interval: string;
    features: string[];
    priceId?: string;
    currentPlan?: boolean;
    action_type: any;
    trialDays?: number;
  }) {
    return (
      <div className="pt-6">
        <h2 className="text-2xl font-medium text-black mb-2">{name}</h2>
        {trialDays ? (
          <p className="text-sm text-gray-700 mb-4">
            with {trialDays} day free trial
          </p>
        ) : (
          <p className="text-sm text-gray-700 mb-4">&nbsp;</p>
        )}
        <p className="text-4xl font-medium text-black mb-6">
          ${price / 100}{' '}
          <span className="text-xl font-normal text-gray-700">
            per / {interval}
          </span>
        </p>
        <ul className="space-y-4 mb-8">
          {features.map((feature, index) => (
            <li key={index} className="flex items-start">
              <Check className="h-5 w-5 text-gray-600 mr-2 mt-0.5 flex-shrink-0" />
              <span className="text-gray-700">{feature}</span>
            </li>
          ))}
        </ul>
        {currentPlan ? (
          <SubmitButton display = 'Continue'/>
        ) : (
          <form action={action_type}>
            {action_type === checkoutAction ?(
              <input type="hidden" name="priceId" value={priceId} />
            ) : null}
            <SubmitButton display = 'Switch'/>
          </form>
        )}
      </div>
  );
}