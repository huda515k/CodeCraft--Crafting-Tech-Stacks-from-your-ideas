// api.index.ts - Exports the correct API based on environment
// This file should be imported as '@/services/api' to get the right API

// Check if we should use Gemini API
const useGemini = import.meta.env.VITE_USE_GEMINI === 'true' || 
                  (typeof window !== 'undefined' && window.location.port === '9090');

// Export the appropriate API
if (useGemini) {
  export { api, ApiError } from './api.gemini';
} else {
  export { api, ApiError } from './api';
}
