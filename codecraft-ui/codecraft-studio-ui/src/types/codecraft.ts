export type ModuleType = 
  | 'frontend-to-backend'
  | 'backend-to-frontend'
  | 'erd-to-backend'
  | 'prompt-to-backend'
  | 'prompt-to-frontend'
  | 'ui-to-frontend';

export interface Module {
  id: ModuleType;
  name: string;
  description: string;
  icon: string;
  acceptsFiles: boolean;
  fileTypes?: string[];
}

export interface UploadedFile {
  id: string;
  name: string;
  type: string;
  size: number;
  preview?: string;
  file: File;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  files?: UploadedFile[];
}

export interface GeneratedCode {
  filename: string;
  language: string;
  content: string;
}

export interface UserProfile {
  name: string;
  email: string;
  avatar?: string;
}
