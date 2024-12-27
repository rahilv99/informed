import { redirect } from 'next/navigation';
import { getUser } from '@/lib/db/queries';
import { Interests } from './interests';

export default async function Keywords() {
  const user = await getUser();
  if (!user) {
    redirect('/sign-in');
  }

  return (
    <div>
      <Interests/>
    </div>
  );
}