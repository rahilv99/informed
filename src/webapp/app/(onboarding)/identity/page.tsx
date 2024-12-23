import { redirect } from 'next/navigation';
import { getUser } from '@/lib/db/queries';
import { Roles } from './roles';

export default async function Identity() {
  const user = await getUser();
  if (!user) {
    redirect('/sign-in');
  }

  return (
    <div>
      <Roles />
    </div>
  );
}