import { redirect } from 'next/navigation';
import { Activity } from './activity';
import { getUser } from '@/lib/db/queries';

export default async function SettingsPage() {
  const user = await getUser();

  if (!user) {
    redirect('/sign-in');
  }

  return <Activity />;
}
