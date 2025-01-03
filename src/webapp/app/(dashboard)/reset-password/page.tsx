'use client';

import { useState, useActionState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react';
import { resetPassword } from '@/lib/actions';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ActionState } from '@/lib/auth/middleware';


export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const [state, formAction, pending] = useActionState<ActionState, FormData>(resetPassword, {success: '', error: ''});
  const [newPassword, setNewPassword] = useState('');

  if (!token) {
    return <div>Invalid or missing token. Please try the password reset process again.</div>;
  }

  return (
    <div className="min-h-[100dvh] flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 bg-amber-100/40">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-black">
          Reset Your Password
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        {state?.success && (
          <Alert className="mb-6 bg-gray-800 text-white font-bold text-center">
            <AlertDescription>{state.success}</AlertDescription>
          </Alert>
        )}
        <form className="space-y-6" action={formAction}>
          <input type="hidden" name="token" value={token} />
          <div>
            <Label
              htmlFor="newPassword"
              className="block text-sm font-medium text-gray-800"
            >
              New Password
            </Label>
            <div className="mt-1">
              <Input
                id="newPassword"
                name="newPassword"
                type="password"
                required
                minLength={8}
                maxLength={100}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="appearance-none rounded-full relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-300 text-black bg-gray-300 focus:outline-none focus:ring-black focus:border-gray-800 focus:z-10 sm:text-sm"
                placeholder="Enter your new password"
              />
            </div>
          </div>

          {state?.error && (
            <div className="text-red-500 text-sm">{state.error}</div>
          )}

          <div>
            <Button
              type="submit"
              className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-full shadow-sm text-sm font-medium text-white bg-gray-800 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black"
              disabled={pending}
            >
              {pending ? (
                <>
                  <Loader2 className="animate-spin mr-2 h-4 w-4" />
                  Resetting...
                </>
              ) : (
                'Reset Password'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
