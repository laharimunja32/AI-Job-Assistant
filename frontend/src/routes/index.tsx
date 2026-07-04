import { lazy, Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '@/layouts/AppLayout';
import { AuthLayout } from '@/layouts/AuthLayout';
import { ProtectedRoute, PublicRoute } from './ProtectedRoute';
import { PageLoader } from '@/components/ui/Loader';

const DashboardPage = lazy(() => import('@/pages/dashboard/DashboardPage'));
const LoginPage = lazy(() => import('@/pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('@/pages/auth/RegisterPage'));
const ForgotPasswordPage = lazy(() => import('@/pages/auth/ForgotPasswordPage'));
const JobsPage = lazy(() => import('@/pages/jobs/JobsPage'));
const JobDetailPage = lazy(() => import('@/pages/jobs/JobDetailPage'));
const WalkInsPage = lazy(() => import('@/pages/walk-ins/WalkInsPage'));
const WalkInDetailPage = lazy(() => import('@/pages/walk-ins/WalkInDetailPage'));
const ResumesPage = lazy(() => import('@/pages/resumes/ResumesPage'));
const ResumeDetailPage = lazy(() => import('@/pages/resumes/ResumeDetailPage'));
const ResumeOptimizerPage = lazy(() => import('@/pages/resume-optimizer/ResumeOptimizerPage'));
const ResumeOptimizationHistoryPage = lazy(() => import('@/pages/resume-optimizer/ResumeOptimizationHistoryPage'));
const ResumeOptimizationDetailPage = lazy(() => import('@/pages/resume-optimizer/ResumeOptimizationDetailPage'));
const ProfilePage = lazy(() => import('@/pages/profile/ProfilePage'));
const ApplicationsPage = lazy(() => import('@/pages/applications/ApplicationsPage'));
const NotificationsPage = lazy(() => import('@/pages/notifications/NotificationsPage'));
const SettingsPage = lazy(() => import('@/pages/settings/SettingsPage'));
const BrowserAutomationPage = lazy(() => import('@/pages/browser/BrowserAutomationPage'));
const FormAssistantPage = lazy(() => import('@/pages/browser/FormAssistantPage'));
const UploadAssistantPage = lazy(() => import('@/pages/browser/UploadAssistantPage'));
const ReviewAssistantPage = lazy(() => import('@/pages/browser/ReviewAssistantPage'));
const RecruitmentEmailsPage = lazy(() => import('@/pages/recruitment/RecruitmentEmailsPage'));
const AssessmentsPage = lazy(() => import('@/pages/recruitment/AssessmentsPage'));
const InterviewsPage = lazy(() => import('@/pages/recruitment/InterviewsPage'));
const InterviewPreparationPage = lazy(() => import('@/pages/interviews/InterviewPreparationPage'));
const InterviewPracticePage = lazy(() => import('@/pages/interviews/InterviewPracticePage'));
const InterviewFeedbackPage = lazy(() => import('@/pages/interviews/InterviewFeedbackPage'));
const InterviewHistoryPage = lazy(() => import('@/pages/interviews/InterviewHistoryPage'));
const TimelinePage = lazy(() => import('@/pages/recruitment/TimelinePage'));
const RemindersPage = lazy(() => import('@/pages/recruitment/RemindersPage'));

function Lazy({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<PageLoader />}>{children}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Lazy><DashboardPage /></Lazy> },
      { path: 'jobs', element: <Lazy><JobsPage /></Lazy> },
      { path: 'jobs/:id', element: <Lazy><JobDetailPage /></Lazy> },
      { path: 'walk-ins', element: <Lazy><WalkInsPage /></Lazy> },
      { path: 'walk-ins/:id', element: <Lazy><WalkInDetailPage /></Lazy> },
      { path: 'resumes', element: <Lazy><ResumesPage /></Lazy> },
      { path: 'resumes/:id', element: <Lazy><ResumeDetailPage /></Lazy> },
      { path: 'resume-optimizer', element: <Lazy><ResumeOptimizerPage /></Lazy> },
      { path: 'resume-optimizer/history', element: <Lazy><ResumeOptimizationHistoryPage /></Lazy> },
      { path: 'resume-optimizer/:id', element: <Lazy><ResumeOptimizationDetailPage /></Lazy> },
      { path: 'profile', element: <Lazy><ProfilePage /></Lazy> },
      { path: 'applications', element: <Lazy><ApplicationsPage /></Lazy> },
      { path: 'notifications', element: <Lazy><NotificationsPage /></Lazy> },
      { path: 'settings', element: <Lazy><SettingsPage /></Lazy> },
      { path: 'browser-automation', element: <Lazy><BrowserAutomationPage /></Lazy> },
      { path: 'form-assistant', element: <Lazy><FormAssistantPage /></Lazy> },
      { path: 'upload-assistant', element: <Lazy><UploadAssistantPage /></Lazy> },
      { path: 'review-assistant', element: <Lazy><ReviewAssistantPage /></Lazy> },
      { path: 'recruitment-emails', element: <Lazy><RecruitmentEmailsPage /></Lazy> },
      { path: 'assessments', element: <Lazy><AssessmentsPage /></Lazy> },
      { path: 'interviews', element: <Lazy><InterviewsPage /></Lazy> },
      { path: 'interview-prep/history', element: <Lazy><InterviewHistoryPage /></Lazy> },
      { path: 'interview-prep/:preparationId', element: <Lazy><InterviewPreparationPage /></Lazy> },
      { path: 'interview-prep/:preparationId/practice', element: <Lazy><InterviewPracticePage /></Lazy> },
      { path: 'interview-prep/:preparationId/feedback', element: <Lazy><InterviewFeedbackPage /></Lazy> },
      { path: 'timeline', element: <Lazy><TimelinePage /></Lazy> },
      { path: 'reminders', element: <Lazy><RemindersPage /></Lazy> },
    ],
  },
  {
    element: <AuthLayout />,
    children: [
      {
        path: 'login',
        element: (
          <PublicRoute>
            <Lazy><LoginPage /></Lazy>
          </PublicRoute>
        ),
      },
      {
        path: 'register',
        element: (
          <PublicRoute>
            <Lazy><RegisterPage /></Lazy>
          </PublicRoute>
        ),
      },
      {
        path: 'forgot-password',
        element: (
          <PublicRoute>
            <Lazy><ForgotPasswordPage /></Lazy>
          </PublicRoute>
        ),
      },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
]);
