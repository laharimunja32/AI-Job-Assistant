import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AnswerEditor } from '@/components/interviews/AnswerEditor';
import { InterviewProgress } from '@/components/interviews/InterviewProgress';
import { QuestionCard } from '@/components/interviews/QuestionCard';
import { Button, EmptyState, PageLoader } from '@/components/ui';
import { useFinishInterview, useInterviewPreparation, useStartInterview, useSubmitInterviewAnswer } from '@/hooks';
import { useToast } from '@/contexts/ToastContext';
import type { InterviewQuestion, InterviewSessionProgress } from '@/types';

export default function InterviewPracticePage() {
  const { preparationId } = useParams<{ preparationId: string }>();
  const id = Number(preparationId);
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { data: preparation, isLoading } = useInterviewPreparation(id, id > 0);
  const startMutation = useStartInterview();
  const answerMutation = useSubmitInterviewAnswer();
  const finishMutation = useFinishInterview();

  const [currentQuestion, setCurrentQuestion] = useState<InterviewQuestion | null>(null);
  const [progress, setProgress] = useState<InterviewSessionProgress | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [started, setStarted] = useState(false);

  useEffect(() => {
    if (!id || started) return;
    startMutation.mutate(id, {
      onSuccess: ({ data }) => {
        setCurrentQuestion(data.current_question);
        setProgress(data.progress);
        setStarted(true);
      },
      onError: () => addToast('Unable to start practice session', 'error'),
    });
  }, [id, started, startMutation, addToast]);

  useEffect(() => {
    if (!started) return;
    const timer = window.setInterval(() => setElapsedSeconds((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, [started]);

  const questionNumber = useMemo(() => (progress ? progress.current_index + 1 : 1), [progress]);

  const handleSubmit = (answerText: string, timeSpentSeconds: number) => {
    answerMutation.mutate(
      { id, answer_text: answerText, time_spent_seconds: timeSpentSeconds },
      {
        onSuccess: ({ data }) => {
          setProgress(data.progress);
          setCurrentQuestion(data.next_question);
          if (!data.next_question) {
            addToast('All questions answered. Finish to get feedback.', 'success');
          }
        },
        onError: () => addToast('Failed to save answer', 'error'),
      },
    );
  };

  const handleFinish = () => {
    finishMutation.mutate(id, {
      onSuccess: () => {
        addToast('Interview practice completed', 'success');
        navigate(`/interview-prep/${id}/feedback`);
      },
      onError: () => addToast('Unable to finish session', 'error'),
    });
  };

  if (isLoading || startMutation.isPending) return <PageLoader />;
  if (!preparation) return <EmptyState title="Preparation not found" />;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Mock Interview</h1>
          <p className="text-sm text-slate-500">Answer one question at a time and save your progress.</p>
        </div>
        <Button variant="secondary" onClick={handleFinish} loading={finishMutation.isPending}>
          Finish Interview
        </Button>
      </div>

      {progress && <InterviewProgress progress={progress} elapsedSeconds={elapsedSeconds} />}

      {currentQuestion ? (
        <>
          <QuestionCard
            question={currentQuestion}
            questionNumber={questionNumber}
            totalQuestions={progress?.total_questions ?? preparation.questions.length}
          />
          <AnswerEditor onSubmit={handleSubmit} loading={answerMutation.isPending} />
        </>
      ) : (
        <div className="space-y-4 rounded-xl border border-slate-200 p-6 text-center dark:border-slate-700">
          <p className="text-slate-600 dark:text-slate-300">You have answered all questions.</p>
          <Button onClick={handleFinish} loading={finishMutation.isPending}>View Feedback</Button>
        </div>
      )}
    </div>
  );
}
