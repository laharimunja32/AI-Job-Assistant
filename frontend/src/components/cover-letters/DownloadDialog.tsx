import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';

interface DownloadDialogProps {
  open: boolean;
  onClose: () => void;
  selectedFormat: 'pdf' | 'docx' | 'markdown' | 'html';
  onFormatChange: (format: 'pdf' | 'docx' | 'markdown' | 'html') => void;
  onDownload: () => void;
}

export function DownloadDialog({ open, onClose, selectedFormat, onFormatChange, onDownload }: DownloadDialogProps) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Download cover letter"
      footer={
        <>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={onDownload}>Download</Button>
        </>
      }
    >
      <div className="flex flex-wrap gap-2">
        {(['pdf', 'docx', 'markdown', 'html'] as const).map((fmt) => (
          <Button key={fmt} size="sm" variant={selectedFormat === fmt ? 'primary' : 'outline'} onClick={() => onFormatChange(fmt)}>
            {fmt.toUpperCase()}
          </Button>
        ))}
      </div>
    </Modal>
  );
}
