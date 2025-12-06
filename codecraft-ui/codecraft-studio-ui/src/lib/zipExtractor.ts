import JSZip from 'jszip';

export interface ExtractedFile {
  filename: string;
  content: string;
  language: string;
}

const getLanguageFromFilename = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase() || '';
  const langMap: Record<string, string> = {
    'js': 'javascript',
    'jsx': 'jsx',
    'ts': 'typescript',
    'tsx': 'tsx',
    'json': 'json',
    'py': 'python',
    'java': 'java',
    'cpp': 'cpp',
    'c': 'c',
    'cs': 'csharp',
    'php': 'php',
    'rb': 'ruby',
    'go': 'go',
    'rs': 'rust',
    'swift': 'swift',
    'kt': 'kotlin',
    'html': 'html',
    'css': 'css',
    'scss': 'scss',
    'sass': 'sass',
    'less': 'less',
    'md': 'markdown',
    'yml': 'yaml',
    'yaml': 'yaml',
    'xml': 'xml',
    'sql': 'sql',
    'sh': 'bash',
    'bash': 'bash',
    'zsh': 'bash',
    'dockerfile': 'dockerfile',
    'env': 'text',
    'txt': 'text',
    'gitignore': 'text',
    'eslintrc': 'json',
    'prettierrc': 'json',
  };
  return langMap[ext] || 'text';
};

const shouldIncludeFile = (filename: string): boolean => {
  // Exclude binary files and common non-code files
  const excludePatterns = [
    /\.(png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot|otf)$/i,
    /\.(zip|tar|gz|rar|7z)$/i,
    /node_modules/,
    /\.git/,
    /\.DS_Store/,
    /\.log$/,
    /package-lock\.json$/,
    /yarn\.lock$/,
    /pnpm-lock\.yaml$/,
  ];
  
  return !excludePatterns.some(pattern => pattern.test(filename));
};

export const extractZipFiles = async (blob: Blob): Promise<ExtractedFile[]> => {
  try {
    const zip = await JSZip.loadAsync(blob);
    const files: ExtractedFile[] = [];
    
    // Process all files in the ZIP
    const filePromises: Promise<void>[] = [];
    
    zip.forEach((relativePath, file) => {
      if (file.dir) return; // Skip directories
      if (!shouldIncludeFile(relativePath)) return;
      
      const promise = file.async('string').then(content => {
        const language = getLanguageFromFilename(relativePath);
        files.push({
          filename: relativePath,
          content,
          language,
        });
      }).catch(err => {
        // If file can't be read as string (binary), skip it
        console.warn(`Skipping binary file: ${relativePath}`, err);
      });
      
      filePromises.push(promise);
    });
    
    await Promise.all(filePromises);
    
    // Sort files: put important files first, then alphabetically
    files.sort((a, b) => {
      const aPriority = getFilePriority(a.filename);
      const bPriority = getFilePriority(b.filename);
      if (aPriority !== bPriority) return bPriority - aPriority;
      return a.filename.localeCompare(b.filename);
    });
    
    return files;
  } catch (error) {
    console.error('Error extracting ZIP file:', error);
    throw new Error('Failed to extract ZIP file contents');
  }
};

const getFilePriority = (filename: string): number => {
  // Higher priority = shown first
  if (filename.includes('package.json') || filename.includes('package-lock.json')) return 10;
  if (filename.includes('README')) return 9;
  if (filename.includes('server') || filename.includes('index') || filename.includes('app')) return 8;
  if (filename.includes('main') || filename.includes('entry')) return 7;
  if (filename.endsWith('.js') || filename.endsWith('.ts') || filename.endsWith('.jsx') || filename.endsWith('.tsx')) return 6;
  if (filename.endsWith('.json')) return 5;
  if (filename.endsWith('.md')) return 4;
  return 1;
};

