import { Badge, Card } from '@/components/ui';
import type { InterviewQuestion } from '@/types';

interface QuestionCardProps {
  question: InterviewQuestion;
  questionNumber: number;
  totalQuestions: number;
}

const categoryLabels: Record<string, string> = {
  company_specific: 'Company',
  hr: 'HR',
  behavioral: 'Behavioral',
  technical: 'Technical',
  project: 'Project',
  resume_based: 'Resume',
};

export function QuestionCard({ question, questionNumber, totalQuestions }: QuestionCardProps) {
  return (
    <Card className="p-5">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <Badge variant="default">
          Question {questionNumber} / {totalQuestions}
        </Badge>
        <Badge variant="info">{categoryLabels[question.category] ?? question.category}</Badge>
        <Badge variant={question.difficulty === 'hard' ? 'danger' : question.difficulty === 'easy' ? 'success' : 'warning'}>
          {question.difficulty}
        </Badge>
      </div>
      <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{question.question_text}</h2>
      {question.hints.length > 0 && (
        <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-600 dark:text-slate-300">
          {question.hints.map((hint) => (
            <li key={hint}>{hint}</li>
          ))}
        </ul>
      )}
    </Card>
  );
}
