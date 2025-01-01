'use client';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { verifyEmail } from '@/lib/actions';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';

export default function VerifyEmailPage() {
    const [verificationStatus, setVerificationStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  useEffect(() => {
    if (token) {
      verifyEmail(token)
        .then((result) => {
          if (result.error) {
            setVerificationStatus('error');
          } else {
            setVerificationStatus('success');
          }
        })
        .catch(() => setVerificationStatus('error'));
    } else {
      setVerificationStatus('error');
    }
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <Card className="w-[350px]">
        <CardHeader>
          <CardTitle>Email Verification</CardTitle>
          <CardDescription>Verifying your email address</CardDescription>
        </CardHeader>
        <CardContent>
          {verificationStatus === 'verifying' && <p>Verifying your email...</p>}
          {verificationStatus === 'success' && (
            <>
              <p className="text-green-600 mb-4">Your email has been successfully verified!</p>
              <Button asChild>
                <a href="/dashboard/pulse">Go to Dashboard</a>
              </Button>
            </>
          )}
          {verificationStatus === 'error' && (
            <p className="text-red-600">There was an error verifying your email. The link may have expired. Please try signing in to receive a new verification email.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

