import { redirect } from 'next/navigation';
import { getUser } from '@/lib/db/queries';
import { Interests } from './interests';
import { getRoleForUser } from '@/lib/db/queries';

export default async function Keywords() {
  const user = await getUser();
  if (!user) {
    redirect('/sign-in');
  }
  // get role from user
    const role = await getRoleForUser(user.id);

    if (!role) {
        throw new Error('Role not found');
      }

  return (
    <div>
      <Interests role = { role as "researcher" | "student" | "clinician" | "other" }/>
    </div>
  );
}