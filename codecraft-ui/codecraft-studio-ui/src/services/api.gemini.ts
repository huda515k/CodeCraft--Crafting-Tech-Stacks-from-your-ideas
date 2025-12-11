// api.gemini.ts - API service for Gemini backend (port 9090)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:9090';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

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

    // Use Gemini streaming endpoint
    const response = await fetch(`${API_BASE_URL}/gemini/frontend-to-backend-stream`, {
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

    // Use Gemini streaming endpoint
    const response = await fetch(`${API_BASE_URL}/gemini/prompt-to-backend-stream`, {
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

    // Use Gemini streaming endpoint
    const response = await fetch(`${API_BASE_URL}/gemini/prompt-to-frontend-stream`, {
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

    // Use Gemini streaming endpoint
    const response = await fetch(`${API_BASE_URL}/gemini/backend-to-frontend-stream`, {
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
    // ERD to Backend not available in Gemini version - return error
    throw new ApiError(501, 'ERD to Backend is not available in Gemini version. Use the Ollama version on port 8080.');
  },

  async generateUIToFrontend(
    files: File[],
    additionalContext?: string,
    framework: string = 'react',
    stylingApproach: string = 'tailwind',
    includeTypeScript: boolean = true
  ) {
    // Use Gemini endpoint for UI to Frontend
    if (files.length === 1) {
      return this.generateSingleUIToFrontend(
        files[0],
        additionalContext,
        framework,
        stylingApproach,
        includeTypeScript
      );
    }

    // Multi-file UI to Frontend
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    if (additionalContext) {
      formData.append('additional_context', additionalContext);
    }
    formData.append('include_typescript', includeTypeScript.toString());
    formData.append('styling_approach', stylingApproach);

    const response = await fetch(`${API_BASE_URL}/gemini/ui-to-frontend-multi-stream`, {
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
    stylingApproach: string = 'tailwind',
    includeTypeScript: boolean = true
  ) {
    // Use Gemini streaming endpoint
    const formData = new FormData();
    formData.append('file', file);
    if (additionalContext) {
      formData.append('additional_context', additionalContext);
    }
    formData.append('styling_approach', stylingApproach);
    formData.append('include_typescript', includeTypeScript.toString());

    const response = await fetch(`${API_BASE_URL}/gemini/ui-to-frontend-stream`, {
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
    // Use Gemini download endpoint
    const downloadUrl = `${API_BASE_URL}/gemini/download/${projectId}`;
    
    const response = await fetch(downloadUrl, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new ApiError(response.status, 'Failed to download project');
    }

    return response;
  },
};
