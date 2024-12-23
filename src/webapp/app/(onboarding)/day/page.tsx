import { redirect } from 'next/navigation';
import { getUser } from '@/lib/db/queries';
import { Delivery } from './delivery';

export default async function Day() {
  const user = await getUser();
  if (!user) {
    redirect('/sign-in');
  }

  return (
    <div>
      <Delivery />
    </div>
  );
}