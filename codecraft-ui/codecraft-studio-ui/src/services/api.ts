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

    // Use streaming endpoint for real-time code preview
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

  async generateERDToBackend(file: File, additionalContext?: string) {
    const formData = new FormData();
    formData.append('file', file);
    if (additionalContext) {
      formData.append('additional_context', additionalContext);
    }

    const response = await fetch(`${API_BASE_URL}/agent/upload-erd`, {
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
    // Use single screen endpoint for one file, multi-screen for multiple
    if (files.length === 1) {
      return this.generateSingleUIToFrontend(
        files[0],
        additionalContext,
        framework,
        stylingApproach,
        includeTypeScript
      );
    }

    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    if (additionalContext) {
      formData.append('additional_context', additionalContext);
    }
    formData.append('framework', framework);
    formData.append('styling_approach', stylingApproach);
    formData.append('include_typescript', includeTypeScript.toString());

    const response = await fetch(`${API_BASE_URL}/frontend/generate-multi-screen`, {
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
    const formData = new FormData();
    formData.append('file', file);
    if (additionalContext) {
      formData.append('additional_context', additionalContext);
    }
    formData.append('framework', framework);
    formData.append('styling_approach', stylingApproach);
    formData.append('include_typescript', includeTypeScript.toString());

    const response = await fetch(`${API_BASE_URL}/frontend/generate-react`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(response.status, errorText || 'Failed to generate frontend from UI');
    }

    return response;
  },

  async downloadProject(projectId: string) {
    const response = await fetch(`${API_BASE_URL}/nodegen/download/${projectId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new ApiError(response.status, 'Failed to download project');
    }

    return response;
  },
};

