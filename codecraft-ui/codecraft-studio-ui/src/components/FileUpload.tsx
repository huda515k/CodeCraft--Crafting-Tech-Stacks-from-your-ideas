import { useCallback, useState } from 'react';
import { Plus, X, FileCode, Image as ImageIcon, File } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { UploadedFile } from '@/types/codecraft';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  files: UploadedFile[];
  onFilesChange: (files: UploadedFile[]) => void;
  acceptedTypes?: string[];
  maxFiles?: number;
}

export function FileUpload({ 
  files, 
  onFilesChange, 
  acceptedTypes = ['*'],
  maxFiles = 10 
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    processFiles(droppedFiles);
  }, [files, maxFiles]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      processFiles(selectedFiles);
    }
  };

  const processFiles = (newFiles: File[]) => {
    const remainingSlots = maxFiles - files.length;
    const filesToAdd = newFiles.slice(0, remainingSlots);

    const uploadedFiles: UploadedFile[] = filesToAdd.map(file => ({
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: file.name,
      type: file.type,
      size: file.size,
      file,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
    }));

    onFilesChange([...files, ...uploadedFiles]);
  };

  const removeFile = (id: string) => {
    const file = files.find(f => f.id === id);
    if (file?.preview) {
      URL.revokeObjectURL(file.preview);
    }
    onFilesChange(files.filter(f => f.id !== id));
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <ImageIcon className="w-4 h-4" />;
    if (type.includes('javascript') || type.includes('typescript') || type.includes('json')) {
      return <FileCode className="w-4 h-4" />;
    }
    return <File className="w-4 h-4" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-3">
      {/* File List */}
      {files.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {files.map((file) => (
            <div
              key={file.id}
              className="flex items-center gap-2 bg-secondary/50 rounded-lg px-3 py-2 group animate-fade-in"
            >
              {file.preview ? (
                <img 
                  src={file.preview} 
                  alt={file.name}
                  className="w-8 h-8 rounded object-cover"
                />
              ) : (
                <div className="w-8 h-8 rounded bg-secondary flex items-center justify-center text-muted-foreground">
                  {getFileIcon(file.type)}
                </div>
              )}
              <div className="flex flex-col">
                <span className="text-sm font-medium truncate max-w-[120px]">{file.name}</span>
                <span className="text-xs text-muted-foreground">{formatFileSize(file.size)}</span>
              </div>
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={() => removeFile(file.id)}
                className="opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-3.5 h-3.5" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Drop Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={cn(
          "file-upload-zone flex items-center justify-center gap-3 cursor-pointer",
          isDragging && "dragging"
        )}
      >
        <input
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="flex items-center gap-3 cursor-pointer">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
            <Plus className="w-5 h-5 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium">Add files</p>
            <p className="text-xs text-muted-foreground">
              Drag & drop or click to browse
            </p>
          </div>
        </label>
      </div>
    </div>
  );
}
