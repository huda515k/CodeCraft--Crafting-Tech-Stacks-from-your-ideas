import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { FileUpload } from './FileUpload';
import { ModuleSelector } from './ModuleSelector';
import { Message, ModuleType, UploadedFile } from '@/types/codecraft';
import { modules } from '@/data/modules';
import { cn } from '@/lib/utils';

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (content: string, files?: UploadedFile[]) => void;
  isGenerating: boolean;
  selectedModule: ModuleType | null;
  onSelectModule: (module: ModuleType) => void;
}

export function ChatInterface({
  messages,
  onSendMessage,
  isGenerating,
  selectedModule,
  onSelectModule,
}: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const currentModule = modules.find(m => m.id === selectedModule);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() && files.length === 0) return;
    if (!selectedModule) return;

    onSendMessage(input.trim(), files.length > 0 ? files : undefined);
    setInput('');
    setFiles([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Module Selector */}
      <div className="flex-shrink-0">
        <ModuleSelector 
          selectedModule={selectedModule} 
          onSelectModule={onSelectModule} 
        />
      </div>

      {/* Messages - This is the scrollable area */}
      <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-4 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-[hsl(199_89%_48%)] flex items-center justify-center mb-4 animate-pulse-glow">
              <Sparkles className="w-8 h-8 text-primary-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Welcome to CodeCraft</h3>
            <p className="text-muted-foreground max-w-md">
              Select a module above and describe what you want to build. 
              {currentModule?.acceptsFiles && " You can also upload files to help me understand your requirements."}
            </p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={message.id}
              className={cn(
                "flex animate-fade-in",
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div
                className={cn(
                  "chat-bubble",
                  message.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'
                )}
              >
                {message.files && message.files.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-2">
                    {message.files.map(file => (
                      <div key={file.id} className="flex items-center gap-1.5 text-xs opacity-80">
                        📎 {file.name}
                      </div>
                    ))}
                  </div>
                )}
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))
        )}

        {isGenerating && (
          <div className="flex justify-start animate-fade-in">
            <div className="chat-bubble chat-bubble-assistant">
              <div className="flex items-center gap-1">
                <span className="typing-dot w-2 h-2 rounded-full bg-current" />
                <span className="typing-dot w-2 h-2 rounded-full bg-current" />
                <span className="typing-dot w-2 h-2 rounded-full bg-current" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0 border-t border-border p-4 bg-card/50">
        {currentModule?.acceptsFiles && (
          <div className="mb-3">
            <FileUpload
              files={files}
              onFilesChange={setFiles}
              acceptedTypes={currentModule.fileTypes}
            />
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-2">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              selectedModule 
                ? `Describe what you want to build with ${currentModule?.name}...`
                : "Select a module to get started..."
            }
            disabled={!selectedModule || isGenerating}
            className="min-h-[52px] max-h-32 resize-none bg-secondary/50 border-0 focus-visible:ring-1"
            rows={1}
          />
          <Button
            type="submit"
            variant="gradient"
            size="icon"
            disabled={!selectedModule || isGenerating || (!input.trim() && files.length === 0)}
            className="h-[52px] w-[52px] flex-shrink-0"
          >
            {isGenerating ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}
