import { redirect } from 'next/navigation';
import { EditKeywords } from './keywords';
import { getUser } from '@/lib/db/queries';
import { getKeywords, getName } from '@/lib/actions';


export default async function SettingsPage() {
  const user = await getUser();

  if (!user) {
    redirect('/sign-in');
  }

  const name = await getName();
  const interests = await getKeywords();


  return <EditKeywords name = {name} interests = {interests}/>;
}
