'use client';

import { useActionState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react';
import { forgotPassword } from '@/lib/actions';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ActionState } from '@/lib/auth/middleware';


export default function ForgotPasswordForm() {
  const [state, formAction, pending] = useActionState<ActionState, FormData>(forgotPassword, {success: '', error: ''});

  return (
    <div className="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 className="mt-6 text-center text-3xl font-extrabold text-black">
        Forgot your password?
      </h2>
      <p className="mt-2 text-center text-sm text-gray-600">
        Enter your email address and we'll send you a link to reset your password.
      </p>
      {state?.success && (
        <Alert className="mt-6 bg-gray-800 text-white font-bold text-center">
          <AlertDescription>{state.success}</AlertDescription>
        </Alert>
      )}
      <form className="mt-8 space-y-6" action={formAction}>
        <div>
          <Label
            htmlFor="email"
            className="block text-sm font-medium text-gray-800"
          >
            Email
          </Label>
          <div className="mt-1">
            <Input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              maxLength={50}
              className="appearance-none rounded-full relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-300 text-black bg-gray-300 focus:outline-none focus:ring-black focus:border-gray-800 focus:z-10 sm:text-sm"
              placeholder="Enter your email"
            />
          </div>
        </div>

        {state?.error && (
          <div className="text-red-500 text-sm">{state.error}</div>
        )}

        <div>
          <Button
            type="submit"
            className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-full shadow-sm text-sm font-medium text-white bg-gray-800 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-200"
            disabled={pending}
          >
            {pending ? (
              <>
                <Loader2 className="animate-spin mr-2 h-4 w-4" />
                Sending...
              </>
            ) : (
              'Send reset link'
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}

