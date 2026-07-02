import { Outlet, Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

export function AuthLayout() {
  return (
    <div className="flex min-h-screen">
      <div className="hidden w-1/2 flex-col justify-between bg-gradient-to-br from-brand-600 to-brand-900 p-12 text-white lg:flex">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-white/20 p-2">
            <Sparkles className="h-6 w-6" />
          </div>
          <span className="text-xl font-bold">AI Job Assistant</span>
        </div>
        <div>
          <h1 className="text-4xl font-bold leading-tight">
            Your personalized job feed, powered by AI
          </h1>
          <p className="mt-4 text-lg text-brand-100">
            Discover matched jobs, walk-in drives, and career opportunities — automatically curated for you.
          </p>
        </div>
        <p className="text-sm text-brand-200">© {new Date().getFullYear()} AI Job Application Assistant</p>
      </div>
      <div className="flex w-full flex-col justify-center px-6 py-12 lg:w-1/2 lg:px-16">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-8 flex items-center gap-2 lg:hidden">
            <Sparkles className="h-6 w-6 text-brand-600" />
            <span className="text-lg font-bold">AI Job Assistant</span>
          </div>
          <Outlet />
          <p className="mt-8 text-center text-sm text-slate-500">
            <Link to="/" className="text-brand-600 hover:underline">
              Back to home
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
