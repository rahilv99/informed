'use server';

import { 
  getUserById,
  updateUserSubscription,
} from '@/lib/db/queries';

export interface RevenueCatSubscriber {
  app_user_id: string;
  original_app_user_id: string;
}

export interface RevenueCatProduct {
  identifier: string;
  display_name: string;
}

export interface RevenueCatEntitlement {
  expires_date?: string;
  product_identifier: string;
  purchase_date: string;
}

export interface RevenueCatWebhookEvent {
  event: {
    type: string;
    app_user_id: string;
    original_app_user_id: string;
    subscriber_attributes?: Record<string, any>;
    entitlements?: Record<string, RevenueCatEntitlement>;
    product_id?: string;
    period_type?: string;
    purchased_at_ms?: number;
    expiration_at_ms?: number;
    environment?: string;
  };
  api_version: string;
}

export async function handleRevenueCatSubscriptionChange(
  event: RevenueCatWebhookEvent
) {
  const { type, app_user_id, entitlements, product_id } = event.event;

  console.log('Processing RevenueCat event:', type, 'for user:', app_user_id);

  // Find user by RevenueCat customer ID (app_user_id)
  const users = await getUserById(Number(app_user_id));

  if (users.length === 0) {
    console.error('User not found for RevenueCat app_user_id:', app_user_id);
    return;
  }

  const user = users[0];

  // Handle different event types
  switch (type) {
    case 'INITIAL_PURCHASE':
    case 'RENEWAL':
    case 'PRODUCT_CHANGE':
      await handleSubscriptionActive(user.id, entitlements, product_id);
      break;
      
    case 'CANCELLATION':
    case 'EXPIRATION':
    case 'BILLING_ISSUE':
      await handleSubscriptionInactive(user.id);
      break;
      
    default:
      console.log(`Unhandled RevenueCat event type: ${type}`);
  }
}

async function handleSubscriptionActive(
  userId: number,
  entitlements?: Record<string, RevenueCatEntitlement>,
  productId?: string
) {
  // Determine plan based on product ID or entitlements
  let plan = 'free';
  
  if (productId) {
    // Map RevenueCat product IDs to internal plan names
    if (productId.toLowerCase().includes('monthly')) {
      plan = 'pro';
    }
  } else if (entitlements) {
    // Check for active entitlements
    const activeEntitlements = Object.keys(entitlements).filter(key => {
      const entitlement = entitlements[key];
      const expiresDate = entitlement.expires_date ? new Date(entitlement.expires_date) : null;
      return !expiresDate || expiresDate > new Date();
    });

    if (activeEntitlements.length > 0) {
      const entitlementKey = activeEntitlements[0];
      if (entitlementKey.toLowerCase().includes('pro')) {
        plan = 'pro';
      } else if (entitlementKey.toLowerCase().includes('plus')) {
        plan = 'plus';
      }
    }
  }

  // Update user subscription - only update the plan field as requested
  await updateUserSubscription(userId, {
    stripeCustomerId: null, // Keep Stripe fields null for RevenueCat users
    stripeSubscriptionId: null,
    stripeProductId: null,
    plan: plan
  });

  console.log(`Updated user ${userId} to plan: ${plan}`);
}

async function handleSubscriptionInactive(userId: number) {
  // Set user back to free plan
  await updateUserSubscription(userId, {
    stripeCustomerId: null,
    stripeSubscriptionId: null, 
    stripeProductId: null,
    plan: 'free'
  });

  console.log(`Updated user ${userId} to free plan`);
}
