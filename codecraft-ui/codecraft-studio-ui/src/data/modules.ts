import { Module } from '@/types/codecraft';

export const modules: Module[] = [
  {
    id: 'frontend-to-backend',
    name: 'Frontend to Backend',
    description: 'Generate Express.js backend from React frontend code',
    icon: '🔄',
    acceptsFiles: true,
    fileTypes: ['.jsx', '.tsx', '.js', '.ts'],
  },
  {
    id: 'backend-to-frontend',
    name: 'Backend to Frontend',
    description: 'Generate React frontend from Express.js backend code',
    icon: '🎨',
    acceptsFiles: true,
    fileTypes: ['.js', '.ts'],
  },
  {
    id: 'erd-to-backend',
    name: 'ERD to Backend',
    description: 'Generate database models and APIs from ERD diagrams',
    icon: '🗄️',
    acceptsFiles: true,
    fileTypes: ['.png', '.jpg', '.jpeg', '.svg', '.json'],
  },
  {
    id: 'prompt-to-backend',
    name: 'Prompt to Backend',
    description: 'Generate complete Express.js backend from natural language',
    icon: '⚡',
    acceptsFiles: false,
  },
  {
    id: 'prompt-to-frontend',
    name: 'Prompt to Frontend',
    description: 'Generate React frontend components from natural language',
    icon: '✨',
    acceptsFiles: false,
  },
  {
    id: 'ui-to-frontend',
    name: 'UI to Frontend',
    description: 'Convert UI designs/screenshots to React components',
    icon: '🖼️',
    acceptsFiles: true,
    fileTypes: ['.png', '.jpg', '.jpeg', '.webp', '.figma'],
  },
];
