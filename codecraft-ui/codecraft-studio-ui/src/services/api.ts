const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export const api = {
  async generateFrontendToBackend(file: File, archType: string = 'Monolith') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('arch_type', archType);

    // Use streaming endpoint for real-time code preview (now using llmbackend)
    const response = await fetch(`${API_BASE_URL}/nodegen/frontend-to-backend-stream`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(response.status, errorText || 'Failed to generate backend');
    }

    return response;
  },

  async generatePromptToBackend(prompt: string, archType: string = 'Monolith') {
    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('arch_type', archType);

    // Use streaming endpoint (now using llmbackend)
    const response = await fetch(`${API_BASE_URL}/nodegen/prompt-to-backend-stream`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(response.status, errorText || 'Failed to generate backend');
    }

    return response;
  },

  async generatePromptToFrontend(prompt: string) {
    const formData = new FormData();
    formData.append('prompt', prompt);

    // Use streaming endpoint (using llmbackend)
    const response = await fetch(`${API_BASE_URL}/nodegen/prompt-to-frontend-stream`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(response.status, errorText || 'Failed to generate frontend');
    }

    return response;
  },

  async generateBackendToFrontend(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    // Use streaming endpoint (using llmbackend)
    const response = await fetch(`${API_BASE_URL}/nodegen/backend-to-frontend-stream`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(response.status, errorText || 'Failed to generate frontend from backend');
    }

    return response;
  },

  async generateERDToBackend(file: File, additionalContext?: string) {
    const formData = new FormData();
    formData.append('file', file);
    if (additionalContext) {
      formData.append('additional_context', additionalContext);
    }

    // Use streaming endpoint for real-time code preview
    const response = await fetch(`${API_BASE_URL}/agent/upload-erd-stream`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(response.status, errorText || 'Failed to generate backend from ERD');
    }

    return response;
  },

  async generateUIToFrontend(
    files: File[],
    additionalContext?: string,
    framework: string = 'react',
    stylingApproach: string = 'css-modules',
    includeTypeScript: boolean = true
  ) {
    // Use AI agent endpoint for single file, Claude agent for multiple files
    if (files.length === 1) {
      return this.generateSingleUIToFrontend(
        files[0],
        additionalContext,
        framework,
        stylingApproach,
        includeTypeScript
      );
    }

    // Use Ollama-based endpoint for multiple UI images
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    if (additionalContext) {
      formData.append('additional_context', additionalContext);
    }
    formData.append('include_typescript', includeTypeScript.toString());
    formData.append('styling_approach', stylingApproach);

    const response = await fetch(`${API_BASE_URL}/frontend/ollama/generate-react-multi-stream`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(response.status, errorText || 'Failed to generate frontend from UI');
    }

    return response;
  },

  async generateSingleUIToFrontend(
    file: File,
    additionalContext?: string,
    framework: string = 'react',
    stylingApproach: string = 'css-modules',
    includeTypeScript: boolean = true
  ) {
    // Use Ollama-based streaming endpoint for real-time code preview
    const formData = new FormData();
    formData.append('file', file);
    if (additionalContext) {
      formData.append('additional_context', additionalContext);
    }
    formData.append('styling_approach', stylingApproach);
    formData.append('include_typescript', includeTypeScript.toString());

    const response = await fetch(`${API_BASE_URL}/frontend/ollama/generate-react-stream`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(response.status, errorText || 'Failed to generate frontend from UI');
    }

    return response;
  },

  async downloadProject(projectId: string, moduleType?: string) {
    // Determine the correct download endpoint based on module type
    let downloadUrl = `${API_BASE_URL}/nodegen/download/${projectId}`;
    
    if (moduleType === 'erd-to-backend') {
      downloadUrl = `${API_BASE_URL}/agent/download/${projectId}`;
    } else if (moduleType === 'ui-to-frontend') {
      downloadUrl = `${API_BASE_URL}/frontend/download/${projectId}`;
    }
    
    const response = await fetch(downloadUrl, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new ApiError(response.status, 'Failed to download project');
    }

    return response;
  },
};

