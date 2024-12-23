'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Lock, Trash2, Loader2 } from 'lucide-react';
import { startTransition, useActionState } from 'react';
import { updatePassword, deleteAccount } from '@/app/(login)/actions';

type ActionState = {
  error?: string;
  success?: string;
};

export default function SecurityPage() {
  const [passwordState, passwordAction, isPasswordPending] = useActionState<
    ActionState,
    FormData
  >(updatePassword, { error: '', success: '' });

  const [deleteState, deleteAction, isDeletePending] = useActionState<
    ActionState,
    FormData
  >(deleteAccount, { error: '', success: '' });

  const handlePasswordSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();
    startTransition(() => {
      passwordAction(new FormData(event.currentTarget));
    });
  };

  const handleDeleteSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();
    startTransition(() => {
      deleteAction(new FormData(event.currentTarget));
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 md:p-12">
      <section className="w-full max-w-2xl text-white">
        <h1 className="text-3xl font-bold mb-8">Security Settings</h1>
        <div className="space-y-12">
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Update Password</h2>
            <form className="space-y-4" onSubmit={handlePasswordSubmit}>
              <div>
                <Label htmlFor="current-password" className="text-white/80">Current Password</Label>
                <Input
                  id="current-password"
                  name="currentPassword"
                  type="password"
                  autoComplete="current-password"
                  required
                  minLength={8}
                  maxLength={100}
                  className="bg-white/5 border-white/10 text-white"
                />
              </div>
              <div>
                <Label htmlFor="new-password" className="text-white/80">New Password</Label>
                <Input
                  id="new-password"
                  name="newPassword"
                  type="password"
                  autoComplete="new-password"
                  required
                  minLength={8}
                  maxLength={100}
                  className="bg-white/5 border-white/10 text-white"
                />
              </div>
              <div>
                <Label htmlFor="confirm-password" className="text-white/80">Confirm New Password</Label>
                <Input
                  id="confirm-password"
                  name="confirmPassword"
                  type="password"
                  required
                  minLength={8}
                  maxLength={100}
                  className="bg-white/5 border-white/10 text-white"
                />
              </div>
              {passwordState.error && (
                <p className="text-red-400 text-sm">{passwordState.error}</p>
              )}
              {passwordState.success && (
                <p className="text-green-400 text-sm">{passwordState.success}</p>
              )}
              <Button
                type="submit"
                className="w-full bg-cyan-500 hover:bg-cyan-600 text-white transition-colors duration-200"
                disabled={isPasswordPending}
              >
                {isPasswordPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Updating...
                  </>
                ) : (
                  <>
                    <Lock className="mr-2 h-4 w-4" />
                    Update Password
                  </>
                )}
              </Button>
            </form>
          </div>

          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Delete Account</h2>
            <p className="text-sm text-white/60 mb-4">
              Account deletion is non-reversible. Please proceed with caution.
            </p>
            <form onSubmit={handleDeleteSubmit} className="space-y-4">
              <div>
                <Label htmlFor="delete-password" className="text-white/80">Confirm Password</Label>
                <Input
                  id="delete-password"
                  name="password"
                  type="password"
                  required
                  minLength={8}
                  maxLength={100}
                  className="bg-white/5 border-white/10 text-white"
                />
              </div>
              {deleteState.error && (
                <p className="text-red-400 text-sm">{deleteState.error}</p>
              )}
              <Button
                type="submit"
                className="w-full bg-red-500 hover:bg-red-600 text-white transition-colors duration-200"
                disabled={isDeletePending}
              >
                {isDeletePending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete Account
                  </>
                )}
              </Button>
            </form>
          </div>
        </div>
      </section>
    </div>
  );
}

