// api.wrapper.ts - Wrapper that selects the correct API based on port
// If running on port 9090, use Gemini API, otherwise use Ollama API

const useGeminiAPI = () => {
  // Check if we're running on port 9090 (Gemini version)
  if (typeof window !== 'undefined') {
    const port = window.location.port;
    return port === '9090' || import.meta.env.VITE_USE_GEMINI === 'true';
  }
  return import.meta.env.VITE_USE_GEMINI === 'true';
};

// Dynamically import the correct API
const getAPI = () => {
  if (useGeminiAPI()) {
    return import('./api.gemini');
  } else {
    return import('./api');
  }
};

// Export a promise that resolves to the correct API
export const apiPromise = getAPI();

// For synchronous access (will use default API initially, then switch if needed)
// This is a workaround - in practice, components should await apiPromise
let _api: any = null;

apiPromise.then((module) => {
  _api = module.api;
});

export const api = new Proxy({} as any, {
  get(target, prop) {
    if (_api && prop in _api) {
      return _api[prop];
    }
    // Fallback: return a function that will use the promise
    return async (...args: any[]) => {
      const module = await apiPromise;
      const method = (module.api as any)[prop];
      if (typeof method === 'function') {
        return method(...args);
      }
      return method;
    };
  }
});
