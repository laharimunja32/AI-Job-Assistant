import { Download } from 'lucide-react';
import { Button } from '@/components/ui';

interface DownloadButtonsProps {
  onDownload: (format: 'pdf' | 'docx') => void;
  downloading?: 'pdf' | 'docx' | null;
  disabled?: boolean;
}

export function DownloadButtons({ onDownload, downloading, disabled }: DownloadButtonsProps) {
  return (
    <div className="flex gap-2">
      <Button variant="outline" onClick={() => onDownload('pdf')} disabled={disabled || downloading === 'pdf'} className="gap-2">
        <Download className="h-4 w-4" />
        {downloading === 'pdf' ? 'Downloading...' : 'PDF'}
      </Button>
      <Button variant="outline" onClick={() => onDownload('docx')} disabled={disabled || downloading === 'docx'} className="gap-2">
        <Download className="h-4 w-4" />
        {downloading === 'docx' ? 'Downloading...' : 'DOCX'}
      </Button>
    </div>
  );
}
