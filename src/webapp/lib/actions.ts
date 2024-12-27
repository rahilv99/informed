'use server';

import { z } from 'zod';
import { eq } from 'drizzle-orm';
import { db } from '@/lib/db/drizzle';
import {
  User,
  users,
  type NewUser,
} from '@/lib/db/schema';
import { comparePasswords, hashPassword, setSession } from '@/lib/auth/session';
import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import { getUserByEmail, createUser, getUser, updateUser } from '@/lib/db/queries';
import {
  validatedAction,
  validatedActionWithUser,
} from '@/lib/auth/middleware';


const signInSchema = z.object({
  email: z.string().email().min(3).max(255),
  password: z.string().min(8).max(100),
});

export const signIn = validatedAction(signInSchema, async (data, formData) => {
  const { email, password } = data;

  const user = await getUserByEmail(email);

  if (!user) {
    return { error: 'Invalid email or password. Please try again.' };
  }

  const foundUser = user[0];

  const isPasswordValid = await comparePasswords(
    password,
    foundUser.passwordHash
  );

  if (!isPasswordValid) {
    return { error: 'Invalid email or password. Please try again.' };
  }

  await Promise.all([
    setSession(foundUser)
  ]);

  redirect('/dashboard/pulse');
});


const signUpSchema = z.object({
  email: z.string().email().min(3).max(255),
  password: z.string().min(8).max(100),
});

export const signUp = validatedAction(signUpSchema, async (data) => {
  const { email, password } = data;

  // Check if user already exists
  const existingUser = await getUserByEmail(email);

  if (existingUser.length > 0) {
    throw new Error('User already exists');
  }

  const passwordHash = await hashPassword(password);

  // Create new user
  const newUser: NewUser = {
    email,
    passwordHash,
    name: '',
    deliveryDay: 0,
    keywords: [], // Initialize empty
    role: 'Other',
    stripeCustomerId: null,
    stripeSubscriptionId: null,
    stripeProductId: null,
    plan: 'free',
  };

  const createdUser = await createUser(newUser);


  await Promise.all([
    setSession(createdUser[0]),
  ]);

  redirect('/identity');
});


export async function signOut() {
  const user = (await getUser()) as User;
  (await cookies()).delete('session');

  redirect('/');
}

export async function updatePassword(formData: { currentPassword: string; newPassword: string }) {

  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  const isPasswordValid = await comparePasswords(
    formData.currentPassword,
    user.passwordHash
  );

  if (!isPasswordValid) {
    return { error: 'Current password is incorrect.' };
  }

  if (formData.currentPassword === formData.newPassword) {
    return {
      error: 'New password must be different from the current password.',
    };
  }

  const newPasswordHash = await hashPassword(formData.newPassword);
  await updateUser(user.id, {passwordHash: newPasswordHash });

  return { success: 'Password updated successfully.' };
}

const deleteAccountSchema = z.object({
  password: z.string().min(8).max(100),
});

export async function deleteAccount() {
  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  await db.delete(users).where(eq(users.id, user.id));

  await signOut();
}

export async function updateEmail(user_input: string) {

  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  // Update the user's email in the database
  await updateUser(user.id, { email: user_input });

  return { success: true, message: 'Email updated successfully' };
}


export async function updateUserRole(designations: string[]) {

  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  // Combine selected roles into a comma-separated string
  const roleString = designations.join(',');

  // Update the user's position
  await updateUser(user.id, {role: roleString});

  return { success: true, message: 'Roles updated successfully' };
}


export async function submitInterests(user_input: string) {
  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }
  // parse the keywords comma separated string into an array
  const keys = user_input.split(',').map((word) => word.trim());

  // Update the user's keywords in the database
  await updateUser(user.id, { keywords: keys });

  return { success: true, message: 'Keywords updated successfully' };
}

export async function updateInterests(keywords: string[]) {
  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  // Update the user's keywords in the database
  await updateUser(user.id, { keywords: keywords });

  return { success: true, message: 'Keywords updated successfully' };
}


export async function submitDay(day: number) {
  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  // Update the user's keywords in the database
  await updateUser(user.id, { deliveryDay: day });

  return { success: true, message: 'Keywords updated successfully' };
}

export async function getKeywords(): Promise<string[]> {
  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  const keywords = user.keywords;

  if (Array.isArray(keywords)) {
    return keywords; 
  } else {
    throw new Error('Error parsing jsonb');
  }
}

export async function getDay(): Promise<number> {
  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  return user.deliveryDay;
}

export async function getName(): Promise<string> {
  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  if (user.name) {
    return user.name;
  } else {
    return '';
  }
}

export async function getDeliveryStatus(): Promise<boolean> {
  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  return user.delivered;
}

export async function getAccountStatus(): Promise<boolean> {
  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  return user.active;
}

export async function setAccountStatus(status: boolean) {
  const user = await getUser();
  if (!user) {
    throw new Error('User is not authenticated');
  }

  await updateUser(user.id, { active: status });

  return { success: true, message: 'Account status updated successfully' };
}


/*  THIS IS HOW YOU UPDATE DB
const updateAccountSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  email: z.string().email('Invalid email address'),
});

export const updateAccount = validatedActionWithUser(
  updateAccountSchema,
  async (data, _, user) => {
    const { name, email } = data;
    const userWithTeam = await getUserWithTeam(user.id);

    await Promise.all([
      db.update(users).set({ name, email }).where(eq(users.id, user.id)),
      logActivity(userWithTeam?.teamId, user.id, ActivityType.UPDATE_ACCOUNT),
    ]);

    return { success: 'Account updated successfully.' };
  }
);
*/