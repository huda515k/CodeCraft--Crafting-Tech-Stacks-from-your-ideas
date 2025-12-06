import { useState, useEffect } from 'react';
import { Download, Copy, Check, FileCode, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GeneratedCode } from '@/types/codecraft';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useTheme } from '@/contexts/ThemeContext';

interface CodePreviewProps {
  generatedCode: GeneratedCode[];
  onDownloadZip: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export function CodePreview({ 
  generatedCode, 
  onDownloadZip,
  isCollapsed,
  onToggleCollapse 
}: CodePreviewProps) {
  const [activeFile, setActiveFile] = useState(0);
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();
  const { theme } = useTheme();
  
  // Update active file when generatedCode changes
  useEffect(() => {
    if (generatedCode.length > 0 && activeFile >= generatedCode.length) {
      setActiveFile(0);
    }
  }, [generatedCode.length, activeFile]);

  const handleCopy = async () => {
    if (generatedCode.length === 0) return;
    
    await navigator.clipboard.writeText(generatedCode[activeFile].content);
    setCopied(true);
    toast({
      title: "Copied!",
      description: "Code copied to clipboard",
    });
    setTimeout(() => setCopied(false), 2000);
  };

  const getLanguageColor = (lang: string) => {
    const colors: Record<string, string> = {
      javascript: 'bg-yellow-500',
      typescript: 'bg-blue-500',
      jsx: 'bg-cyan-500',
      tsx: 'bg-blue-400',
      json: 'bg-green-500',
      css: 'bg-pink-500',
      html: 'bg-orange-500',
    };
    return colors[lang] || 'bg-gray-500';
  };

  if (isCollapsed) {
    return (
      <div className="w-12 border-l border-border bg-card/50 flex flex-col items-center py-4">
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={onToggleCollapse}
          className="mb-4"
        >
          <ChevronLeft className="w-4 h-4" />
        </Button>
        <div className="flex-1 flex flex-col items-center gap-2">
          {generatedCode.map((file, index) => (
            <button
              key={index}
              onClick={() => { setActiveFile(index); onToggleCollapse(); }}
              className={cn(
                "w-8 h-8 rounded-lg flex items-center justify-center transition-colors",
                index === activeFile ? "bg-primary/20 text-primary" : "hover:bg-secondary"
              )}
              title={file.filename}
            >
              <FileCode className="w-4 h-4" />
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full border-l border-border bg-card/30 overflow-hidden">
      {/* Header */}
      <div className="h-14 flex-shrink-0 border-b border-border px-4 flex items-center justify-between bg-card/50">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onToggleCollapse}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
          <h3 className="font-medium">Code Preview</h3>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            disabled={generatedCode.length === 0}
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          </Button>
          <Button
            variant="gradient"
            size="sm"
            onClick={onDownloadZip}
            disabled={generatedCode.length === 0}
            className="gap-2"
          >
            <Download className="w-4 h-4" />
            Download ZIP
          </Button>
        </div>
      </div>

      {/* File Tabs */}
      {generatedCode.length > 0 && (
        <div className="flex-shrink-0 flex overflow-x-auto border-b border-border bg-secondary/30 scrollbar-thin">
          {generatedCode.map((file, index) => (
            <button
              key={index}
              onClick={() => setActiveFile(index)}
              className={cn(
                "flex items-center gap-2 px-4 py-2 text-sm border-b-2 transition-colors whitespace-nowrap",
                index === activeFile
                  ? "border-primary text-foreground bg-card/50"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              )}
            >
              <span className={cn("w-2 h-2 rounded-full", getLanguageColor(file.language))} />
              {file.filename}
            </button>
          ))}
        </div>
      )}

      {/* Code Content - This is the scrollable area */}
      <div className="flex-1 min-h-0 overflow-auto scrollbar-thin">
        {generatedCode.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4">
            <div className="w-16 h-16 rounded-2xl bg-secondary/50 flex items-center justify-center mb-4">
              <FileCode className="w-8 h-8 text-muted-foreground" />
            </div>
            <h4 className="font-medium mb-1">No code generated yet</h4>
            <p className="text-sm text-muted-foreground max-w-xs">
              Select a module and enter your prompt to generate code
            </p>
          </div>
        ) : (
          <div className="animate-fade-in">
            <SyntaxHighlighter
              language={generatedCode[activeFile].language}
              style={theme === 'dark' ? vscDarkPlus : oneLight}
              customStyle={{
                margin: 0,
                padding: '1rem',
                background: 'transparent',
                fontSize: '0.875rem',
                lineHeight: '1.6',
              }}
              showLineNumbers
              wrapLines
              wrapLongLines
            >
              {generatedCode[activeFile].content}
            </SyntaxHighlighter>
          </div>
        )}
      </div>
    </div>
  );
}
