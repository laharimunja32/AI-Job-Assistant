import { Link } from 'react-router-dom';
import { Mail } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function ForgotPasswordPage() {
  return (
    <div className="text-center">
      <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-900/30">
        <Mail className="h-7 w-7 text-brand-600" />
      </div>
      <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Forgot password?</h2>
      <p className="mt-2 text-sm text-slate-500">
        Password reset is not yet available via the API. This UI is prepared for a future backend endpoint.
        Contact your administrator or create a new account.
      </p>
      <Link to="/login" className="mt-8 inline-block">
        <Button variant="outline">Back to sign in</Button>
      </Link>
    </div>
  );
}
