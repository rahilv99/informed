'use server';

import { redirect } from 'next/navigation';
import { createCheckoutSession, createCustomerPortalSession } from './stripe';
import { withUser } from '@/lib/auth/middleware';


// could be sketch here; this is overcomplicated bc it was initially for teams and now it's for users (12/2/2024)
export const checkoutAction = withUser(async (formData, user) => {
  const priceId = formData.get('priceId') as string;
  await createCheckoutSession({ priceId });
});

export const customerPortalAction = withUser(async (_, user) => {
  const portalSession = await createCustomerPortalSession(user);
  redirect(portalSession.url);
});
