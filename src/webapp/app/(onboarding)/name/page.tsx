import { redirect } from 'next/navigation';
import { getUser } from '@/lib/db/queries';
import { NameOccupation } from './name';

export default async function Keywords() {
  const user = await getUser();
  if (!user) {
    redirect('/sign-in');
  }

  return (
    <div>
      <NameOccupation/>
    </div>
  );
}