import { handleRevenueCatSubscriptionChange } from '@/lib/payments/revenuecat';
import { NextRequest, NextResponse } from 'next/server';
import type { RevenueCatWebhookEvent } from '@/lib/payments/revenuecat';

//const webhookSecret = process.env.REVENUECAT_WEBHOOK_SECRET!;

export async function POST(request: NextRequest) {
  try {
    const payload = await request.text();
    
    // Verify webhook authorization header if secret is provided
    // if (webhookSecret) {
    //   const authHeader = request.headers.get('authorization');
    //   if (!authHeader || authHeader !== webhookSecret) {
    //   console.error('RevenueCat webhook authorization failed');
    //   return NextResponse.json(
    //     { error: 'Webhook authorization failed' },
    //     { status: 401 }
    //   );
    //   }
    // }

    console.log('Received RevenueCat event:', payload);
    // Parse the webhook event
    let event: RevenueCatWebhookEvent;
    try {
      event = JSON.parse(payload);
    } catch (err) {
      console.error('Failed to parse RevenueCat webhook payload:', err);
      return NextResponse.json(
        { error: 'Invalid JSON payload' },
        { status: 400 }
      );
    }

    // Validate required fields
    if (!event.event || !event.event.type || !event.event.app_user_id) {
      console.error('Missing required fields in RevenueCat webhook event');
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Handle the subscription change
    await handleRevenueCatSubscriptionChange(event);

    return NextResponse.json({ received: true }, { status: 200 });
  } catch (err) {
    console.error('Error processing RevenueCat webhook:', err);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
