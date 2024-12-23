'use client';

import { Button } from '@/components/ui/button';
import { ArrowRight, Loader2 } from 'lucide-react';
import { useFormStatus } from 'react-dom';
import { redirect } from 'next/navigation';


export function SubmitButton({ freePlan }: { freePlan?: boolean }) {
  const { pending } = useFormStatus();


  const handleClick = () => {
    if (freePlan) {
      // add free plan to user data
      redirect('/dashboard');
    }
  };

  return (
    <Button
      type="submit"
      disabled={pending}
      onClick={freePlan ? handleClick : undefined}
      className="w-full bg-white text-black border border-gray-200 rounded-full flex items-center justify-center hover:bg-cyan-100 transition duration-300"
    >
      {pending ? (
      <>
        <Loader2 className="animate-spin mr-2 h-4 w-4" />
        Loading...
      </>
      ) : (
      <>
        {freePlan ? "Continue" : "Upgrade"}
        <ArrowRight className="ml-2 h-4 w-4" />
      </>
      )}
    </Button>
  );
}
