'use client';
import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { verifyEmail } from '@/lib/actions';

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  useEffect(() => {
    if (token) {
      verifyEmail( token );
    }
  }, [token]);

  return null; // This component doesn't render anything
}

