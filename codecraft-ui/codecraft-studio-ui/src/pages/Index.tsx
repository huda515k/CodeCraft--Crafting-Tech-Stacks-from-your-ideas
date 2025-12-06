import { useState, useCallback } from 'react';
import { Header } from '@/components/Header';
import { ChatInterface } from '@/components/ChatInterface';
import { CodePreview } from '@/components/CodePreview';
import { SettingsModal } from '@/components/SettingsModal';
import { Message, ModuleType, UploadedFile, GeneratedCode, UserProfile } from '@/types/codecraft';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/services/api';
import { extractZipFiles } from '@/lib/zipExtractor';

// Sample generated code for demo
const sampleCode: GeneratedCode[] = [
  {
    filename: 'App.jsx',
    language: 'jsx',
    content: `import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import './styles/global.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;`,
  },
  {
    filename: 'server.js',
    language: 'javascript',
    content: `const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date() });
});

// Start server
app.listen(PORT, () => {
  console.log(\`Server running on port \${PORT}\`);
});`,
  },
  {
    filename: 'package.json',
    language: 'json',
    content: `{
  "name": "codecraft-generated-app",
  "version": "1.0.0",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "client": "cd client && npm start"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.1.0"
  }
}`,
  },
];

export default function Index() {
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedModule, setSelectedModule] = useState<ModuleType | null>(null);
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode[]>([]);
  const [isCodeCollapsed, setIsCodeCollapsed] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserProfile>(() => {
    const saved = localStorage.getItem('codecraft-profile');
    if (saved) {
      return JSON.parse(saved);
    }
    return {
      name: 'Developer',
      email: 'dev@codecraft.ai',
    };
  });

  const extractFilesFromCode = (code: string): GeneratedCode[] => {
    const files: GeneratedCode[] = [];
    const filePattern = /```(\w+)?:?([^\n]+)\n([\s\S]*?)```/g;
    let match;
    
    while ((match = filePattern.exec(code)) !== null) {
      const [, language, filename, content] = match;
      if (filename && content) {
        files.push({
          filename: filename.trim(),
          language: language || 'text',
          content: content.trim(),
        });
      }
    }
    
    // If no files found, create a single file with the code
    if (files.length === 0 && code.trim()) {
      files.push({
        filename: 'generated.txt',
        language: 'text',
        content: code,
      });
    }
    
    return files;
  };

  const handleSendMessage = useCallback(async (content: string, files?: UploadedFile[]) => {
    if (!selectedModule) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
      files,
    };

    setMessages(prev => [...prev, userMessage]);
    setIsGenerating(true);
    setGeneratedCode([]);
    setProjectId(null);
    setDownloadUrl(null);

    try {
      let response: Response;
      let fullCode = '';

      if (selectedModule === 'prompt-to-backend') {
        // Handle streaming response
        response = await api.generatePromptToBackend(content);
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        if (!reader) throw new Error('Failed to get response stream');

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.trim() && line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === 'stream' && data.content) {
                  fullCode += data.content;
                  const files = extractFilesFromCode(fullCode);
                  setGeneratedCode(files);
                } else if (data.type === 'file') {
                  setGeneratedCode(prev => [...prev, {
                    filename: data.filename,
                    language: data.filename.split('.').pop() || 'text',
                    content: data.preview || '',
                  }]);
                } else if (data.type === 'complete') {
                  setProjectId(data.project_id);
                  setDownloadUrl(data.project_id);
                } else if (data.type === 'error') {
                  throw new Error(data.message);
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e);
              }
            }
          }
        }
      } else if (selectedModule === 'ui-to-frontend') {
        if (!files || files.length === 0) {
          throw new Error('Please upload at least one UI image');
        }
        const fileList = files.map(f => f.file);
        response = await api.generateUIToFrontend(fileList, content);
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setDownloadUrl(url);
        
        // Extract and display code from ZIP
        try {
          const extractedFiles = await extractZipFiles(blob);
          setGeneratedCode(extractedFiles.map(file => ({
            filename: file.filename,
            language: file.language,
            content: file.content,
          })));
        } catch (extractError) {
          console.error('Error extracting ZIP:', extractError);
          setGeneratedCode([{
            filename: 'project.zip',
            language: 'text',
            content: 'Frontend code generated successfully! Download the ZIP file to view all files.',
          }]);
        }
      } else if (selectedModule === 'frontend-to-backend') {
        if (!files || files.length === 0) {
          throw new Error('Please upload a frontend ZIP file');
        }
        // Use streaming endpoint for real-time preview
        response = await api.generateFrontendToBackend(files[0].file);
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullCode = '';

        if (!reader) throw new Error('Failed to get response stream');

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.trim() && line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === 'stream' && data.content) {
                  fullCode += data.content;
                  const files = extractFilesFromCode(fullCode);
                  setGeneratedCode(files);
                } else if (data.type === 'file') {
                  setGeneratedCode(prev => {
                    const existing = prev.findIndex(f => f.filename === data.filename);
                    if (existing >= 0) {
                      const updated = [...prev];
                      updated[existing] = {
                        filename: data.filename,
                        language: data.filename.split('.').pop() || 'text',
                        content: data.preview || '',
                      };
                      return updated;
                    } else {
                      return [...prev, {
                        filename: data.filename,
                        language: data.filename.split('.').pop() || 'text',
                        content: data.preview || '',
                      }];
                    }
                  });
                } else if (data.type === 'complete') {
                  setProjectId(data.project_id);
                  setDownloadUrl(data.project_id);
                } else if (data.type === 'error') {
                  throw new Error(data.message);
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e);
              }
            }
          }
        }
      } else if (selectedModule === 'erd-to-backend') {
        if (!files || files.length === 0) {
          throw new Error('Please upload an ERD image');
        }
        response = await api.generateERDToBackend(files[0].file, content);
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setDownloadUrl(url);
        
        // Extract and display code from ZIP
        try {
          const extractedFiles = await extractZipFiles(blob);
          setGeneratedCode(extractedFiles.map(file => ({
            filename: file.filename,
            language: file.language,
            content: file.content,
          })));
        } catch (extractError) {
          console.error('Error extracting ZIP:', extractError);
          setGeneratedCode([{
            filename: 'project.zip',
            language: 'text',
            content: 'Backend code generated successfully! Download the ZIP file to view all files.',
          }]);
        }
      } else {
        // Placeholder for other modules
        throw new Error(`${selectedModule} is not yet implemented`);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I've successfully generated your ${selectedModule.replace(/-/g, ' ')} code! ${(downloadUrl || projectId) ? 'You can download the complete project as a ZIP file.' : 'Check the code preview panel on the right.'}`,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsGenerating(false);

      toast({
        title: "Code generated successfully!",
        description: "Your project files are ready.",
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ Error: ${errorMessage}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
      setIsGenerating(false);

      toast({
        title: "Generation failed",
        description: errorMessage,
        variant: "destructive",
      });
    }
  }, [selectedModule, toast]);

  const handleDownloadZip = useCallback(async () => {
    if (downloadUrl || projectId) {
      try {
        if (projectId) {
          // Backend download endpoint
          const response = await api.downloadProject(projectId);
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = 'codecraft-project.zip';
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        } else if (downloadUrl) {
          // Direct blob URL
          const link = document.createElement('a');
          link.href = downloadUrl;
          link.download = 'codecraft-project.zip';
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }
        toast({
          title: "Download started",
          description: "Your project ZIP file is downloading...",
        });
      } catch (error) {
        toast({
          title: "Download failed",
          description: error instanceof Error ? error.message : 'Failed to download',
          variant: "destructive",
        });
      }
    } else {
      toast({
        title: "No file to download",
        description: "Please generate code first",
        variant: "destructive",
      });
    }
  }, [downloadUrl, projectId, toast]);

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <Header 
        onOpenSettings={() => setIsSettingsOpen(true)} 
        userName={profile.name}
      />

      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* Chat Panel */}
        <div className="flex-1 min-w-0 lg:max-w-[50%] flex flex-col overflow-hidden">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isGenerating={isGenerating}
            selectedModule={selectedModule}
            onSelectModule={setSelectedModule}
          />
        </div>

        {/* Code Preview Panel */}
        <div className={`hidden lg:flex ${isCodeCollapsed ? 'w-12' : 'w-1/2'} transition-all duration-300 overflow-hidden`}>
          <CodePreview
            generatedCode={generatedCode}
            onDownloadZip={handleDownloadZip}
            isCollapsed={isCodeCollapsed}
            onToggleCollapse={() => setIsCodeCollapsed(!isCodeCollapsed)}
          />
        </div>
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        profile={profile}
        onUpdateProfile={(newProfile) => {
          setProfile(newProfile);
          localStorage.setItem('codecraft-profile', JSON.stringify(newProfile));
        }}
      />
    </div>
  );
}
