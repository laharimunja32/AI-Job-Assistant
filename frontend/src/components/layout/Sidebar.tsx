import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Briefcase,
  Users,
  FileText,
  User,
  ClipboardList,
  Bell,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Globe,
  ListChecks,
  Upload,
  ShieldCheck,
  Mail,
  ClipboardCheck,
  CalendarClock,
  Timer,
  AlarmClock,
  MessageSquare,
} from 'lucide-react';
import { useUIStore } from '@/store';
import { cn } from '@/utils';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/jobs', label: 'Jobs', icon: Briefcase },
  { to: '/walk-ins', label: 'Walk-ins', icon: Users },
  { to: '/resumes', label: 'Resumes', icon: FileText },
  { to: '/profile', label: 'Profile', icon: User },
  { to: '/applications', label: 'Applications', icon: ClipboardList },
  { to: '/notifications', label: 'Notifications', icon: Bell },
  { to: '/settings', label: 'Settings', icon: Settings },
  { to: '/browser-automation', label: 'Browser Automation', icon: Globe },
  { to: '/form-assistant', label: 'Form Assistant', icon: ListChecks },
  { to: '/upload-assistant', label: 'Upload Assistant', icon: Upload },
  { to: '/review-assistant', label: 'Guided Review', icon: ShieldCheck },
  { to: '/recruitment-emails', label: 'Recruitment Emails', icon: Mail },
  { to: '/assessments', label: 'Assessments', icon: ClipboardCheck },
  { to: '/interview-prep/history', label: 'Interview Prep', icon: MessageSquare },
  { to: '/interviews', label: 'Interviews', icon: CalendarClock },
  { to: '/timeline', label: 'Timeline', icon: Timer },
  { to: '/reminders', label: 'Reminders', icon: AlarmClock },
];

export function Sidebar() {
  const location = useLocation();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-30 flex h-full flex-col border-r border-slate-200 bg-white transition-all duration-300 dark:border-slate-800 dark:bg-slate-900',
        sidebarOpen ? 'w-64' : 'w-[72px]',
      )}
    >
      <div className="flex h-16 items-center gap-2 border-b border-slate-200 px-4 dark:border-slate-800">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-600 text-white">
          <Sparkles className="h-5 w-5" />
        </div>
        {sidebarOpen && (
          <div className="min-w-0">
            <p className="truncate text-sm font-bold text-slate-900 dark:text-slate-100">AI Job Assistant</p>
            <p className="truncate text-xs text-slate-500">Smart career platform</p>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-3 scrollbar-thin">
        {navItems.map(({ to, label, icon: Icon }) => {
          const active = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to);
          return (
            <Link
              key={to}
              to={to}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                active
                  ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300'
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800',
              )}
              title={!sidebarOpen ? label : undefined}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {sidebarOpen && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>

      <button
        onClick={toggleSidebar}
        className="m-3 flex items-center justify-center rounded-lg border border-slate-200 p-2 text-slate-500 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
        aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
      >
        {sidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>
    </aside>
  );
}
