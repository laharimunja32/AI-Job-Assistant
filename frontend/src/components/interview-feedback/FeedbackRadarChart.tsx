import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { Card } from '@/components/ui';
import type { InterviewFeedbackDetail } from '@/types';

interface FeedbackRadarChartProps {
  feedback: Pick<
    InterviewFeedbackDetail,
    | 'technical_score'
    | 'communication_score'
    | 'behavioral_score'
    | 'grammar_score'
    | 'clarity_score'
    | 'problem_solving_score'
    | 'readiness_score'
    | 'confidence_score'
  >;
  title?: string;
}

export function FeedbackRadarChart({ feedback, title = 'Skill Radar' }: FeedbackRadarChartProps) {
  const data = [
    { skill: 'Technical', score: feedback.technical_score ?? 0 },
    { skill: 'Communication', score: feedback.communication_score ?? 0 },
    { skill: 'Behavioral', score: feedback.behavioral_score ?? 0 },
    { skill: 'Grammar', score: feedback.grammar_score ?? 0 },
    { skill: 'Clarity', score: feedback.clarity_score ?? 0 },
    { skill: 'Problem Solving', score: feedback.problem_solving_score ?? 0 },
    { skill: 'Readiness', score: feedback.readiness_score ?? 0 },
    { skill: 'Confidence', score: feedback.confidence_score ?? 0 },
  ].filter((item) => item.score > 0);

  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</h3>
      {data.length === 0 ? (
        <p className="text-sm text-slate-500">No skill scores available for this session.</p>
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={data}>
              <PolarGrid />
              <PolarAngleAxis dataKey="skill" tick={{ fontSize: 11 }} />
              <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Radar dataKey="score" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.35} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
