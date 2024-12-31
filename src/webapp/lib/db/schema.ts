import { pgTable, serial, text, varchar, jsonb, integer, boolean, timestamp } from 'drizzle-orm/pg-core';

// Define the user table schema
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  passwordHash: text('password_hash').notNull(),
  name: varchar('name', { length: 255 }),
  deliveryDay: integer('deliveryDay').notNull().default(1),
  delivered: timestamp('delivered').notNull().default(new Date(0)),
  active: boolean('active').notNull().default(true),
  keywords: jsonb('keywords').notNull(),
  role: varchar('role', { length: 20 }).notNull().default('Other'),
  occupation: varchar('occupation', { length: 255 }),
  stripeCustomerId: text('stripe_customer_id').unique(),
  stripeSubscriptionId: text('stripe_subscription_id').unique(),
  stripeProductId: text('stripe_product_id'),
  plan: varchar('plan', { length: 50 }).notNull().default('free'),
  notes: jsonb('note').notNull().default([]),
  activeNotes: jsonb('active_notes').notNull().default([]),
  episode: integer('episode').notNull().default(0),
  // insight will use a second table to store pdfs
});

// Email table for newsletter
export const emails = pgTable('emails', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  subscribed: boolean('subscribed').notNull().default(true),
});


export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;

export enum ActivityType {
  SIGN_UP = 'SIGN_UP',
  SIGN_IN = 'SIGN_IN',
  SIGN_OUT = 'SIGN_OUT',
  UPDATE_PASSWORD = 'UPDATE_PASSWORD',
  DELETE_ACCOUNT = 'DELETE_ACCOUNT',
  UPDATE_ACCOUNT = 'UPDATE_ACCOUNT',
}