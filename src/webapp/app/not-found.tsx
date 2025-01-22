import Link from 'next/link';
import { CircleIcon } from 'lucide-react';
import Image from 'next/image';

export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-[100dvh] bg-amber-100/40">
      <div className="max-w-md space-y-8 p-4 text-center">
        <div className="flex justify-center">
          <Image 
            src="/logo.svg" 
            alt="Company Logo" 
            width={100}
            height={100}
          />
        </div>
        <h1 className="text-4xl font-bold text-black tracking-tight">
          Page Not Found
        </h1>
        <p className="text-base text-gray-700">
          Sorry! Looks like we sent you to the wrong place. 
        </p>
        <Link
          href="/"
          className="max-w-48 mx-auto flex justify-center py-2 px-4 border border-gray-300 rounded-full shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-600"
        >
          Back to Home
        </Link>
      </div>
    </div>
  );
}
